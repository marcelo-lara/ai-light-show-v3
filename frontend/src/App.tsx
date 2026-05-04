import { useState, useEffect, useRef } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Play, Pause, Square, Upload } from 'lucide-react';

const SHOWS = [
  "wave_01",
  "pulse_01"
];

interface FrameData {
  timestamp: number;
  pixels: number[];
}

interface ShowData {
  metadata: {
    song_name: string;
    show_id: string;
    fps: number;
    resolution: { width: number; height: number };
    duration_sec: number;
    total_frames: number;
  };
  frames: FrameData[];
}

function App() {
  const [songs, setSongs] = useState<string[]>([]);
  const [selectedSong, setSelectedSong] = useState("");
  const [selectedShow, setSelectedShow] = useState("wave_01");
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [drift, setDrift] = useState(0);
  const [serverState, setServerState] = useState("CONNECTED");
  
  const waveformRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wavesurfer = useRef<WaveSurfer | null>(null);
  const framesData = useRef<FrameData[]>([]);
  const metadataRef = useRef<ShowData['metadata'] | null>(null);
  const animationRef = useRef<number>(0);

  // Math parameters
  const [beatSensitivity, setBeatSensitivity] = useState(50);
  const [waveSpeed, setWaveSpeed] = useState(10);
  const [waveHeight, setWaveHeight] = useState(5);
  const [sizeMultiplier, setSizeMultiplier] = useState(50);

  const initWavesurfer = () => {
    if (waveformRef.current) {
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
        url: `/data/songs/${selectedSong}.mp3`,
      });

      wavesurfer.current.on('ready', () => {
        setIsLoaded(true);
      });

      wavesurfer.current.on('audioprocess', (time) => {
        setCurrentTime(time);
      });

      wavesurfer.current.on('seeking', (time) => {
        setCurrentTime(time);
      });

      wavesurfer.current.on('play', () => setIsPlaying(true));
      wavesurfer.current.on('pause', () => setIsPlaying(false));
    }
  };

  const fetchFrames = async () => {
    if (!selectedSong) return;
    try {
      const response = await fetch(`/data/canvas/${selectedSong}.${selectedShow}.json`);
      if (response.ok) {
        const data: ShowData = await response.json();
        metadataRef.current = data.metadata;
        framesData.current = data.frames;
      } else {
        metadataRef.current = null;
        framesData.current = [];
      }
    } catch (e) {
      console.error(e);
      metadataRef.current = null;
      framesData.current = [];
    }
  };

  const handleLoad = () => {
    setIsLoaded(false);
    setIsPlaying(false);
    setCurrentTime(0);
    initWavesurfer();
    fetchFrames();
  };

  const handlePlayPause = () => {
    if (wavesurfer.current) {
      wavesurfer.current.playPause();
    }
  };

  const handleStop = () => {
    if (wavesurfer.current) {
      wavesurfer.current.stop();
      setIsPlaying(false);
      setCurrentTime(0);
    }
  };

  const handleGenerate = async () => {
    if (!selectedSong || !selectedShow) return;
    
    setServerState("GENERATING...");
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          song_name: selectedSong,
          show_id: selectedShow,
          beat_sensitivity: beatSensitivity,
          wave_speed: waveSpeed,
          wave_height: waveHeight,
          size_multiplier: sizeMultiplier
        })
      });
      
      const data = await response.json();
      const jobId = data.job;
      
      if (jobId) {
        const intervalId = setInterval(async () => {
          try {
            const statusRes = await fetch(`/api/status/${jobId}`);
            const statusData = await statusRes.json();
            
            if (statusData.status === 'COMPLETED') {
              clearInterval(intervalId);
              setServerState("CONNECTED");
              handleLoad(); // Reload the UI with the new frames
            } else if (statusData.status === 'FAILED') {
              clearInterval(intervalId);
              setServerState("ERROR");
            }
          } catch (e) {
            clearInterval(intervalId);
            setServerState("ERROR");
          }
        }, 1000);
      }
    } catch (e) {
      console.error(e);
      setServerState("ERROR");
    }
  };

  const formatTime = (timeInSeconds: number) => {
    const mins = Math.floor(timeInSeconds / 60);
    const secs = Math.floor(timeInSeconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Rendering loop
  useEffect(() => {
    const renderLoop = () => {
      // Get the exact playback time from wavesurfer to avoid react state delay
      const realTime = wavesurfer.current?.getCurrentTime() || currentTime;
      
      if (canvasRef.current && framesData.current.length > 0 && metadataRef.current) {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          const fps = metadataRef.current.fps || 50;
          const frameIndex = Math.floor(realTime * fps);
          const frame = framesData.current[Math.min(frameIndex, framesData.current.length - 1)];
          
          if (frame && frame.pixels) {
            const width = metadataRef.current.resolution.width;
            const height = metadataRef.current.resolution.height;
            const imageData = ctx.createImageData(width, height);
            
            for (let i = 0; i < frame.pixels.length; i++) {
              const val = frame.pixels[i];
              const idx = i * 4;
              
              const r = (val >> 16) & 0xFF;
              const g = (val >> 8) & 0xFF;
              const b = val & 0xFF;
              
              imageData.data[idx] = r;
              imageData.data[idx + 1] = g;
              imageData.data[idx + 2] = b;
              imageData.data[idx + 3] = 255;
            }
            ctx.putImageData(imageData, 0, 0);
          }
          
          // Calculate drift: difference between audio time and the frame timestamp
          if (frame) {
            const driftMs = Math.round((realTime - frame.timestamp) * 1000);
            // Throttle drift updates to avoid react rendering too often,
            // but for spec compliance let's just use it (or update a ref and periodically sync to state)
            if (Math.abs(drift - driftMs) > 10) {
              setDrift(driftMs);
            }
          }
        }
      }
      animationRef.current = requestAnimationFrame(renderLoop);
    };

    animationRef.current = requestAnimationFrame(renderLoop);
    return () => cancelAnimationFrame(animationRef.current);
  }, [currentTime, drift]);

  useEffect(() => {
    fetch('/api/songs')
      .then(res => res.json())
      .then(data => {
        setSongs(data);
        if (data.length > 0) {
          setSelectedSong(data[0]);
        }
      })
      .catch(err => console.error(err));

    return () => {
      if (wavesurfer.current) {
        wavesurfer.current.destroy();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run on mount

  // Watch for selectedSong to be set initially, and load
  useEffect(() => {
    if (selectedSong && !isLoaded && !wavesurfer.current) {
      initWavesurfer();
      fetchFrames();
    }
  }, [selectedSong]);

  return (
    <div className="app-container">
      {/* Zone 1: Top Bar */}
      <div className="top-bar">
        <div className="selectors-group">
          <div className="selector">
            <label>SONG:</label>
            <select value={selectedSong} onChange={(e) => setSelectedSong(e.target.value)}>
              {songs.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="selector">
            <label>SHOW:</label>
            <select value={selectedShow} onChange={(e) => setSelectedShow(e.target.value)} disabled={!selectedSong}>
              {SHOWS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>
        <div className="status-strip">
          <div className="drift-gauge">
            <div className="drift-baseline"></div>
            <div className="drift-bar" style={{ width: `${Math.min(Math.abs(drift), 100)}%`, left: drift < 0 ? 'auto' : '50%', right: drift < 0 ? '50%' : 'auto' }}></div>
            <span className="drift-text">{drift > 0 ? `+${drift}` : drift}ms</span>
          </div>
          <div className={`status-chip ${isPlaying ? 'success' : isLoaded ? 'success' : 'muted'}`}>
            {isPlaying ? 'PLAYING' : isLoaded ? 'READY' : 'IDLE'}
          </div>
          <div className={`status-chip ${serverState === 'CONNECTED' ? 'success' : serverState === 'GENERATING...' ? 'muted' : 'error'}`}>
            {serverState === 'CONNECTED' ? 'SERVER' : serverState}
          </div>
        </div>
      </div>

      {/* Zone 2: Waveform Area */}
      <div className="waveform-area">
        <div ref={waveformRef} className="waveform-container"></div>
      </div>

      {/* Zone 3: Transport Controls */}
      <div className="transport-row">
        <div className="transport-controls">
          <button className="btn-icon load" onClick={handleLoad} disabled={!selectedSong} title="Load">
            <Upload size={24} />
          </button>
          <button className="btn-icon stop" onClick={handleStop} disabled={!isLoaded} title="Stop">
            <Square size={24} />
          </button>
          <button className={`btn-icon primary ${isPlaying ? 'pause' : 'play'}`} onClick={handlePlayPause} disabled={!isLoaded} title={isPlaying ? 'Pause' : 'Play'}>
            {isPlaying ? <Pause size={32} /> : <Play size={32} />}
          </button>
        </div>
        <div className="transport-clock">
          {formatTime(currentTime)}
        </div>
      </div>

      {/* Zone 4: Bottom Area */}
      <div className="bottom-area">
        <div className="math-parameters">
          <div className="math-section">
            <div className="math-section-title">Beat Detection</div>
            <div className="form-group">
              <label>Sensitivity</label>
              <input type="range" min="0" max="100" value={beatSensitivity} onChange={(e) => setBeatSensitivity(Number(e.target.value))} />
              <span className="range-value">{beatSensitivity}%</span>
            </div>
          </div>
          <div className="math-section">
            <div className="math-section-title">Wave Logic</div>
            <div className="form-group">
              <label>Speed Modifier</label>
              <input type="range" min="1" max="50" value={waveSpeed} onChange={(e) => setWaveSpeed(Number(e.target.value))} />
              <span className="range-value">{waveSpeed}x</span>
            </div>
            <div className="form-group">
              <label>Amplitude Base</label>
              <input type="range" min="1" max="20" value={waveHeight} onChange={(e) => setWaveHeight(Number(e.target.value))} />
              <span className="range-value">{waveHeight}px</span>
            </div>
          </div>
          <div className="math-section">
            <div className="math-section-title">Shapes</div>
            <div className="form-group">
              <label>Size Multiplier</label>
              <input type="range" min="1" max="100" value={sizeMultiplier} onChange={(e) => setSizeMultiplier(Number(e.target.value))} />
              <span className="range-value">{sizeMultiplier}%</span>
            </div>
            <button 
              style={{
                width: '100%', 
                marginTop: '1.5rem', 
                padding: '0.75rem', 
                backgroundColor: serverState === 'GENERATING...' ? '#333' : '#9000dd', 
                color: serverState === 'GENERATING...' ? '#888' : '#fff', 
                border: 'none', 
                fontFamily: 'monospace',
                fontWeight: 'bold',
                cursor: serverState === 'GENERATING...' ? 'not-allowed' : 'pointer'
              }} 
              onClick={handleGenerate} 
              disabled={serverState === 'GENERATING...'}
            >
              {serverState === 'GENERATING...' ? 'GENERATING...' : 'APPLY PARAMETERS'}
            </button>
          </div>
        </div>
        <div className="canvas-render">
          <canvas
            ref={canvasRef}
            width="100"
            height="50"
            className="main-canvas"
            style={{ width: '1000px', height: '500px', imageRendering: 'pixelated' }}
          ></canvas>
        </div>
      </div>
    </div>
  );
}

export default App;
