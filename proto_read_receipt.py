"""
@author: Max
@date: 2023-04-07

Prototyping the receipt recognition
"""
from pathlib import Path
import pytesseract as ocr
from skimage.color import rgb2gray
from skimage import io as skio
from skimage.filters import threshold_otsu
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import re
import pandas as pd

# TODO Rotation is the most important factor to get a good ocr!
def rot_event(act_ax, event):
    if event.inaxes is act_ax:
        if event.key == 'right':
            print('rot right')
        elif event.key == 'left':
            print('rot left')
        elif event.key == 'shift+right':
            print('rot right much')
        elif event.key == 'shift+left':
            print('rot left much')
        else:
            return


price_pattern_eu = r'(\d{1,3},\d{2})'
price_with_class = r'(\d{1,3},\d{2}_[AB12])'
mult_pattern_eu = r'((?<=[xX*]_)\d{1,3},\d{2})'  # r'[xX]{1}'
weight_pattern_eu = r'(\d{1,3},\d{1,3}(?=_EUR\/kg))'
amount_in_weight_eu = r'(\b\d{1,2},\d{1,3})'
total_sum_pattern_eu = (r'(((?<=total.)\d{1,3},\d{2})|'
                        r'((?<=betrag.)\d{1,3},\d{2})|'
                        r'((?<=summe.)\d{1,3},\d{2}))')

valid_article_pattern = r'(.*?(?=' + price_pattern_eu + '))'

# TODO Add compile for regexp in loops!

receipts = [Path(f) for f in [
    r'examples/IMG_5991.JPG',
    r'examples/IMG_6005.JPG',
    r'examples/IMG_6006.JPG'
]]

# for rec in receipts:
rec = receipts[2]

image = rgb2gray(skio.imread(rec))
thresh = threshold_otsu(image)
binary = image > thresh

data = ocr.image_to_data(binary, lang='deu', output_type='data.frame').dropna(
    subset=['text']).reset_index()

# First item is usually first price, if not let it 0 so get everything
first_item = 0
first_item = data['text'].str.extract(
    '(' + price_pattern_eu + ')').first_valid_index()

# Move tis to beginning of line so to catch all on this line if price
# is not the first item
first_item = data.loc[(data['block_num'] == data.loc[first_item, 'block_num']) & (
    data['line_num'] == data.loc[first_item, 'line_num'])].first_valid_index()


fig, ax = plt.subplots(1, 2, sharex=True, sharey=True, constrained_layout=True)
_ = ax[0].grid()
_ = ax[1].grid()
ax[0].imshow(image, cmap='gray')
ax[1].imshow(binary, cmap='gray')
# cid = fig.canvas.mpl_connect(
#     'key_press_event', lambda event: rot_event(ax[1], event))

# This will hold a list of tuples with valid data, where the elements are
# article number, name, units, price per unit, total
retrieved_data = pd.DataFrame(
    columns=['ArtNr', 'Name', 'Units', 'PricePerUnit', 'Price', 'TaxClass'])
this_row_exists = False

# Parse line by line and see what can be classified
for line, group in data.loc[first_item:, :].groupby('line_num'):
    has_price, has_weight, has_mult = False, False, False

    # Smash the line and regexp to victory
    this_line = '_'.join(group.text.str.strip())
    print('Analyzing: ', this_line)

    # These need to be ordered and aligned into the final data, lets start...
    # Is there a price with tax class?
    if (re_res := re.search(price_with_class, this_line)) is not None:
        price, tax_class = re_res.group(0).split('_')

        # TODO add trz except and set to 0 if parse fails
        price = float(price.replace(',', '.'))
        tax_class = int(tax_class.upper().replace('A', '1').replace('B', '2'))
        has_price = True
        print('Normal item: ', this_line, price, tax_class)

    # Is there a kg price, e.g. weight multiplier (then skip normal mult.)
    if (re_res := re.search(weight_pattern_eu, this_line)) is not None:
        price_per_unit = float(re_res.group(0).replace(',', '.'))
        amount = float(
            re.search(amount_in_weight_eu, this_line).group(0).replace(',', '.'))
        has_weight = True
        print('Found weight: ', amount, price_per_unit)

    # Is there a multiplier
    elif (re_res := re.search(mult_pattern_eu, this_line)) is not None:
        price_per_unit = float(re_res.group(0).replace(',', '.'))
        has_mult = True
        print('Found mult: ', price_per_unit)

    # Analysis done, now extract and sort the data
    # Has mult (before item): pre-create row and set flag
    if has_mult and not has_price:
        retrieved_data = pd.concat(
            [retrieved_data, pd.DataFrame({
                'PricePerUnit': price_per_unit,
            }, index=[0])],
            ignore_index=True)
        this_row_exists = True

    # Found weight but no price with tax class: Lookbehind and assemble
    if has_weight and not has_price:
        retrieved_data.loc[retrieved_data.index[-1], ['Units', 'PricePerUnit']] = [amount, price_per_unit]

    # TODO with weight before the article, see nahkauf

    # If this has a price then try to extract the name, a possible article id,
    # creating a new item
    if has_price and not (has_mult or has_weight):
        article_data = re.match(valid_article_pattern, this_line).group(0).split('_')
        if (re_res := re.match(r'\d{1,}', article_data[0])) is not None:
            article_number = int(re_res.group(0))
            article_name = ' '.join(article_data[1:]).strip()
        else:
            article_number = -1
            article_name = ' '.join(article_data).strip()
        print('Final: ', article_number, article_name)

        if this_row_exists:
            retrieved_data.loc[retrieved_data.index[-1],
                               ['ArtNr', 'Name', 'Price', 'TaxClass']] = [
                                   article_number, article_name, price, tax_class]
            this_row_exists = False
        else:
            retrieved_data = pd.concat(
                [retrieved_data, pd.DataFrame({
                    'ArtNr': article_number,
                    'Name': article_name,
                    'Price': price,
                    'TaxClass': tax_class
                }, index=[0])],
                ignore_index=True)

    # Heavy lifting done, now just plot and get total
    # Plot box if this line is a valid price around the full line
    if has_price:
        box_xy = (group['left'].min(), group['top'].min())
        box_height = (group['height'] + group['top']).max() - box_xy[1]
        box_width = (group['width'] + group['left']).max() - box_xy[0]
        text_rec = Rectangle(box_xy, box_width, box_height,
                             ec='green', fc='none', lw=0.3)

        ax[0].add_patch(text_rec)

    # Is there a final price? If so break the loop
    elif (re_res := re.search(total_sum_pattern_eu, this_line, re.IGNORECASE)) is not None:
        total_price = float(re_res.group(0).replace(',', '.'))
        print('Found total price: ', total_price)
        break

    print(20 * '-')

# Post process
retrieved_data['Units'] = retrieved_data['Units'].fillna(1)
ppu_nan = retrieved_data['PricePerUnit'].isna()
retrieved_data.loc[ppu_nan, 'PricePerUnit'] = (retrieved_data.loc[ppu_nan, 'Price'] /
                                               retrieved_data.loc[ppu_nan, 'Units'])
