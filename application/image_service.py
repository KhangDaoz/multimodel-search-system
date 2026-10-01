from PIL import Image
import numpy as np
class ImageService:
    def encode(self, path):
        # Handcrafted pixel descriptor, not a pretrained neural embedding.
        with Image.open(path) as image:
            rgb = np.asarray(image.convert('RGB').resize((16, 16)), dtype=float) / 255.0
        # Center pixels reduce the influence of the shared background.
        pixels = rgb[3:14, 3:14]
        return pixels.reshape(-1).tolist()
