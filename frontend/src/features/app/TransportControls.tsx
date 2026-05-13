import React from 'react';
import { Pause, Play, Square, Upload } from 'lucide-react';

interface Props {
  isLoaded: boolean;
  isPlaying: boolean;
  onLoad: () => void;
  onStop: () => void;
  onPlayPause: () => void;
}

export default function TransportControls({ isLoaded, isPlaying, onLoad, onStop, onPlayPause }: Props) {
  return (
    <div className="transport-controls">
      <button className="btn-icon load" onClick={onLoad} disabled={!isLoaded} title="Load">
        <Upload size={24} />
      </button>
      <button className="btn-icon stop" onClick={onStop} disabled={!isLoaded} title="Stop">
        <Square size={24} />
      </button>
      <button className={`btn-icon primary ${isPlaying ? 'pause' : 'play'}`} onClick={onPlayPause} disabled={!isLoaded} title={isPlaying ? 'Pause' : 'Play'}>
        {isPlaying ? <Pause size={32} /> : <Play size={32} />}
      </button>
    </div>
  );
}
