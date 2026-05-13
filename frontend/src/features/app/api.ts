export async function loadOverlaysImpl(overlaysRef: any) {
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
    // keep quiet
  }
}

export async function fetchServerStateImpl() {
  const response = await fetch('/api/current_state');
  return response.json();
}

export async function fetchChunkedFrameDataImpl(chunkPaths: string[]) {
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
}

export async function fetchFramesImpl(canvasId: string | null, songId: string | null, metadataRef: any, legacyFramesData: any, binaryFramesData: any, setCurrentCanvas: (s: string|null)=>void, setServerState: (s:string)=>void) {
  if (!songId && !canvasId) {
    return;
  }

  const canvasToLoad = canvasId
    ? (canvasId.endsWith('.json') ? canvasId : `${canvasId}.json`)
    : `${songId}.undersea_pulse_01.json`;

  try {
    const response = await fetch(`/data/canvas/${encodeURIComponent(canvasToLoad)}`);
    if (!response.ok) {
      metadataRef.current = null;
      legacyFramesData.current = [];
      binaryFramesData.current = null;
      return;
    }

    const data = await response.json();
    if (
      data.metadata.schema_version !== 'v2'
      || data.metadata.frame_encoding !== 'rgb24'
      || !data.metadata.frame_chunks?.length
    ) {
      setServerState('INCOMPATIBLE_SCHEMA');
      metadataRef.current = null;
      legacyFramesData.current = [];
      binaryFramesData.current = null;
      return;
    }

    const frameBytes = await fetchChunkedFrameDataImpl(data.metadata.frame_chunks);
    const bytesPerFrame = data.metadata.bytes_per_frame ?? data.metadata.resolution.width * data.metadata.resolution.height * 3;
    const expectedBytes = bytesPerFrame * data.metadata.frame_count;
    if (frameBytes.byteLength !== expectedBytes) {
      setServerState('INCOMPATIBLE_SCHEMA');
      metadataRef.current = null;
      legacyFramesData.current = [];
      binaryFramesData.current = null;
      return;
    }

    metadataRef.current = data.metadata;
    legacyFramesData.current = [];
    binaryFramesData.current = frameBytes;
    setCurrentCanvas(canvasToLoad);
    setServerState('CONNECTED');
  } catch (error) {
    metadataRef.current = null;
    legacyFramesData.current = [];
    binaryFramesData.current = null;
    setServerState('ERROR');
  }
}
