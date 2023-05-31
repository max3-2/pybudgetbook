# pybudgetbook
Organize and sort your receipts locally, use pandas power to analyze your
expenses!
But why? There are tons of Apps out there scanning and even some for receipts.
Some of them might even be more general or better at parsing. Sure, but here are
the core reasons why I built this app. If they are important to you, give it a
try (and help to support more receipts)!

**Reason 1: Data Privacy**

Your receipts combined with some personal data are a pretty good estimator on
where you are and what you are doing. I prefer to keep that data locally. This
software will never *access and send* any of that data since it runs locally.

**Reason 2: Adaptability**

Receipts differ for region and even for supermarkets. Here, some of the more
common german stores are included. If something does not work, add your own
reader / parser!

**Reason 3: Data Analysis**

The data is saved in `hdf`-files for `pandas` and can be easily exported to
`csv` or any other format manually. So analysis is not limited to the few plots
available (even though the initial version has some important ones). You can
easily load all your data using a simple one-liner and run all the analysis you
want. If you find anything particular useful, let me know and I can implement
that.

Full Readme and Code on Github!

Uses some icons from [Yusuke Kamiyamane](http://p.yusukekamiyamane.com/)

Some emojis / icons designed by OpenMoji – the open-source emoji and icon
project. License: CC BY-SA 4.0