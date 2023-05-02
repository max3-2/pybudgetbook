# pybudgetbook

Organize and sort your receipts locally, use pandas power to analyze your
spendings!
But why? There are tons of Apps out there scanning and even some for receipts.


TODO note that each part works by his own and describe parts

Also, the core ideas are:
<u>Reason 1: Data Privacy</u>

Your receipts combined with some personal data are a pretty good estimator on
where you are and what you are doing. I prefer to keep that data locally. This
software will access any of that data since it runs locally.

<u>Reason 2: Adaptability</u>

Receipts differ for region and even for supermarket. Here, some of the more
common german stores are included. If something does not work, add your own
reader / parser!

<u>Reason 3: Data Analysis</u>

The data is saved in `hdf`-files for `pandas` and can be easily exported to
`csv` or any other format manually. So analysis is not limited to simple plots
over time (even though the initial version does just that. Feel free to add
ideas and improvements!)

Uses some icons from [Yusuke Kamiyamane](http://p.yusukekamiyamane.com/)

## Current State of Functionality and Roadmap

- Prepare receipt images for `tesseract`
- Parse receipts from german supermarkets and read items
- Correct items, add important metadata
- Save items it a dedicated folder
- Generate most basic analysis
- Export data

Future

- More types of receipts
- More languages
- Better analysis tools
- Continous UX improvements


## Tutorial
To get started, you will need a receipt from a supermarket. A main criterion in
the current state is that the items have a price with a tax class connected,
usually an **A**, **B**, **1** or a **2** trailing the price. This should be the
case for most german receipts. Other languages might differ but are not in
scope yet.

Take an image from the receipt as flat as possible, including all from the
header (for supermarket identification) to at least the total. JPEG is fine,
iPhones are fine. Lateral crop to the receipt borders. Straighten / Rotate to
make the text horizontal. This all takes a minute on any modern phone.

ToDo Start he UI and load the receipt

TODO Manual corrections, e.g. chaning amount if bulk packages are bought

## More Informations
### Good Scans / Images
- Have your receipt as flat as possible against a darker background.
- Images are scaled to 600dpi **assuming a basic receipt width of 75mm**. This
  is an option which might needs adaption. Scale is important for `tesseract`
  and also for some types of identification where a logo is matched.
- Try to apply a lateral Crop fairly close at the receipt borders. Rotate to
  have the text horizontal.

### Grouping
Categrorizing searches language specific (currently only german) dicts which
are consecutively improved from data (if you want to help, see below). Tagging
your articles will improve matching. You can always create your own language
specific dicts following a fairly simple `json` syntax for a dict with keys
being groups and the values being list of case-insensitive patterns. Feel free
to create issues / gists with your local dicts so I can merge them in.
Best practice:
- Base dataset dicts are delivered for some languages with the package and
  updated from time to time with package updates.
- A User data dict with the same syntax is kept in the data folder and is
  updated with your data.
- On load, those will be combined (exclusive set())
- Explain negative groups

## Improving
If you want, you can help to improve! Code improvement and bug fixes are
welcome. Additionally, classification is based on brute force and needs more
data. There are different options with some drawbacks (mainly reason 1: Privacy)
to partake:
- ToDo
- ToDo

## Issues
### The receipt is not detected or the information is not parsed correctly
Check the following step by step. If you need more information on where to look,
run the functions and analyze the output without the UI (see also under the
hood)
- Check orientation
- Check image crop
- Check filter result (text legible?)
- Check detected supermarket
- Check unfiltered base string data (see UI menu ToDo)
- Check retrieved data

### Still not detected?
- If your receipt type **is supported** and your **base text** is recognized
  but not parsed, create an issue.
- If your **receipt type is not supported** and your **base text is**
  recognized but not parsed, create a PR asking for the new receipt type. If
  you do not have the capabilities for a PR, create an issue and support the
  receipt image and additional information (the more receipts of a type,
  the better!)
- If your **base text** is not recognized, you need to adapt filtering
  parameters. Check filtered output and use the API to improve (UI
  not supported). If there are better parameters, let me know via issues or PR!

## API Usage
ToDO

## Under the hood
1. Images are scaled, (rotated, ) filtered
2. Text extraction using OCR by `tesseract`
3. Vendor detection by either
   1. Text search for a known vendor
   2. Logo detection: Logo is filtered and pattern matched in the receipt
4. Regexp based text analysis with receipt specific patterns (optional) and /
   or best fit for all patterns
5. Sort and post-process data in DataFrame, display data

## Drawbacks
- Relies on a "valid" price, at least for the current state and the supported
  types of german receipts. A valid price is a price that is followed by
  `[A,B,1,2]` for Tax Class (which is the default in Germany). Not the case for
  you? **Create a new receipt type!** Caveat: Find a new way to identify a
  single valid article.
