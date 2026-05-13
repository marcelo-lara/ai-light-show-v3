from types import SimpleNamespace
from .layers import get_layer
from .modulators import get_modulator


def setup_scene(renderer, scene):
    preset = renderer.presets[scene.preset_id]

    def _to_obj(x):
        if isinstance(x, dict):
            return SimpleNamespace(**x)
        return x

    active_layers = []
    for layer_config in preset.layers:
        cfg = _to_obj(layer_config)
        layer_inst = get_layer(cfg.layer_type)
        active_layers.append((cfg, layer_inst))

    active_modulators = []
    for mod_config in preset.modulators:
        mcfg = _to_obj(mod_config)
        mod_inst = get_modulator(mcfg.type)
        active_modulators.append((mcfg, mod_inst))

    return preset, active_layers, active_modulators


def evaluate_param(renderer, param_val, scene_params, preset, mod_values=None):
    from .mod_mapping import apply_mapping

    if isinstance(param_val, dict):
        if 'mod' in param_val:
            mod_id = param_val['mod']
            base = None
            if mod_values and mod_id in mod_values:
                base = float(mod_values[mod_id])
            else:
                base = float(param_val.get('value', 0.0))
            if 'mapping' in param_val:
                return apply_mapping(base, param_val['mapping'])
            return base
        if 'param' in param_val:
            return evaluate_param(renderer, f"param.{param_val['param']}", scene_params, preset, mod_values)
        if 'value' in param_val:
            return param_val['value']

    if mod_values and isinstance(param_val, str) and param_val.startswith("mod."):
        mod_id = param_val.replace("mod.", "")
        if mod_id in mod_values:
            return mod_values[mod_id]

    if isinstance(param_val, str) and param_val.startswith("param."):
        param_name = param_val.replace("param.", "")
        if param_name in scene_params:
            return scene_params[param_name]
        if param_name in renderer.global_params:
            return renderer.global_params[param_name]
        for p in preset.parameters:
            if p.id == param_name:
                return p.default
    return param_val
