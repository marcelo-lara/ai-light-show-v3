import { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Pause, Play, Square, Upload } from 'lucide-react';
import Diagnostics from './Diagnostics';
import type { Fixture } from './types/layers';

import CanvasRenderer from './features/app/CanvasRenderer';

import type {
  FrameData,
  PresetParameter,
  ModulatorConfig,
  AnalysisFeatures,
  TransitionSchema,
  SceneSchema,
  TimelineSchema,
  PresetSummary,
  ShowMetadata,
  ShowData,
  ServerStatePayload,
} from './features/app/types';

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

  const fetchChunkedFrameData = async (chunkPaths: string[]) => {
    const chunks = await Promise.all(
      chunkPaths.map(async (chunkPath) => {
        const response = await fetch(`/data/canvas/${encodeURIComponent(chunkPath)}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch frame chunk: ${chunkPath}`);
        }

        return new Uint8Array(await response.arrayBuffer());
      }),
    );

    const totalLength = chunks.reduce((length, chunk) => length + chunk.byteLength, 0);
    const frameBytes = new Uint8Array(totalLength);
    let offset = 0;
    for (const chunk of chunks) {
      frameBytes.set(chunk, offset);
      offset += chunk.byteLength;
    }

    return frameBytes;
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
      if (
        data.metadata.schema_version !== 'v2'
        || data.metadata.frame_encoding !== 'rgb24'
        || !data.metadata.frame_chunks?.length
      ) {
        setServerState('INCOMPATIBLE_SCHEMA');
        clearFrames();
        return;
      }

      const frameBytes = await fetchChunkedFrameData(data.metadata.frame_chunks);
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
      setServerState('CONNECTED');
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

  // Render loop moved to CanvasRenderer component

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
          <CanvasRenderer metadataRef={metadataRef} legacyFramesData={legacyFramesData} binaryFramesData={binaryFramesData} overlaysRef={overlaysRef} wavesurfer={wavesurfer} setDrift={setDrift} />
        </div>
      </div>
    </div>
  );
}

export default App;
