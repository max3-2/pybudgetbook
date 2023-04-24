"""Image filtering functions"""
import numpy as np
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
from skimage import io as skio
from skimage.filters import threshold_otsu, rank
from skimage.transform import rescale
from skimage.filters import unsharp_mask
from skimage.segmentation import clear_border
from skimage.morphology import disk, diamond, binary_erosion
from skimage.util import img_as_ubyte

#TODO relative
import pybudgetbook.config.constants as bbconstants


def load_image(imgpath):
    return rgb2gray(skio.imread(imgpath))


def preprocess_image(grayscale, otsu='global',
                     rescale_image=True, unsharp_ma=True, final_er_dil=1,
                     remove_border_art=True, receipt_width=80, show=False):
    """
    Assumes portrait mode. Filter factors are designed after scaling!

    width in mm
    """
    if rescale_image:
        scale = bbconstants._TARGET_DPI / grayscale.shape[1] * (80 / 25.4)
        proc_img = rescale(grayscale, scale)

    if unsharp_ma:
        proc_img = unsharp_mask(proc_img, radius=5, amount=0.7)

    # Convert to binary
    if otsu == 'global':
        threshold = threshold_otsu(proc_img)
        dilate_kernel = diamond(1)
        bin_img = proc_img >= threshold

    elif otsu == 'local':
        radius = 29
        selem = disk(radius)
        threshold = rank.otsu(img_as_ubyte(proc_img), selem) / 255
        dilate_kernel = disk(1)
        bin_img = proc_img >= threshold
        bin_img = binary_erosion(bin_img, disk(2))

    # If final filters are set, do the best to get strong black letters
    if final_er_dil >= 1:
        for i in range(final_er_dil):
            bin_img = binary_erosion(bin_img, dilate_kernel)
        # bin_img = gaussian(bin_img, sigma=1) > threshold

    if remove_border_art:
        bin_img = ~clear_border(~bin_img, 30)

    # Pad the image, grayscale with nan for plotting and binary with ones
    # Padding is set to approx. 10pt ~ 50px
    proc_img = np.pad(proc_img, ((50, 50), (50, 50)), constant_values=np.nan)
    bin_img = np.pad(bin_img, ((50, 50), (50, 50)), constant_values=1)

    return proc_img, bin_img
