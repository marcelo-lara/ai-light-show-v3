import { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Pause, Play, Square, Upload } from 'lucide-react';
import Diagnostics from './Diagnostics';
import { Fixture } from './types/layers';

interface FrameData {
  timestamp: number;
  pixels: number[];
}

export interface PresetParameter {
  id: string;
  label: string;
  type: 'int' | 'float' | 'boolean' | 'color' | 'select';
  default: boolean | number | string;
  min?: number;
  max?: number;
  step?: number;
  options?: string[];
  ui_group: string;
}

export interface ModulatorConfig {
  id: string;
  type: 'lfo' | 'envelope';
  params: Record<string, unknown>;
}

export interface AnalysisFeatures {
  times: number[];
  beat_times: number[];
  global_energy: number[];
  onset_env?: number[];
  freq_data: {
    sub_bass: number[];
    bass: number[];
    low_mid: number[];
    high_mid: number[];
    treble: number[];
  };
}

export interface TransitionSchema {
  type: string;
  duration: number;
  params: Record<string, unknown>;
}

export interface SceneSchema {
  start: number;
  end: number;
  preset_id: string;
  params: Record<string, unknown>;
  seed: number;
  intensity: number;
  transition?: TransitionSchema;
}

export interface TimelineSchema {
  scenes: SceneSchema[];
}

export interface PresetSummary {
  preset_id: string;
  version: string;
  name: string;
  description: string;
  tags: string[];
  parameters: PresetParameter[];
  modulators?: ModulatorConfig[];
}

interface ShowMetadata {
  schema_version: string;
  render_id: string;
  preset_id: string;
  preset_version: string;
  seed: number;
  params: Record<string, unknown>;
  song_id: string;
  analysis_id: string;
  palette?: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
  };
  analysis_features?: AnalysisFeatures;
  analysis_diagnostics?: {
    beat_confidence: number;
    frame_count: number;
    sources: string[];
  };
  analysis_structure?: {
    sections: number;
    phrases_interval: number;
    section_candidates: number[];
  };
  timeline?: TimelineSchema;
  fps: number;
  duration: number;
  frame_count: number;
  resolution: { width: number; height: number };
  frame_encoding?: string;
  frame_data_path?: string;
  bytes_per_frame?: number;
}

interface ShowData {
  metadata: ShowMetadata;
  frames?: FrameData[];
}

interface ServerStatePayload {
  current_song: string | null;
  current_canvas: string | null;
}

const MAIN_TAB = 'Main';

function App() {
  const [songs, setSongs] = useState<string[]>([]);
  const [presets, setPresets] = useState<PresetSummary[]>([]);
  const [selectedSong, setSelectedSong] = useState('');
  const [selectedShow, setSelectedShow] = useState('undersea_pulse_01');
  const [currentCanvas, setCurrentCanvas] = useState<string | null>(null);
  const [activePreset, setActivePreset] = useState<PresetSummary | null>(null);
  const [params, setParams] = useState<Record<string, boolean | number | string>>({});
  const [activeTab, setActiveTab] = useState(MAIN_TAB);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [drift, setDrift] = useState(0);
  const [serverState, setServerState] = useState('CONNECTED');

  const waveformRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wavesurfer = useRef<WaveSurfer | null>(null);
  const legacyFramesData = useRef<FrameData[]>([]);
  const binaryFramesData = useRef<Uint8Array | null>(null);
  const metadataRef = useRef<ShowMetadata | null>(null);
  const imageDataRef = useRef<ImageData | null>(null);
  const animationRef = useRef<number>(0);

  const overlaysRef = useRef({ fixtures: [] as Fixture[], pois: [] as any[] });

  const loadOverlays = async () => {
    try {
      const [fixturesRes, poisRes] = await Promise.all([
        fetch('/data/fixtures/fixtures.json'),
        fetch('/data/fixtures/pois.json'),
      ]);
      if (fixturesRes.ok) {
        const f = await fixturesRes.json();
        overlaysRef.current.fixtures = f;
      }
      if (poisRes.ok) {
        const p = await poisRes.json();
        overlaysRef.current.pois = p;
      }
    } catch (e) {
      console.error('Failed to load overlays', e);
    }
  };

  const parameterGroups = activePreset
    ? [...new Set(activePreset.parameters.map((parameter) => parameter.ui_group))]
    : [];
  const controlTabs = [MAIN_TAB, ...parameterGroups];
  const activeParameters = activePreset
    ? activePreset.parameters.filter((parameter) => parameter.ui_group === activeTab)
    : [];

  const initWavesurfer = (songId = selectedSong) => {
    if (!songId || !waveformRef.current) {
      return;
    }

    if (wavesurfer.current) {
      wavesurfer.current.destroy();
    }

    wavesurfer.current = WaveSurfer.create({
      container: waveformRef.current,
      waveColor: '#333333',
      progressColor: '#9000dd',
      cursorColor: '#ffffff',
      cursorWidth: 1,
      barWidth: 2,
      barGap: 1,
      height: 128,
      normalize: true,
      minPxPerSec: 100,
      url: `/data/songs/${encodeURIComponent(songId)}.mp3`,
    });

    wavesurfer.current.on('ready', () => setIsLoaded(true));
    wavesurfer.current.on('audioprocess', (time) => setCurrentTime(time));
    wavesurfer.current.on('seeking', (time) => setCurrentTime(time));
    wavesurfer.current.on('play', () => setIsPlaying(true));
    wavesurfer.current.on('pause', () => setIsPlaying(false));
  };

  const clearFrames = () => {
    metadataRef.current = null;
    legacyFramesData.current = [];
    binaryFramesData.current = null;
  };

  const fetchServerState = async () => {
    const response = await fetch('/api/current_state');
    return response.json() as Promise<ServerStatePayload>;
  };

  const fetchFrames = async (canvasId: string | null = null, songId = selectedSong) => {
    if (!songId && !canvasId) {
      return;
    }

    const canvasToLoad = canvasId
      ? (canvasId.endsWith('.json') ? canvasId : `${canvasId}.json`)
      : `${songId}.${selectedShow}.json`;

    try {
      const response = await fetch(`/data/canvas/${encodeURIComponent(canvasToLoad)}`);
      if (!response.ok) {
        clearFrames();
        return;
      }

      const data: ShowData = await response.json();
      if (data.metadata.schema_version === 'v1') {
        metadataRef.current = data.metadata;
        legacyFramesData.current = data.frames ?? [];
        binaryFramesData.current = null;
        setCurrentCanvas(canvasToLoad);
        return;
      }

      if (data.metadata.schema_version !== 'v2' || data.metadata.frame_encoding !== 'rgb24' || !data.metadata.frame_data_path) {
        setServerState('INCOMPATIBLE_SCHEMA');
        clearFrames();
        return;
      }

      const binaryResponse = await fetch(`/data/canvas/${encodeURIComponent(data.metadata.frame_data_path)}`);
      if (!binaryResponse.ok) {
        clearFrames();
        return;
      }

      const frameBytes = new Uint8Array(await binaryResponse.arrayBuffer());
      const bytesPerFrame = data.metadata.bytes_per_frame
        ?? data.metadata.resolution.width * data.metadata.resolution.height * 3;
      const expectedBytes = bytesPerFrame * data.metadata.frame_count;
      if (frameBytes.byteLength !== expectedBytes) {
        setServerState('INCOMPATIBLE_SCHEMA');
        clearFrames();
        return;
      }

      metadataRef.current = data.metadata;
      legacyFramesData.current = [];
      binaryFramesData.current = frameBytes;
      setCurrentCanvas(canvasToLoad);
    } catch (error) {
      console.error(error);
      clearFrames();
    }
  };

  const handleLoad = async (songId = selectedSong) => {
    if (!songId) {
      return;
    }

    setSelectedSong(songId);
    setIsLoaded(false);
    setIsPlaying(false);
    setCurrentTime(0);

    try {
      const response = await fetch(`/api/load_song/${encodeURIComponent(songId)}`, {
        method: 'POST',
      });
      const state: ServerStatePayload = await response.json();
      if (!response.ok) {
        throw new Error('Failed to load song');
      }

      const resolvedSong = state.current_song ?? songId;
      setSelectedSong(resolvedSong);
      setCurrentCanvas(state.current_canvas);
      initWavesurfer(resolvedSong);

      if (state.current_canvas) {
        await fetchFrames(state.current_canvas, resolvedSong);
      } else {
        clearFrames();
      }
    } catch (error) {
      console.error(error);
      setServerState('ERROR');
    }
  };

  const handlePlayPause = () => {
    wavesurfer.current?.playPause();
  };

  const handleStop = () => {
    if (!wavesurfer.current) {
      return;
    }

    wavesurfer.current.stop();
    setIsPlaying(false);
    setCurrentTime(0);
  };

  const handleGenerate = async () => {
    if (!selectedSong || !selectedShow || !activePreset) {
      return;
    }

    setServerState('GENERATING...');
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          song_id: selectedSong,
          preset_id: selectedShow,
          preset_version: activePreset.version,
          seed: 42,
          params,
        }),
      });

      const data = await response.json();
      const jobId = data.job;
      if (!jobId) {
        throw new Error('Missing job id');
      }

      const intervalId = setInterval(async () => {
        try {
          const statusResponse = await fetch(`/api/status/${encodeURIComponent(jobId)}`);
          const statusData = await statusResponse.json();

          if (statusData.status === 'COMPLETED') {
            clearInterval(intervalId);
            setServerState('CONNECTED');

            const state = await fetchServerState();
            setCurrentCanvas(state.current_canvas);
            if (state.current_song) {
              setSelectedSong(state.current_song);
            }

            if (state.current_canvas) {
              await fetchFrames(state.current_canvas, state.current_song ?? selectedSong);
            } else {
              clearFrames();
            }
          } else if (statusData.status === 'FAILED') {
            clearInterval(intervalId);
            setServerState('ERROR');
          }
        } catch (error) {
          console.error(error);
          clearInterval(intervalId);
          setServerState('ERROR');
        }
      }, 1000);
    } catch (error) {
      console.error(error);
      setServerState('ERROR');
    }
  };

  const formatTime = (timeInSeconds: number) => {
    const mins = Math.floor(timeInSeconds / 60);
    const secs = Math.floor(timeInSeconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleParamChange = (parameterId: string, value: boolean | number | string) => {
    setParams((currentParams) => ({
      ...currentParams,
      [parameterId]: value,
    }));
  };

  const renderParameterInput = (parameter: PresetParameter) => {
    const currentValue = params[parameter.id] ?? parameter.default;

    if (parameter.type === 'boolean') {
      return (
        <label className="toggle-row">
          <span>{parameter.label}</span>
          <input
            checked={Boolean(currentValue)}
            onChange={(event) => handleParamChange(parameter.id, event.target.checked)}
            type="checkbox"
          />
        </label>
      );
    }

    if (parameter.type === 'select') {
      return (
        <select
          value={String(currentValue)}
          onChange={(event) => handleParamChange(parameter.id, event.target.value)}
        >
          {parameter.options?.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      );
    }

    if (parameter.type === 'color') {
      return (
        <input
          type="color"
          value={String(currentValue)}
          onChange={(event) => handleParamChange(parameter.id, event.target.value)}
        />
      );
    }

    const min = parameter.min ?? 0;
    const max = parameter.max ?? 100;
    const step = parameter.step ?? (parameter.type === 'float' ? 0.1 : 1);

    return (
      <>
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={Number(currentValue)}
          onChange={(event) => handleParamChange(parameter.id, Number(event.target.value))}
        />
        <span className="range-value">{currentValue}</span>
      </>
    );
  };

  useEffect(() => {
    const renderLoop = () => {
      const realTime = wavesurfer.current?.getCurrentTime() || currentTime;
      const metadata = metadataRef.current;
      const hasLegacyFrames = legacyFramesData.current.length > 0;
      const hasBinaryFrames = binaryFramesData.current !== null;

      if (canvasRef.current && metadata && (hasLegacyFrames || hasBinaryFrames)) {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          const fps = metadata.fps || 50;
          const frameIndex = Math.floor(realTime * fps);
          const clampedFrameIndex = Math.min(frameIndex, Math.max(0, metadata.frame_count - 1));
          const width = metadata.resolution.width;
          const height = metadata.resolution.height;
          const pixelCount = width * height;
          const bytesPerFrame = metadata.bytes_per_frame ?? pixelCount * 3;

          if (!imageDataRef.current || imageDataRef.current.width !== width || imageDataRef.current.height !== height) {
            imageDataRef.current = ctx.createImageData(width, height);
          }

          const imageData = imageDataRef.current;
          const { data } = imageData;

          if (hasBinaryFrames && binaryFramesData.current) {
            const frameStart = clampedFrameIndex * bytesPerFrame;
            const frameBytes = binaryFramesData.current.subarray(frameStart, frameStart + bytesPerFrame);
            for (let index = 0; index < pixelCount; index += 1) {
              const sourceIndex = index * 3;
              const pixelIndex = index << 2;
              data[pixelIndex] = frameBytes[sourceIndex];
              data[pixelIndex + 1] = frameBytes[sourceIndex + 1];
              data[pixelIndex + 2] = frameBytes[sourceIndex + 2];
              data[pixelIndex + 3] = 255;
            }
          } else {
            const frame = legacyFramesData.current[Math.min(clampedFrameIndex, legacyFramesData.current.length - 1)];
            if (!frame?.pixels) {
              animationRef.current = requestAnimationFrame(renderLoop);
              return;
            }

            for (let index = 0; index < frame.pixels.length; index += 1) {
              const value = frame.pixels[index];
              const pixelIndex = index << 2;
              data[pixelIndex] = (value >> 16) & 0xff;
              data[pixelIndex + 1] = (value >> 8) & 0xff;
              data[pixelIndex + 2] = value & 0xff;
              data[pixelIndex + 3] = 255;
            }
          }

          const metaW = width;
          const metaH = height;
          const clientW = canvas.clientWidth || metaW;
          const clientH = canvas.clientHeight || metaH;
          const dpr = window.devicePixelRatio || 1;
          const desiredW = Math.max(1, Math.round(clientW * dpr));
          const desiredH = Math.max(1, Math.round(clientH * dpr));
          if (canvas.width !== desiredW || canvas.height !== desiredH) {
            canvas.width = desiredW;
            canvas.height = desiredH;
          }
          const off = document.createElement('canvas');
          off.width = metaW;
          off.height = metaH;
          const offCtx = off.getContext('2d');
          if (offCtx) {
            offCtx.putImageData(imageData, 0, 0);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(off, 0, 0, canvas.width, canvas.height);
          }
          // draw overlays
          const scaleX = canvas.width / metaW;
          const scaleY = canvas.height / metaH;
          const drawMarker = (x: number, y: number, kind: 'fixture' | 'poi') => {
            const px = x * metaW * scaleX;
            const py = y * metaH * scaleY;
            const radius = Math.max(3, Math.round(6 * (canvas.width / metaW)));
            ctx.beginPath();
            if (kind === 'fixture') {
              ctx.fillStyle = 'rgba(0,128,255,0.9)';
              ctx.strokeStyle = '#003366';
              ctx.lineWidth = 2;
              ctx.arc(px, py, radius, 0, Math.PI * 2);
              ctx.fill();
              ctx.stroke();
            } else {
              ctx.fillStyle = 'rgba(255,64,64,0.95)';
              ctx.strokeStyle = '#660000';
              ctx.lineWidth = 2;
              ctx.fillRect(px - radius, py - radius, radius * 2, radius * 2);
              ctx.strokeRect(px - radius, py - radius, radius * 2, radius * 2);
            }
          };
          // overlaysRef holds originals; entries may already be normalized [0-1] or pixel coords; assume normalized if <=1
          overlaysRef.current.fixtures?.forEach((f: any) => {
            const nx = f.x !== undefined ? f.x : f[0];
            const ny = f.y !== undefined ? f.y : f[1];
            const xNorm = nx <= 1 ? nx : nx / metaW;
            const yNorm = ny <= 1 ? ny : ny / metaH;
            drawMarker(xNorm, yNorm, 'fixture');
          });
          overlaysRef.current.pois?.forEach((p: any) => {
            const nx = p.x !== undefined ? p.x : p[0];
            const ny = p.y !== undefined ? p.y : p[1];
            const xNorm = nx <= 1 ? nx : nx / metaW;
            const yNorm = ny <= 1 ? ny : ny / metaH;
            drawMarker(xNorm, yNorm, 'poi');
          });

          const frameTimestamp = hasBinaryFrames
            ? clampedFrameIndex / fps
            : legacyFramesData.current[Math.min(clampedFrameIndex, legacyFramesData.current.length - 1)]?.timestamp ?? (clampedFrameIndex / fps);
          const driftMs = Math.round((realTime - frameTimestamp) * 1000);
          if (Math.abs(drift - driftMs) > 10) {
            setDrift(driftMs);
          }
        }
      }

      animationRef.current = requestAnimationFrame(renderLoop);
    };

    animationRef.current = requestAnimationFrame(renderLoop);
    return () => cancelAnimationFrame(animationRef.current);
  }, [currentTime, drift]);

  useEffect(() => {
    const loadInitialState = async () => {
      try {
        const [songsResponse, presetsResponse, state] = await Promise.all([
          fetch('/api/songs'),
          fetch('/api/presets'),
          fetchServerState(),
        ]);

        const songsData: string[] = await songsResponse.json();
        const presetsData: PresetSummary[] = await presetsResponse.json();
        setSongs(songsData);
        setPresets(presetsData);

        const initialPreset = presetsData.find((preset) => preset.preset_id === selectedShow) ?? presetsData[0] ?? null;
        if (initialPreset) {
          setSelectedShow(initialPreset.preset_id);
        }

        const initialSong = state.current_song && songsData.includes(state.current_song)
          ? state.current_song
          : songsData[0] ?? '';

        if (initialSong) {
          await handleLoad(initialSong);
        } else {
          setCurrentCanvas(state.current_canvas);
          clearFrames();
        }
      } catch (error) {
        console.error(error);
        setServerState('ERROR');
      }
    };

    void loadInitialState(); void loadOverlays();
    return () => {
      wavesurfer.current?.destroy();
    };
  }, []);
  useEffect(() => {
    const preset = presets.find((entry) => entry.preset_id === selectedShow) ?? null;
    setActivePreset(preset);
    setActiveTab(MAIN_TAB);

    if (preset) {
      const defaultParams = Object.fromEntries(
        preset.parameters.map((parameter) => [parameter.id, parameter.default]),
      );
      setParams(defaultParams);
    } else {
      setParams({});
    }
  }, [selectedShow, presets]);

  return (
    <div className="app-container">
      <div className="top-bar">
        <div className="selectors-group">
          <div className="selector">
            <label>SONG:</label>
            <select value={selectedSong} onChange={(event) => void handleLoad(event.target.value)}>
              {songs.map((song) => (
                <option key={song} value={song}>
                  {song}
                </option>
              ))}
            </select>
          </div>
          <div className="canvas-state">
            <span className="canvas-state-label">CANVAS:</span>
            <span className={currentCanvas ? 'canvas-state-value' : 'canvas-state-empty'}>
              {currentCanvas ? currentCanvas.replace('.json', '') : 'no canvas loaded'}
            </span>
          </div>
        </div>

        <div className="status-strip">
          <div className="drift-gauge">
            <div className="drift-baseline"></div>
            <div
              className="drift-bar"
              style={{
                width: `${Math.min(Math.abs(drift), 100)}%`,
                left: drift < 0 ? 'auto' : '50%',
                right: drift < 0 ? '50%' : 'auto',
              }}
            ></div>
            <span className="drift-text">{drift > 0 ? `+${drift}` : drift}ms</span>
          </div>
          <div className={`status-chip ${isPlaying ? 'success' : isLoaded ? 'success' : 'muted'}`}>
            {isPlaying ? 'PLAYING' : isLoaded ? 'READY' : 'IDLE'}
          </div>
          <div className={`status-chip ${serverState === 'CONNECTED' ? 'success' : serverState === 'GENERATING...' ? 'muted' : 'error'}`}>
            {serverState === 'CONNECTED' ? 'SERVER' : serverState}
          </div>
        </div>

        {metadataRef.current && (
          <div className="metadata-panel">
            <div className="metadata-row">
              <span>Schema: {metadataRef.current.schema_version}</span>
              <span>Render ID: {metadataRef.current.render_id?.substring(0, 8)}</span>
              <span>Preset: {metadataRef.current.preset_id}</span>
              <span>Seed: {metadataRef.current.seed}</span>
            </div>
            {metadataRef.current.analysis_diagnostics && (
              <div className="metadata-row">
                <span>Beat Confidence: {metadataRef.current.analysis_diagnostics.beat_confidence?.toFixed(2)}</span>
                <span>Sections: {metadataRef.current.analysis_structure?.section_candidates?.length || 0}</span>
                <span>Phrase Length: {metadataRef.current.analysis_structure?.phrases_interval?.toFixed(2)}s</span>
              </div>
            )}

            <Diagnostics metadata={metadataRef.current} />
          </div>
        )}
      </div>

      <div className="waveform-area">
        <div ref={waveformRef} className="waveform-container"></div>
      </div>

      <div className="transport-row">
        <div className="transport-controls">
          <button className="btn-icon load" onClick={() => void handleLoad()} disabled={!selectedSong} title="Load">
            <Upload size={24} />
          </button>
          <button className="btn-icon stop" onClick={handleStop} disabled={!isLoaded} title="Stop">
            <Square size={24} />
          </button>
          <button className={`btn-icon primary ${isPlaying ? 'pause' : 'play'}`} onClick={handlePlayPause} disabled={!isLoaded} title={isPlaying ? 'Pause' : 'Play'}>
            {isPlaying ? <Pause size={32} /> : <Play size={32} />}
          </button>
        </div>
        <div className="transport-clock">{formatTime(currentTime)}</div>
      </div>

      <div className="bottom-area">
        <div className="control-panel">
          <div className="control-tabs">
            {controlTabs.map((tab) => (
              <button
                key={tab}
                className={`control-tab ${tab === activeTab ? 'active' : ''}`}
                onClick={() => setActiveTab(tab)}
                type="button"
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="control-panel-body">
            {activeTab === MAIN_TAB ? (
              <div className="main-tab-panel">
                <div className="math-section">
                  <div className="math-section-title">Main</div>
                  <div className="form-group">
                    <label>Show Name</label>
                    <select value={selectedShow} onChange={(event) => setSelectedShow(event.target.value)}>
                      {presets.map((preset) => (
                        <option key={preset.preset_id} value={preset.preset_id}>
                          {preset.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  {activePreset && (
                    <div className="preset-summary">
                      <p>{activePreset.description}</p>
                      <div className="preset-tags">
                        {activePreset.tags.map((tag) => (
                          <span key={tag} className="tag-chip">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  <button className="render-button" onClick={handleGenerate} disabled={serverState === 'GENERATING...' || !selectedSong || !activePreset}>
                    {serverState === 'GENERATING...' ? 'GENERATING...' : 'RENDER'}
                  </button>
                </div>
              </div>
            ) : activeParameters.length > 0 ? (
              <div className="tab-panel">
                <div className="math-section-title">{activeTab}</div>
                {activeParameters.map((parameter) => (
                  <div className="form-group" key={parameter.id}>
                    <label>{parameter.label}</label>
                    {renderParameterInput(parameter)}
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-panel">No controls in this parameter group.</div>
            )}
          </div>
        </div>

        <div className="canvas-render">
          <canvas ref={canvasRef} width={100} height={50} className="main-canvas"></canvas>
        </div>
      </div>
    </div>
  );
}

export default App;
