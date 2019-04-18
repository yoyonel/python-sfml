"""
"""
import logging
import numpy as np
from pathlib import Path
from sfml import sf
from tifffile import tifffile
from typing import Tuple

logger = logging.getLogger(__name__)


def generate_sat(fn_img: str) -> Tuple[Path, np.array]:
    # http://developer.amd.com/wordpress/media/2012/10/GDC2005_SATEnvironmentReflections.pdf
    # https://developer.nvidia.com/gpugems/GPUGems3/gpugems3_ch39.html
    # "Fast Summed-Area Table Generation and its Applications"
    # http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.90.8836&rep=rep1&type=pdf

    image = sf.Image.from_file(fn_img)
    logger.info(
        f"Generate Summed Area Table from: '{fn_img}' ({image.width}, "
        f"{image.height}) ...")
    nparray_image = np.array(
        np.ndarray(
            (image.width, image.height, 4),
            buffer=image.pixels,
            dtype=np.uint8
        )
    )
    normed_image = nparray_image / 255.0
    pixel_average = np.average(normed_image, axis=(0, 1))
    normed_image = np.add(normed_image, pixel_average * -1.0)
    sat = normed_image.cumsum(axis=0).cumsum(axis=1)

    assert all(np.isclose(
        (sat[512][512] + sat[511][511]) - (sat[511][512] + sat[512][511]),
        normed_image[512][512]))

    # https://stackoverflow.com/questions/52490653/saving-float-numpy-images
    path_img = Path(fn_img)
    path_sat = path_img.with_name(path_img.stem + '.sat.tif')
    logger.info(f"export SAT: {path_sat}")
    tifffile.imsave(str(path_sat), sat)

    return path_sat, pixel_average
