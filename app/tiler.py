"""Split a tall screenshot into overlapping tiles (ADR-002)."""

from typing import List

from PIL import Image

MAX_WIDTH = 1440
TILE_HEIGHT = 1600
OVERLAP = 100
MAX_TILES = 6


def tile_image(
    image: Image.Image,
    max_width: int = MAX_WIDTH,
    tile_height: int = TILE_HEIGHT,
    overlap: int = OVERLAP,
    max_tiles: int = MAX_TILES,
) -> List[Image.Image]:
    """Return tiles from the top of the page down.

    The image is first scaled down (never up) to max_width. Tiles are
    tile_height tall and overlap by `overlap` px; the last tile may be
    shorter. Only the first max_tiles tiles are returned, so very long
    pages are cut off at the bottom.
    """
    image = image.convert("RGB")
    if image.width > max_width:
        new_height = round(image.height * max_width / image.width)
        image = image.resize((max_width, new_height), Image.LANCZOS)

    step = tile_height - overlap
    tiles = []
    top = 0
    while len(tiles) < max_tiles:
        bottom = min(top + tile_height, image.height)
        tiles.append(image.crop((0, top, image.width, bottom)))
        if bottom >= image.height:
            break
        top += step
    return tiles
