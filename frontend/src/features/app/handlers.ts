export async function handleLoadImpl(songId, setSelectedSong, setIsLoaded, setIsPlaying, setCurrentTime, initWavesurfer, fetchFrames, setCurrentCanvas, setServerState) {
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
    const state = await response.json();
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
      // clear handled by caller if needed
      setCurrentCanvas(state.current_canvas);
    }
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error(error);
    setServerState('ERROR');
  }
}

export async function handleGenerateImpl(selectedSong, selectedShow, activePreset, params, setServerState, fetchServerState, fetchFrames, setCurrentCanvas, setSelectedSong) {
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
          }
        } else if (statusData.status === 'FAILED') {
          clearInterval(intervalId);
          setServerState('ERROR');
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error(error);
        clearInterval(intervalId);
        setServerState('ERROR');
      }
    }, 1000);
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error(error);
    setServerState('ERROR');
  }
}
