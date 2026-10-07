"""Foreground-normalized pixel descriptor; no pretrained vision model is claimed."""
from PIL import Image, ImageOps
import numpy as np


class ImageService:
    MAX_PIXELS = 20_000_000

    def encode(self, path):
        with Image.open(path) as source:
            if source.width * source.height > self.MAX_PIXELS:
                raise ValueError('Image is too large; maximum 20 megapixels')
            image = ImageOps.exif_transpose(source).convert('RGBA')
            canvas = Image.new('RGBA', image.size, 'white')
            canvas.alpha_composite(image)
            image = canvas.convert('RGB')
            # White studio backgrounds carry little product information.
            probe = np.asarray(image.resize((128, 128)), dtype=float)
            foreground = np.min(probe, axis=2) < 240
            if foreground.any():
                ys, xs = np.where(foreground)
                margin = 3
                box = (max(0, int(xs.min()) - margin), max(0, int(ys.min()) - margin),
                       min(128, int(xs.max()) + margin + 1), min(128, int(ys.max()) + margin + 1))
                image = Image.fromarray(probe.astype('uint8')).crop(box)
            image = ImageOps.pad(image, (16, 16), method=Image.Resampling.LANCZOS, color='white')
            # Invert so a white background contributes zero instead of dominating cosine.
            descriptor = 1.0 - np.asarray(image, dtype=float) / 255.0
        return descriptor.reshape(-1).tolist()
