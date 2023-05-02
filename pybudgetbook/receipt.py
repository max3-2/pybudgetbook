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

# TODO make rel
from pybudgetbook import image_filters
import pybudgetbook.config.constants as bbconstants
import pybudgetbook.config.config as bbconfig
from pybudgetbook import parsers

logger = logging.getLogger(__package__)


class _BaseReceipt():

    def __init__(self):
        self._type = None
        self._gs_image = None
        self._data_extracted = False
        self._raw_text = ''
        self._data = None

        self._vendor = None
        self._patident = None
        self._patset = None
        self._fig = None
        self.disp_ax = None

    # Get but no manual set
    @property
    def raw_text(self):
        if self._data_extracted:
            return self._raw_text
        else:
            logger.warning('No valid data extracted (yet)')
            return None

    @property
    def type(self):
        return self._type

    @property
    def valid_data(self):
        if self._data_extracted:
            return self._data
        else:
            logger.warning('No valid data extracted (yet)')
            return None

    @property
    def parsing_patterns(self):
        return self._patset

    @property
    def vendor(self):
        return self._vendor

    # Template to allow chaining if receipt type not known beforehand
    def filter_image(self, **kwargs):
        return self

    def _create_figure(self):
        self._fig, self._ax = plt.subplots(1, 2, sharex=True, sharey=True)

    def parse_vendor(self, lang=bbconfig.options['lang']):
        self._vendor, self._patident = parsers.get_vendor(self.raw_text)
        if self._vendor == 'General':
            logger.warning(
                'No vendor found, set to General. Please add for best '
                'parsing results using Receipt.set_vendor')

        self._patset = parsers.get_patterns(self._patident, lang)

        return self._vendor

    def set_vendor(self, vendor, lang=bbconfig.options['lang']):
        self._vendor = vendor
        self._patident = bbconfig.receipt_types.get(self._vendor, 'gen')

        self._patset = parsers.get_patterns(self._patident, lang)

        return self._vendor

    def parse_data(self, fill=True):
        if not self._data_extracted:
            logger.info('Please extract data first')
            return None

        if self.vendor is None:
            logger.info('Please set a vendor first')
            return None

        parsing_func = parsers.select_parser(self._patident)

        retrieved_data, total_price = parsing_func(
            self.valid_data, self._patset, self._patident, self.disp_ax)

        # Type check
        retrieved_data = retrieved_data.astype(
            {'PricePerUnit': 'float', 'Price': 'float', 'TaxClass': 'int', 'ArtNr': 'int'})

        if fill:
            return parsers.fill_missing_data(retrieved_data), total_price
        else:
            return retrieved_data, total_price

    def parse_date(self):
        if 'date_pattern' in self._patset:
            date = parsers.get_date(self._raw_text, self._patset['date_pattern'])
        else:
            print('Warn: No date matching pattern')
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

    # Get but no manual set - use the functions (TODO)
    @property
    def rotation(self):
        if not self._has_rotation:
            return None
        return self._rotation

    @property
    def valid_filter(self):
        return self._is_filtered

    @property
    def image(self):
        if not self._is_filtered:
            logger.warning('Image is not filtered - using base grayscale')
            return self._gs_image
        else:
            return self._proc_img

    @property
    def bin_img(self):
        if not self._is_filtered:
            error = 'Binary image is not filtered yet'
            logger.error(error)
            raise RuntimeError(error)

        return self._bin_img

    def filter_image(self, **kwargs):
        self._proc_img, self._bin_img = image_filters.preprocess_image(
            self._gs_image, **kwargs)
        self._is_filtered = True
        if self._fig is not None:
            self.disp_ax = self._fig.axes[0]

        # Chaining support
        return self

    def show_receipt(self):
        if not self.valid_filter:
            logger.warning('Please filter first')
            return

        self._create_figure()
        self._ax[0].imshow(self.image)
        self._ax[1].imshow(self.bin_img)
        self.disp_ax = self._ax[0]

        # Chaining support
        return self

    def extract_data(self, lang=bbconfig.options['lang']):
        """Extracts text **and** converts to data"""
        tess_in = Image.fromarray(self.bin_img)
        tess_in.format = 'TIFF'
        try:
            data = ocr.image_to_data(tess_in, lang=lang, output_type='data.frame',
                                     config=bbconstants._TESS_OPTIONS).dropna(
                subset=['text']).reset_index()
        except (ocr.TesseractError, ocr.TesseractNotFoundError) as tess_e:
            # TODO Sub packages log wrong this might be resolved with package build
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


class PdfReceipt(_BaseReceipt):
    """
    A receipt based on a pdf with text, this could be used solo but is wrapped
    in a user class for handling all types of receipts
    """

    def __init__(self, filepath):
        _BaseReceipt.__init__(self)
        self._type = 'pdf'
        self._file = None
        self.file = filepath

    @property
    def file(self):
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
        if not self._data_extracted:
            error = 'Image is not extracted yet'
            logger.error(error)
            raise RuntimeError(error)
        else:
            return self._gs_image

    def show_receipt(self):
        if not self._data_extracted:
            logger.warning('Please extract data first')
            return

        self._create_figure()
        self._ax[0].imshow(self.image)
        self.disp_ax = self._ax[0]

        return self

    def extract_data(self, page=0, show=False):
        """Extracts text **and** converts to data"""
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

        scale = bbconstants._TARGET_DPI / pagedata.get_width() * (80 / 25.4)
        ref_img = rgb2gray(pagedata.render(scale=scale).to_numpy())

        # Text BB
        txtpage = pagedata.get_textpage()
        rects = np.array([txtpage.get_rect(i) for i in range(txtpage.count_rects())])
        # Now this is left, bottom, right and top in pdf, so scale, invert y
        # and convert for MPL
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
    """
    file = Path(file)
    if not file.is_file() or not file.exists():
        error = 'File does not exist'
        logger.error(error)
        raise FileNotFoundError(error)

    if imghdr.what(file) is not None:
        return ImgReceipt(file)

    elif file.suffix == '.pdf':
        return PdfReceipt(file)

    else:
        raise IOError('Only image files and pdf are supported!')
