import numpy as np

class Compositor:
    @staticmethod
    def blend_max(layer1, layer2):
        return np.maximum(layer1, layer2)
        
    @staticmethod
    def blend_add(layer1, layer2):
        # Add and clip to 255
        return np.clip(layer1.astype(np.uint16) + layer2.astype(np.uint16), 0, 255).astype(np.uint8)
