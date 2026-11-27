"""Prepare palette-neutral photographic maps for early props and Blender sets."""

from pathlib import Path
from functools import lru_cache

import numpy as np
from PIL import Image

PHOTOGRAPHS = Path(__file__).resolve().parent / 'surfaces'
SOURCES = {
    'siding': 'blue_painted_planks', 'timber': 'weathered_planks', 'bark': 'bark_brown_02',
    'stone': 'rock_face_03', 'plaster': 'plastered_wall_04', 'brick': 'brown_brick_02',
    'road': 'asphalt_02', 'sand': 'gravelly_sand', 'roof': 'roof_tiles_14',
    'metal': 'rusty_metal_04', 'corrugated': 'corrugated_iron_02', 'leather': 'fabric_leather_02',
}

@lru_cache(maxsize=None)
def photo(kind, size):
    name = SOURCES[kind]
    source = Image.open(PHOTOGRAPHS / f'{name}_diff.jpg').resize((size, size), Image.Resampling.LANCZOS)
    rgb = np.asarray(source).astype(float)
    raw = rgb @ np.array([.2126, .7152, .0722])
    low, high = np.percentile(raw, [4,96])
    fine = np.clip((raw - np.median(raw)) / max(high - low, 28), -.62, .62)
    return fine, rgb - raw[...,None]


@lru_cache(maxsize=None)
def photo_normal(kind, size):
    source = Image.open(PHOTOGRAPHS / f'{SOURCES[kind]}_nor_gl.jpg')
    return np.asarray(source.resize((size,size), Image.Resampling.LANCZOS)).astype(float) / 127.5 - 1


def game_maps(folder):
    folder.mkdir(parents=True, exist_ok=True)
    for kind in SOURCES:
        fine, chroma = photo(kind, 640)
        brightness = 211 + fine * (65 if kind == 'metal' else 104)
        pixels = brightness[...,None] + .17 * chroma
        path = folder / f'{kind}.jpg'
        Image.fromarray(np.uint8(np.clip(pixels,0,255))).save(path,quality=92,optimize=True)
        source = PHOTOGRAPHS / f'{SOURCES[kind]}_nor_gl.jpg'
        (folder / f'{kind}_n.jpg').write_bytes(source.read_bytes())
