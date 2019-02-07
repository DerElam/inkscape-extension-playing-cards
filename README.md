# An Inkscape Extension to Create Templates for Playing Cards

## Overview

This Inkscape extension creates templates for playing cards. It lets you define:
- the width and height of the cards,
- an optional bleed for the cards,
- an optional horizontal or vertical fold line,
- a minimal distance between the cards,
- a minimal distance between the cards and the fold line,
- an optional page margin, and
- an optional alignment grid.

The following image shows an example template for 2.5in x 3.5in cards on A4
paper in landscape format. The template has a horizontal folding line with at
least 5mm space between the line and the cards. Each card has a bleed of
2mm. The page has a empty margin of 5mm. The bottom left corners of each card
is aligned to a 5mm grid (although the card sizes are defined in inches). Crop
marks for each card extend from the page border to the bleed area and between
between bleed areas.

![An image of typical output of the extension](https://github.com/DerElam/inkscape-extension-playing-cards/blob/master/images/ex_output.png)

## Installation

Download the two files *PlayingCards.inx* and *PlayingCards.py*. Copy these
files to your Inkscape extension folder. To find the location of that folder
open the Inkscape preferences dialog (menu *Edit/Preferences*) and look at
*System/System info/User extensions*.

You must restart Inkscape after copying the files to your Inkscape extension 
folder. There should now be a menu item called 
*Extensions/Boardgames/Playing Cards...*. This opens the settings window for the
extension.

## Settings

### Cards

![An image of the settings window showing the cards tab](https://github.com/DerElam/inkscape-extension-playing-cards/blob/master/images/settings_cards.png)

Here you can define the width and height of your cards and also the width of
the bleed area around the cards. Make sure that the right units are selected.

### Margins

![An image of the settings window showing the margins tab](https://github.com/DerElam/inkscape-extension-playing-cards/blob/master/images/settings_margins.png)

Here you can define several different empty areas on your page. You can enter
the minimal desired values, but the actual values might be larger depending
on the values for the bleed size and the alignment grid.

### Fold line

![An image of the settings window showing the fold lines tab](https://github.com/DerElam/inkscape-extension-playing-cards/blob/master/images/settings_foldline.png)

Here you can define whether or not you want a horizontal or vertical fold
line or no fold line at all. A fold line is usefull if you want to have the
fronts and backs of the cards on one page. This lets you match the fronts and
backs of the cards perfectly while glueing them together.

### Alignment

![An image of the settings window showing the alignment tab](https://github.com/DerElam/inkscape-extension-playing-cards/blob/master/images/settings_alignment.png)

If *Align cards to grid* is enabled the lower left corner of each card is put on
a grid point as defined by *Grid spacing*. This grid might be different from 
you document grid.

The purpose of the grid alignment is that it allows you to easily copy items
between cards even if the units of the cards and the document don't match.

For example: You are used to metric units and your document is set up to use
millimeters. When you design cards of size 2.5in x 3.5in with a bleed of 2mm
and you want to copy items from one card to the card above it you would have
to somehow move the item by 92.9mm (88.9mm for the card and 2x2mm for the
bleed areas). This is inconvenient. But if you enable the grid alignment with
a grid size of say 10mm, then the cards are placed such that you can move
your items up by 100mm. This is easily done with the arrow keys.
