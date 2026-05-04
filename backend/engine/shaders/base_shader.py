from abc import ABC, abstractmethod
import numpy as np

class BaseShader(ABC):
    """
    Abstract base class for all BeatDrop-style visualizer shaders.
    """
    
    @abstractmethod
    def render(self, coords, audio_features, q_buffer, **kwargs):
        """
        Renders the shader effect onto the provided coordinates.
        
        Args:
            coords (np.ndarray): The (N, 2) array of fixture coordinates (x, y).
            audio_features (dict): Dictionary containing the 5-band FFT and onset data for the current frame.
                                   Keys: 'sub_bass', 'bass', 'low_mid', 'high_mid', 'treble', 'onset', 'is_beat'
            q_buffer (dict): Persistent state dictionary spanning across frames.
            kwargs: Any additional parameters.
            
        Returns:
            np.ndarray: An (N, 3) array of RGB values [0-255] for each coordinate.
        """
        pass
