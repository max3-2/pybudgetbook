"""Receipt class to handle a receipt with filtering and parsing"""
import logging
from pathlib import Path
import imghdr

import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

import pytesseract as ocr
import pypdfium2 as pdfium
from skimage.color import rgb2gray
from skimage.transform import rotate

from . import image_filters
from .configs import config
from .configs import constants
from . import parsers


logger = logging.getLogger(__package__)


def _type_check(retrieved_data):
    """Ensures that the data type in each view column is correct"""
    try:
        retrieved_data = retrieved_data.astype(
            {'PricePerUnit': 'float', 'Price': 'float', 'TaxClass': 'int', 'ArtNr': 'int', 'Units': 'float'})
    except ValueError:
        logger.warning('Using float instead of int in some cols due to NaN are left')
        retrieved_data = retrieved_data.astype(
            {'PricePerUnit': 'float', 'Price': 'float', 'TaxClass': 'float', 'ArtNr': 'int', 'Units': 'float'})
    return retrieved_data


class _BaseReceipt():
    """
    Base Receipt holds methods and attributes that are valid for either a pdf
    or an image based receipt. Should not be called directly!
    """
    def __init__(self):
        self._type = None
        self._gs_image = None
        self._data_extracted = False
        self._raw_text = ''
        self._data = None
        self._lang = 'deu'

        self._vendor = None
        self._patident = None
        self._patset = None
        self._fig = None
        self.disp_ax = None

    @property
    def raw_text(self):
        """Raw extracted text from the receipt"""
        if self._data_extracted:
            return self._raw_text
        else:
            logger.warning('No valid data extracted (yet)')
            return None

    @property
    def type(self):
        """Receipt type, image or pdf"""
        return self._type

    @property
    def valid_data(self):
        """Returns if data has been extracted from the receipt"""
        if self._data_extracted:
            return self._data
        else:
            logger.warning('No valid data extracted (yet)')
            return None

    @property
    def parsing_patterns(self):
        """Returns the current set of regexp parsing patterns"""
        return self._patset

    @property
    def vendor(self):
        """Returns vendor"""
        return self._vendor

    # Template to allow chaining if receipt type not known beforehand
    def filter_image(self, **kwargs):
        """Template, dont use directly"""
        return self

    def _create_figure(self):
        """Figure convenience function for high level use"""
        self._fig, self._ax = plt.subplots(1, 2, sharex=True, sharey=True)

    def parse_vendor(self, lang=config.options['lang']):
        """
        Tries to extract the vendor from the receipt. Call this after
        extract_data to get a meaningful result
        """
        self._vendor, self._patident = parsers.get_vendor(self.raw_text)
        if self._vendor == 'General':
            logger.warning(
                'No vendor found, set to General. Please add for best '
                'parsing results using Receipt.set_vendor')

        return self.set_vendor(self._vendor, lang)

    def set_vendor(self, vendor, lang=config.options['lang']):
        """Manually set vendor if auto detect failed"""
        self._vendor = vendor
        self._patident = config.receipt_types.get(self._vendor, 'gen')
        self._patset = parsers.get_patterns(self._patident, lang)
        self._lang = lang
        return self._vendor

    def parse_data(self, fill=True):
        """
        Parses extracted data into articles and prices - this is where the most
        complicated functions are being called!

        Parameters
        ----------
        fill : `bool`
            Fill missing and nans with some basic math. Defaults to `True`.
        """
        if not self._data_extracted:
            logger.info('Please extract data first')
            return None

        if self.vendor is None:
            logger.info('Please set a vendor first')
            return None

        logger.debug(f'Parsing with patident {self._patident} and lang {self._lang}')
        parsing_func = parsers.select_parser(self._patident, lang=self._lang)

        retrieved_data, total_price = parsing_func(
            self.valid_data, self._patset, self._patident, self.disp_ax)

        # Fill
        if fill:
            retrieved_data = parsers.fill_missing_data(retrieved_data)

        # Type check
        retrieved_data = _type_check(retrieved_data)

        # Tax Class corrections
        if self.vendor in config.needs_tax_switch.keys():
            sw_a, sw_b = config.needs_tax_switch[self.vendor]
            logger.info(f'Switching Tax Classes {sw_a} and {sw_b}')
            retrieved_data = parsers._flip_tax_class(
                retrieved_data, sw_a, sw_b)

        return retrieved_data, total_price

    def parse_date(self):
        """Retrieves date from raw text. Call after extract_data"""
        if 'date_pattern' in self._patset:
            date = parsers.get_date(self._raw_text, self._patset['date_pattern'])
        else:
            logger.warning('No date matching pattern available')
            date = None

        return date


class ImgReceipt(_BaseReceipt):
    """
    A receipt based on an image, this could be used solo but is wrapped in a
    user class for handling all types of receipts
    """

    def __init__(self, filepath):
        _BaseReceipt.__init__(self)
        self._type = 'img'
        self._file = None
        self.file = filepath

        self._rotation = 0
        self._has_rotation = False

        self._is_filtered = False

        self._proc_img = None
        self._bin_img = None

    @property
    def file(self):
        """Holds the file path of the underlying image file"""
        return self._file

    @file.setter
    def file(self, filepath):
        filepath = Path(filepath)
        if not filepath.is_file() or not filepath.exists() or imghdr.what(filepath) is None:
            error = 'File does not exist or no valid image'
            logger.error(error)
            raise FileNotFoundError(error)

        self._file = filepath
        self._gs_image = image_filters.load_image(self._file)

        # Reset
        self._proc_img = None
        self._rotation = 0
        self._has_rotation = False
        self._is_filtered = False
        self._patset = None

    @property
    def rotation(self):
        """Returns current image rotation"""
        if not self._has_rotation:
            return None
        return self._rotation

    @rotation.setter
    def rotation(self, inc):
        self._rotation += inc
        self._has_rotation = True

        if self._rotation == 0:
            self._has_rotation + False

    @property
    def valid_filter(self):
        """Returns the state of the image filter"""
        return self._is_filtered

    @property
    def image(self):
        """Returns the original (rescaled) image"""
        if not self._is_filtered:
            logger.warning('Image is not filtered - using base grayscale')
            ref_img = self._gs_image
        else:
            ref_img = self._proc_img

        if self._has_rotation:
            return rotate(ref_img, self._rotation, resize=True)
        else:
            return ref_img

    @property
    def bin_img(self):
        """Returns the binary filtered image if available"""
        if not self._is_filtered:
            error = 'Binary image is not filtered yet'
            logger.error(error)
            raise RuntimeError(error)

        if self._has_rotation:
            return rotate(self._bin_img, self._rotation, resize=True)
        else:
            return self._bin_img

    def filter_image(self, **kwargs):
        """
        Filters the receipt using the filter function defined in library. Any
        kwargs are passed to `image_filters.preprocess_image()` so look there
        for more information."""
        self._proc_img, self._bin_img = image_filters.preprocess_image(
            self._gs_image, **kwargs)
        self._is_filtered = True
        if self._fig is not None:
            self.disp_ax = self._fig.axes[0]

        # Chaining support
        return self

    def show_receipt(self):
        """Creates a plot with the receipt and its filtered view"""
        if not self.valid_filter:
            logger.warning('Please filter first')
            return

        self._create_figure()
        self._ax[0].imshow(self.image)
        self._ax[1].imshow(self.bin_img)
        self.disp_ax = self._ax[0]

        # Chaining support
        return self

    def extract_data(self, lang=config.options['lang']):
        """
        Extracts text **and** converts to dataframe. Uses tesseract as backend
        with the given language.

        Parameters
        ----------
        lang : `str`, optional
            tesseract base language for text extraction, by default the
            current default value from the config file.

        Returns
        -------
        self ; `Receipt`
            Self for chaining support
        """
        tess_in = Image.fromarray(self.bin_img.astype(bool))
        tess_in.format = 'TIFF'
        logger.debug(f'Tesseract with lang: {lang}')
        try:
            data = ocr.image_to_data(tess_in, lang=lang, output_type='data.frame',
                                     config=constants._TESS_OPTIONS).dropna(
                subset=['text']).reset_index()
        except (ocr.TesseractError, ocr.TesseractNotFoundError) as tess_e:
            logger.exception(
                'Tesseract nor found or failure. This has to be '
                f'resolved on system level: {tess_e}')
            return self

        data['height_plus_top'] = data['height'] + data['top']
        data['width_plus_left'] = data['width'] + data['left']

        # Collapse into single lines
        data_by_line = data.groupby('line_num')
        data_combined = pd.concat((
            data_by_line['text'].apply('_'.join),
            data_by_line['top'].min(),
            data_by_line['left'].min(),
            data_by_line['height_plus_top'].max(),
            data_by_line['width_plus_left'].max()),
            axis=1).reset_index()

        # Make BBox format for MPL
        data_combined['width'] = data_combined['width_plus_left'] - data_combined['left']
        data_combined['height'] = data_combined['height_plus_top'] - data_combined['top']
        data_combined.drop(['height_plus_top', 'width_plus_left'], axis=1)

        # Re-Get raw text instead of tesseract twice
        self._raw_text = '\n'.join(data_combined.text)
        self._data = data_combined
        self._data_extracted = True

        # Chaining support
        return self

    def reset_rotation(self):
        """Resets current rotation"""
        self._rotation = 0
        self._has_rotation = False


class PdfReceipt(_BaseReceipt):
    """
    A Receipt based on a pdf. This **must** contain valid text and not just
    images. Currenly, only single page is supported with page 1 being parsed!
    """
    def __init__(self, filepath):
        _BaseReceipt.__init__(self)
        self._type = 'pdf'
        self._file = None
        self.file = filepath

    @property
    def file(self):
        """Holds the file apth of the underlying pdf file"""
        return self._file

    @file.setter
    def file(self, filepath):
        filepath = Path(filepath)
        if not filepath.is_file() or not filepath.exists() or not filepath.suffix == '.pdf':
            error = 'File does not exist or no valid PDF'
            logger.error(error)
            raise FileNotFoundError(error)

        self._file = filepath
        self._gs_image = None
        self._data_extracted = False

    @property
    def image(self):
        """
        Provides a simple image for plotting extracted from the pdf. Only use
        this for plotting purposes!"""
        if not self._data_extracted:
            error = 'Image is not extracted yet'
            logger.error(error)
            raise RuntimeError(error)
        else:
            return self._gs_image

    def show_receipt(self):
        """Helper function to diplay the extracted image"""
        if not self._data_extracted:
            logger.warning('Please extract data first')
            return

        self._create_figure()
        self._ax[0].imshow(self.image)
        self.disp_ax = self._ax[0]

        return self

    def extract_data(self, page=0, lang=None):
        """
        Extracts text **and** converts to dataframe. lang is unused here in
        case of pdf and is solely used for standardization of function
        signatures.

        Parameters
        ----------
        page : `int`, optional
            Page to parse, by default 0
        lang : `str`, optional
            Placeholder, by default None

        Returns
        -------
        self ; `Receipt`
            Self for chaining support
        """
        # Split line-wise
        pdf = pdfium.PdfDocument(self._file)
        pagedata = pdf.get_page(page)
        txt = pagedata.get_textpage().get_text_range().split('\n')

        txt = [line.strip() for line in txt if line.strip()]

        # Remove  many spaces, dont need the layout
        txt = [' '.join(line.split()) for line in txt]
        # Spaces to underscore, better visibility
        txt = [line.replace(' ', '_') for line in txt]

        # Create raw and parse the rest into the DataFrame format which is used
        # in the main text parser
        raw_text = '\n'.join(txt)

        data = pd.DataFrame(columns=['line_num', 'text'])
        data['text'] = txt
        data['line_num'] = [i + 1 for i in range(len(txt))]

        scale = constants._TARGET_DPI / pagedata.get_width() * (80 / 25.4)
        ref_img = rgb2gray(pagedata.render(scale=scale).to_numpy())

        # Text BB
        txtpage = pagedata.get_textpage()
        rects = np.array([txtpage.get_rect(i) for i in range(txtpage.count_rects())])
        # Now this is left, bottom, right and top in pdf, so scale, invert y
        # and convert for MPL
        # TODO make this better right now just catch if rects are messed up
        if rects.shape[0] != data.shape[0]:
            logger.warning('Invalid text BBox data in PDF, skipping rects...')
            data['left'] = 0
            data['top'] = 0
            data['width'] = 0
            data['height'] = 0
        else:
            data['left'] = rects[:, 0] * scale
            data['top'] = ref_img.shape[0] - rects[:, 3] * scale
            data['width'] = (rects[:, 2] - rects[:, 0]) * scale
            data['height'] = (rects[:, 3] - rects[:, 1]) * scale

        self._data = data
        self._raw_text = raw_text
        self._gs_image = ref_img
        self._data_extracted = True

        return self


def Receipt(file):
    """
    The main wrapper function that calls an init from a specific base class
    and then provides all needed methods.

    Parameters
    ----------
    file : `Path`
        Receipt image or pdf path.

    Returns
    -------
    Receipt : `Receipt`
        The receipt class instance

    Raises
    ------
    FileNotFoundError
    IOError
    """
    file = Path(file)
    if not file.is_file() or not file.exists():
        error = 'File does not exist'
        logger.error(error)
        raise FileNotFoundError(error)

    if imghdr.what(file) is not None:
        logger.debug('Creating Image based receipt')
        return ImgReceipt(file)

    elif file.suffix == '.pdf':
        logger.debug('Creating PDF based receipt')
        return PdfReceipt(file)

    else:
        raise IOError('Only image files and pdf are supported!')
