import { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Pause, Play, Square, Upload } from 'lucide-react';
import Diagnostics from './Diagnostics';
import type { Fixture } from './types/layers';

import CanvasRenderer from './features/app/CanvasRenderer';
import ParameterInput from './features/app/ParameterInput';
import TransportControls from './features/app/TransportControls';
import TopBar from './features/app/TopBar';
import BottomArea from './features/app/BottomArea';
import useAppState from './features/app/useAppState';

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
  const app = useAppState();
  const {
    songs,
    presets,
    selectedSong,
    setSelectedSong,
    selectedShow,
    setSelectedShow,
    currentCanvas,
    activePreset,
    params,
    activeTab,
    setActiveTab,
    isPlaying,
    isLoaded,
    currentTime,
    drift,
    serverState,
    waveformRef,
    wavesurfer,
    legacyFramesData,
    binaryFramesData,
    metadataRef,
    overlaysRef,
    handleLoad,
    handlePlayPause,
    handleStop,
    handleGenerate,
    formatTime,
    handleParamChange,
    controlTabs,
    activeParameters,
    setDrift,
  } = app;

  return (
    <div className="app-container">
      <TopBar
        songs={songs}
        selectedSong={selectedSong}
        onSongChange={(s) => void handleLoad(s)}
        currentCanvas={currentCanvas}
        metadata={metadataRef.current}
        isPlaying={isPlaying}
        isLoaded={isLoaded}
        drift={drift}
        serverState={serverState}
      />

      <div className="waveform-area">
        <div ref={waveformRef} className="waveform-container"></div>
      </div>

      <div className="transport-row">
        <TransportControls isLoaded={isLoaded} isPlaying={isPlaying} onLoad={() => void handleLoad()} onStop={handleStop} onPlayPause={handlePlayPause} />
        <div className="transport-clock">{formatTime(currentTime)}</div>
      </div>

      <BottomArea
        controlTabs={controlTabs}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        activeParameters={activeParameters}
        presets={presets}
        selectedShow={selectedShow}
        setSelectedShow={setSelectedShow}
        activePreset={activePreset}
        handleGenerate={handleGenerate}
        serverState={serverState}
        params={params}
        handleParamChange={handleParamChange}
        metadataRef={metadataRef}
        legacyFramesData={legacyFramesData}
        binaryFramesData={binaryFramesData}
        overlaysRef={overlaysRef}
        wavesurfer={wavesurfer}
        setDrift={setDrift}
      />
    </div>
  );
}

export default App;
