import { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import type {
  FrameData,
  PresetParameter,
  PresetSummary,
  ShowMetadata,
  ServerStatePayload,
} from './types';

export default function useAppState() {
  const [songs, setSongs] = useState<string[]>([]);
  const [presets, setPresets] = useState<PresetSummary[]>([]);
  const [selectedSong, setSelectedSong] = useState('');
  const [selectedShow, setSelectedShow] = useState('undersea_pulse_01');
  const [currentCanvas, setCurrentCanvas] = useState<string | null>(null);
  const [activePreset, setActivePreset] = useState<PresetSummary | null>(null);
  const [params, setParams] = useState<Record<string, boolean | number | string>>({});
  const [activeTab, setActiveTab] = useState('Main');
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

  const overlaysRef = useRef({ fixtures: [] as any[], pois: [] as any[] });

  // Delegates and helpers (mirror App behavior but extracted)
  const loadOverlays = () => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { loadOverlaysImpl } = require('./api');
      void loadOverlaysImpl(overlaysRef);
    } catch (e) {
      // noop
    }
  };

  const initWavesurfer = (songId = selectedSong) => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { initWavesurferImpl } = require('./wavesurfer');
      initWavesurferImpl({ songId, waveformRef, wavesurfer, setIsLoaded, setCurrentTime, setIsPlaying });
    } catch (e) {
      // noop
    }
  };

  const clearFrames = () => {
    metadataRef.current = null;
    legacyFramesData.current = [];
    binaryFramesData.current = null;
  };

  const fetchServerState = async () => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { fetchServerStateImpl } = require('./api');
      return await fetchServerStateImpl();
    } catch (e) {
      return { current_canvas: null, current_song: null } as unknown as ServerStatePayload;
    }
  };

  const fetchChunkedFrameData = async (chunkPaths: string[]) => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { fetchChunkedFrameDataImpl } = require('./api');
      return await fetchChunkedFrameDataImpl(chunkPaths);
    } catch (e) {
      return new Uint8Array();
    }
  };

  const fetchFrames = async (canvasId: string | null = null, songId = selectedSong) => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { fetchFramesImpl } = require('./api');
      await fetchFramesImpl(canvasId, songId, metadataRef, legacyFramesData, binaryFramesData, setCurrentCanvas, setServerState);
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error(e);
      clearFrames();
    }
  };

  const handleLoad = async (songId = selectedSong) => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { handleLoadImpl } = require('./handlers');
      await handleLoadImpl(songId, setSelectedSong, setIsLoaded, setIsPlaying, setCurrentTime, initWavesurfer, fetchFrames, setCurrentCanvas, setServerState);
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error(e);
      setServerState('ERROR');
    }
  };

  const handlePlayPause = () => {
    wavesurfer.current?.playPause();
  };

  const handleStop = () => {
    if (!wavesurfer.current) return;
    wavesurfer.current.stop();
    setIsPlaying(false);
    setCurrentTime(0);
  };

  const handleGenerate = async () => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { handleGenerateImpl } = require('./handlers');
      await handleGenerateImpl(selectedSong, selectedShow, activePreset, params, setServerState, fetchServerState, fetchFrames, setCurrentCanvas, setSelectedSong);
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error(e);
      setServerState('ERROR');
    }
  };

  const formatTime = (timeInSeconds: number) => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { formatTime: _f } = require('./utils');
      return _f(timeInSeconds);
    } catch (e) {
      return String(Math.floor(timeInSeconds));
    }
  };

  const handleParamChange = (parameterId: string, value: boolean | number | string) => {
    setParams((currentParams) => ({ ...currentParams, [parameterId]: value }));
  };

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
        if (initialPreset) setSelectedShow(initialPreset.preset_id);

        const initialSong = state.current_song && songsData.includes(state.current_song) ? state.current_song : songsData[0] ?? '';
        if (initialSong) {
          await handleLoad(initialSong);
        } else {
          setCurrentCanvas(state.current_canvas);
          clearFrames();
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error(error);
        setServerState('ERROR');
      }
    };

    void loadInitialState();
    void loadOverlays();
    return () => wavesurfer.current?.destroy();
  }, []);

  useEffect(() => {
    const preset = presets.find((entry) => entry.preset_id === selectedShow) ?? null;
    setActivePreset(preset);
    setActiveTab('Main');

    if (preset) {
      const defaultParams = Object.fromEntries(preset.parameters.map((parameter: PresetParameter) => [parameter.id, parameter.default]));
      setParams(defaultParams);
    } else {
      setParams({});
    }
  }, [selectedShow, presets]);

  const parameterGroups = activePreset ? [...new Set(activePreset.parameters.map((parameter) => parameter.ui_group))] : [];
  const controlTabs = ['Main', ...parameterGroups];
  const activeParameters = activePreset ? activePreset.parameters.filter((parameter) => parameter.ui_group === activeTab) : [];

  return {
    songs,
    presets,
    selectedSong,
    setSelectedSong,
    selectedShow,
    setSelectedShow,
    currentCanvas,
    setCurrentCanvas,
    activePreset,
    params,
    setParams,
    activeTab,
    setActiveTab,
    isPlaying,
    isLoaded,
    currentTime,
    drift,
    serverState,
    setServerState,
    waveformRef,
    canvasRef,
    wavesurfer,
    legacyFramesData,
    binaryFramesData,
    metadataRef,
    overlaysRef,
    initWavesurfer,
    fetchFrames,
    handleLoad,
    handlePlayPause,
    handleStop,
    handleGenerate,
    formatTime,
    handleParamChange,
    controlTabs,
    activeParameters,
    setDrift,
  } as const;
}
