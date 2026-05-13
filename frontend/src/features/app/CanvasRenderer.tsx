import { useEffect, useRef } from 'react';
import type {
  ShowMetadata,
} from './types';

interface Props {
  metadataRef: { current: ShowMetadata | null };
  legacyFramesData: { current: { timestamp: number; pixels: number[] }[] };
  binaryFramesData: { current: Uint8Array | null };
  overlaysRef: { current: { fixtures: any[]; pois: any[] } };
  wavesurfer: { current: any };
  fpsFallback?: number;
  setDrift: (v: number) => void;
}

export default function CanvasRenderer({
  metadataRef,
  legacyFramesData,
  binaryFramesData,
  overlaysRef,
  wavesurfer,
  fpsFallback = 50,
  setDrift,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const imageDataRef = useRef<ImageData | null>(null);
  const animationRef = useRef<number>(0);

  useEffect(() => {
    const renderLoop = () => {
      const realTime = wavesurfer.current?.getCurrentTime() || 0;
      const metadata = metadataRef.current;
      const hasLegacyFrames = legacyFramesData.current.length > 0;
      const hasBinaryFrames = binaryFramesData.current !== null;

      if (canvasRef.current && metadata && (hasLegacyFrames || hasBinaryFrames)) {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          const fps = metadata.fps || fpsFallback;
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

          const drawMarker = (x: number, y: number, kind: 'fixture' | 'poi') => {
            const px = x * metaW * (canvas.width / metaW);
            const py = y * metaH * (canvas.height / metaH);
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
          setDrift(driftMs);
        }
      }

      animationRef.current = requestAnimationFrame(renderLoop);
    };

    animationRef.current = requestAnimationFrame(renderLoop);
    return () => cancelAnimationFrame(animationRef.current);
  }, [metadataRef, legacyFramesData, binaryFramesData, overlaysRef, wavesurfer, fpsFallback, setDrift]);

  return <canvas ref={canvasRef} width={100} height={50} className="main-canvas"></canvas>;
}
