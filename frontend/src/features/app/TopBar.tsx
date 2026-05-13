import React from 'react';
import type { ServerStatePayload, PresetSummary, ShowMetadata } from './types';

interface Props {
  songs: string[];
  selectedSong: string;
  onSongChange: (s: string) => void;
  currentCanvas: string | null;
  metadata?: ShowMetadata | null;
  isPlaying: boolean;
  isLoaded: boolean;
  drift: number;
  serverState: string;
}

export default function TopBar({ songs, selectedSong, onSongChange, currentCanvas, metadata, isPlaying, isLoaded, drift, serverState }: Props) {
  return (
    <div className="top-bar">
      <div className="selectors-group">
        <div className="selector">
          <label>SONG:</label>
          <select value={selectedSong} onChange={(e) => onSongChange(e.target.value)}>
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

      {metadata && (
        <div className="metadata-panel">
          <div className="metadata-row">
            <span>Schema: {metadata.schema_version}</span>
            <span>Render ID: {metadata.render_id?.substring(0, 8)}</span>
            <span>Preset: {metadata.preset_id}</span>
            <span>Seed: {metadata.seed}</span>
          </div>
        </div>
      )}
    </div>
  );
}
