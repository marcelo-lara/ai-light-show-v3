import os
import json
import hashlib

from .diagnostics_compute import FrameDiagnosticsComputer, DiagnosticsSummary, AssetGenerator


def generate_frames(renderer, output_format: str = "legacy", progress_callback=None):
    # This function is a direct extraction of FrameRenderer.generate_frames
    # to reduce file size in renderer.py. It operates on the passed `renderer` instance.
    duration = renderer.analysis_data['duration']
    total_frames = int(duration * renderer.fps)

    import random, time
    import numpy as np
    import numpy as cpu_np

    np.random.seed(renderer.seed)
    random.seed(renderer.seed)

    frames = [] if output_format == "legacy" else bytearray()
    frame_data = []
    diagnostics = renderer.Diagnostics(renderer.coords.shape[0]) if hasattr(renderer, 'Diagnostics') else None
    renderer.modulator_trace = []
    start_time = time.time()
    if progress_callback:
        try:
            progress_callback('render', 0, total_frames)
        except Exception:
            pass

    active_scene = None
    preset = None
    active_layers = []
    active_modulators = []
    prev_scene = None
    prev_preset = None
    prev_layers = []
    prev_modulators = []

    for frame_idx in range(total_frames):
        time_sec = frame_idx / renderer.fps
        current_scene = renderer.timeline.scenes[0]
        for scene in renderer.timeline.scenes:
            if scene.start <= time_sec <= scene.end:
                current_scene = scene
                break
        if current_scene != active_scene:
            prev_scene = active_scene
            prev_preset = preset
            prev_layers = active_layers
            prev_modulators = active_modulators
            active_scene = current_scene
            preset, active_layers, active_modulators = renderer._setup_scene(active_scene)

        audio_features = renderer.analyzer.get_features_at_time(time_sec, renderer.analysis_data)

        def _palette_or_default(p):
            pal = getattr(p, 'palette', None)
            if pal is None:
                return type('P', (), { 'primary': '#000000', 'secondary': '#000000', 'accent': '#000000', 'background': '#000000' })()
            return pal

        context = renderer.FrameContext(
            coords=renderer.coords,
            features=audio_features,
            q_buffer=renderer.q_buffer,
            width=renderer.width,
            height=renderer.height,
            palette=_palette_or_default(preset)
        )

        def render_scene_state(scene, p_preset, p_layers, p_mods):
            mod_values = {}
            for mod_config, mod_inst in p_mods:
                mod_values[mod_config.id] = float(mod_inst.evaluate(time_sec, audio_features, mod_config.params))

            ctx = renderer.FrameContext(
                coords=renderer.coords,
                features=audio_features,
                q_buffer=renderer.q_buffer,
                width=renderer.width,
                height=renderer.height,
                palette=_palette_or_default(p_preset)
            )

            pixels = np.zeros((renderer.coords.shape[0], 3), dtype=np.uint8)
            for config, layer in p_layers:
                evaluated_params = {k: renderer.evaluate_param(v, scene.params, p_preset, mod_values) for k, v in config.params.items()}
                layer_pixels = layer.render(ctx, **evaluated_params)
                if scene.intensity != 1.0:
                    layer_pixels = (layer_pixels * scene.intensity).astype(np.uint8)
                if config.blend_mode == "max":
                    pixels = renderer.Compositor.blend_max(pixels, layer_pixels)
                elif config.blend_mode == "add":
                    pixels = renderer.Compositor.blend_add(pixels, layer_pixels)
                else:
                    pixels = layer_pixels
            return pixels, mod_values

        final_pixels, cur_mod_values = render_scene_state(active_scene, preset, active_layers, active_modulators)
        renderer.modulator_trace.append({"timestamp": float(time_sec), "mod_values": {k: float(v) for k, v in cur_mod_values.items()}})

        if active_scene.transition and prev_scene is not None:
            trans = active_scene.transition
            if time_sec < active_scene.start + trans.duration:
                progress = (time_sec - active_scene.start) / trans.duration
                progress = max(0.0, min(1.0, progress))
                if trans.type == "hard_cut":
                    pass
                elif trans.type == "crossfade":
                    prev_pixels, prev_mod_values = render_scene_state(prev_scene, prev_preset, prev_layers, prev_modulators)
                    final_pixels = (prev_pixels * (1.0 - progress) + final_pixels * progress).astype(np.uint8)
                elif trans.type == "beat_flash":
                    flash_val = (1.0 - progress) * 255.0 * audio_features.get('global_energy', 1.0)
                    final_pixels = np.clip(final_pixels + flash_val, 0, 255).astype(np.uint8)

        host_pixels = renderer._to_host_array(final_pixels).astype(renderer.cpu_np.uint8, copy=False)
        if diagnostics:
            diagnostics.update(host_pixels)

        if output_format == "legacy":
            r = host_pixels[:, 0].astype(renderer.cpu_np.uint32)
            g = host_pixels[:, 1].astype(renderer.cpu_np.uint32)
            b = host_pixels[:, 2].astype(renderer.cpu_np.uint32)
            packed_pixels = (r << 16) | (g << 8) | b
            frames.append({
                "timestamp": time_sec,
                "pixels": packed_pixels.tolist()
            })
        else:
            frames.extend(host_pixels.reshape(-1).tobytes())

        frame_data.append({
            "index": frame_idx,
            "timestamp": time_sec,
            "pixels": host_pixels.copy(),
        })

        if frame_idx % 200 == 0 and frame_idx > 0:
            if progress_callback:
                try:
                    progress_callback('render', frame_idx, total_frames)
                except Exception:
                    pass

    end_time = time.time()
    render_duration_sec = end_time - start_time

    frame_diagnostics_computer = FrameDiagnosticsComputer()
    summary_computer = DiagnosticsSummary()

    prev_pixels = None
    for frame_data_item in frame_data:
        frame_diag = frame_diagnostics_computer.compute_frame_diagnostics(
            frame_num=frame_data_item["index"],
            timestamp=frame_data_item["timestamp"],
            pixels=frame_data_item["pixels"],
            prev_pixels=prev_pixels,
        )
        summary_computer.add_frame(frame_diag)
        prev_pixels = frame_data_item["pixels"]

    diagnostics_summary = summary_computer.compute_summary(
        render_duration_ms=render_duration_sec * 1000,
        fps=renderer.fps,
    )

    contact_sheet_path = None
    preview_strip_path = None
    asset_metadata = {}

    try:
        contact_sheet_name = f"{renderer.song_id}.{hashlib.sha256((renderer.song_id + str(renderer.seed)).encode()).hexdigest()[:8]}.contact.png"
        contact_sheet_path = os.path.join(renderer.output_dir, contact_sheet_name)
        frame_pixel_arrays = [fd["pixels"] for fd in frame_data]
        contact_sheet_meta = AssetGenerator.generate_contact_sheet(
            frames=frame_pixel_arrays,
            output_path=contact_sheet_path,
            cols=4,
            rows=3,
            frame_width=50,
            frame_height=25,
        )
        asset_metadata["contact_sheet"] = {
            "filename": contact_sheet_name,
            "path": contact_sheet_path,
            "metadata": contact_sheet_meta,
        }

        preview_strip_name = f"{renderer.song_id}.{hashlib.sha256((renderer.song_id + str(renderer.seed)).encode()).hexdigest()[:8]}.preview.png"
        preview_strip_path = os.path.join(renderer.output_dir, preview_strip_name)
        preview_meta = AssetGenerator.generate_preview_strip(
            frames=frame_pixel_arrays,
            output_path=preview_strip_path,
            strip_height=50,
            max_width=2000,
        )
        asset_metadata["preview_strip"] = {
            "filename": preview_strip_name,
            "path": preview_strip_path,
            "metadata": preview_meta,
        }
    except Exception as e:
        print(f"Warning: Failed to generate preview assets: {e}")

    renderer.render_diagnostics = {
        "summary": diagnostics_summary,
        "frame_diagnostics": [d for d in summary_computer.frame_diagnostics],
        "assets": asset_metadata,
    }
    if progress_callback:
        try:
            progress_callback('render', total_frames, total_frames)
        except Exception:
            pass
    return frames


def export(renderer, progress_callback=None, canvas_name: str = "default"):
    sanitized_canvas_name = "".join(c for c in canvas_name if c.isalnum() or c in "_-").strip()
    if not sanitized_canvas_name:
        sanitized_canvas_name = "default"
    hash_input = f"{renderer.song_id}_{renderer.seed}_{json.dumps(renderer.global_params, sort_keys=True)}_{renderer.fps}_timeline"
    render_id = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    base_name = f"{renderer.song_id}.{sanitized_canvas_name}.{render_id}"
    output_path = os.path.join(renderer.output_dir, f"{base_name}.json")

    frame_bytes = generate_frames(renderer, output_format="rgb24", progress_callback=progress_callback)

    bytes_per_frame = renderer.width * renderer.height * 3
    chunk_frames = 200
    chunk_size = bytes_per_frame * chunk_frames

    chunk_files = []
    idx = 0
    for start in range(0, len(frame_bytes), chunk_size):
        chunk_name = f"{base_name}.bin.{idx:04d}"
        chunk_path = os.path.join(renderer.output_dir, chunk_name)
        with open(chunk_path, 'wb') as cf:
            cf.write(frame_bytes[start:start+chunk_size])
        chunk_files.append(os.path.basename(chunk_path))
        idx += 1

    metadata = {
        "schema_version": "v2",
        "render_id": render_id,
        "preset_id": renderer.preset_id,
        "preset_version": renderer.preset_version,
        "seed": renderer.seed,
        "params": renderer.global_params,
        "song_id": renderer.song_id,
        "analysis_id": "v1",
        "analysis_diagnostics": renderer.analysis_data.get('diagnostics', {}),
        "analysis_structure": renderer.analysis_data.get('structure', {}),
        "fps": renderer.fps,
        "duration": renderer.analysis_data['duration'],
        "frame_count": int(renderer.analysis_data['duration'] * renderer.fps),
        "resolution": {"width": renderer.width, "height": renderer.height},
        "frame_encoding": "rgb24",
        "frame_chunks": chunk_files,
        "chunk_frames": chunk_frames,
        "bytes_per_frame": bytes_per_frame,
        "timeline": renderer.timeline.dict(),
        "render_diagnostics": getattr(renderer, 'render_diagnostics', {}),
        "modulator_trace": getattr(renderer, 'modulator_trace', [])
    }

    with open(output_path, 'w') as f:
        json.dump({"metadata": metadata}, f)

    print("Export complete! (wrote {} chunks)".format(len(chunk_files)))
    return output_path
