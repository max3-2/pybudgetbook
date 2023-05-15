"""Image filtering functions"""
import numpy as np
from skimage.color import rgb2gray
from skimage import io as skio
from skimage.filters import threshold_otsu, rank
from skimage.transform import rescale
from skimage.filters import unsharp_mask
from skimage.segmentation import clear_border
from skimage.morphology import disk, diamond, binary_erosion
from skimage.util import img_as_ubyte


from .configs import constants


def load_image(imgpath):
    """Loads image and converts to grayscale"""
    return rgb2gray(skio.imread(imgpath))


def preprocess_image(grayscale, otsu='global',
                     rescale_image=True, unsharp_ma=(5, 1.15), final_er_dil=1,
                     remove_border_art=True, receipt_width=80):
    """
    Takes a grayscale image and processes the image for best tesseract result.
    The image is scaled to a good resolution and the filter parameters are
    designed for that resolution, so changing can have different effects.

    Filtering includes rescaling, unsharp masking, binarization, erosion and
    border removal and final padding.

    Parameters
    ----------
    grayscale : `ndarray`
        Input image as numpy array, grayscale
    otsu : `str`, optional
        Use global or local otsu threshold detection, by default 'global'
    rescale_image : `bool`, optional
        Apply rescale to approx. 600dpi before filtering, by default True
    unsharp_ma : `tuple`, optional
        Unsharp mask parameters, by default (5, 1.15)
    final_er_dil : `int`, optional
        The number of erosion passes to apply to the binary image, by default 1
    remove_border_art : `bool`, optional
        Removes a possible border from the binary image, if e.g. image was
        taken on a dark background, by default True
    receipt_width : `int`, optional
        Approximate receipt width in millimeters. Used for calculating the
        correct scale and final dimensions, by default 80

    Returns
    -------
    `(ndarray, ndarray)`
        The processed image, as scaled and sharpened grayscale and fully
        processed binary image.
    """
    if rescale_image:
        scale = constants._TARGET_DPI / grayscale.shape[1] * (80 / 25.4)
        proc_img = rescale(grayscale, scale)

    if not any(param is None for param in unsharp_ma):
        proc_img = unsharp_mask(proc_img, radius=unsharp_ma[0], amount=unsharp_ma[1])

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


def detect_rotation(image):
    """
    Placeholder for an auto rotate function which is a ToDo.

    Parameters
    ----------
    image : `ndarray`
        Input image
    """
    ...
