export function initWavesurferImpl({ songId, waveformRef, wavesurfer, setIsLoaded, setCurrentTime, setIsPlaying }: any) {
  if (!songId || !waveformRef.current) {
    return;
  }

  if (wavesurfer.current) {
    wavesurfer.current.destroy();
  }

  // dynamic import to avoid SSR issues
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const WaveSurfer = require('wavesurfer.js').default;

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
  wavesurfer.current.on('audioprocess', (time: number) => setCurrentTime(time));
  wavesurfer.current.on('seeking', (time: number) => setCurrentTime(time));
  wavesurfer.current.on('play', () => setIsPlaying(true));
  wavesurfer.current.on('pause', () => setIsPlaying(false));
}
