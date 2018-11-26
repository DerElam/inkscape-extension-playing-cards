import inkex
import simplestyle
from math import ceil, floor

UNITS = {
    "in": 72.0,
    "cm": 72.0 / 2.54,
    "mm": 72.0 / 25.4
}

EPSILON = 1e-3

NO_FOLD_LINE = "NoFoldLine"
HORIZONTAL_FOLD_LINE = "HorizontalFoldLine"
VERTICAL_FOLD_LINE = "VerticalFoldLine"
FOLD_LINE_TYPES = [NO_FOLD_LINE, HORIZONTAL_FOLD_LINE, VERTICAL_FOLD_LINE]


def roundUp(value, gridSize):
    return ceil(value / gridSize - EPSILON) * gridSize


def roundDown(value, gridSize):
    return floor(value / gridSize + EPSILON) * gridSize


def mirrorAbout(value, about):
    return 2.0 * about - value


def calculatePositionsWithoutFoldLine(pageSize, marginSize, cardSize,
                                      bleedSize, gridSize, minSpacing,
                                      gridAligned):
    # First card
    cardBegin = marginSize + bleedSize
    if gridAligned:
        cardBegin = roundUp(cardBegin, gridSize)
    cardEnd = cardBegin + cardSize

    # Space between cards
    spacing = max(minSpacing, 2.0 * bleedSize)
    if gridAligned:
        spacing = roundUp(cardEnd + spacing, gridSize) - cardEnd

    # Add cards until a bleed is beyond the page margin
    cards = []
    remaining = 0
    while True:
        cardEnd = cardBegin + cardSize
        nextRemaining = pageSize - marginSize - cardEnd - bleedSize
        if nextRemaining < 0:
            break
        remaining = nextRemaining
        cards.append(cardBegin)
        cardBegin = cardEnd + spacing

    # Shift everything towards the center
    shift = remaining / 2.0
    if gridAligned:
        shift = roundDown(shift, gridSize)

    for i in range(len(cards)):
        cards[i] += shift

    return cards


def calculatePositionsWithFoldLine(pageSize, marginSize, cardSize,
                                   bleedSize, gridSize, minSpacing,
                                   minFoldLineSpacing, gridAligned):
    # Space between the two cards at the fold line
    centralSpacing = max(2.0 * minFoldLineSpacing,
                         max(minSpacing, 2.0 * bleedSize))

    # First card before the fold line
    cardBegin = (pageSize - centralSpacing) / 2.0 - cardSize
    if gridAligned:
        cardBegin = roundDown(cardBegin, gridSize)
    cardEnd = cardBegin + cardSize

    # Adjust the spacing between the two cards at the fold line so that both
    # central cards are aligned to the grid
    if gridAligned:
        centralSpacing = roundUp(cardEnd + centralSpacing, gridSize) - cardEnd

    # Fold line is centered between the two central cards
    foldLine = cardEnd + centralSpacing / 2.0

    # Spacing between the non-central cards
    spacing = max(minSpacing, 2.0 * bleedSize)
    if gridAligned:
        spacing = roundUp(cardEnd + spacing, gridSize) - cardEnd

    # Add cards to both sides of the fold line until a bleed is beyond the page
    # margin
    cards = []
    while True:
        if cardBegin < marginSize:
            break
        cards.append(cardBegin)
        cards.append(mirrorAbout(cardEnd, foldLine))
        cardBegin -= cardSize + spacing
        cardEnd = cardBegin + cardSize

    # Sort the positions because right now the positions alternate between the
    # left and right side of the fold line
    cards.sort()

    return (cards, foldLine)


class PlayingCardsExtension(inkex.Effect):

    def __init__(self):
        inkex.Effect.__init__(self)

        self.pageWidth = None
        self.pageHeight = None
        self.cardWidth = None
        self.cardHeight = None
        self.bleedSize = None
        self.minCardSpacing = None
        self.minFoldSpacing = None
        self.pageMargin = None
        self.gridSize = None
        self.gridAligned = None
        self.foldLineType = None

        self.horizontalCardPositions = None
        self.verticalCardPositions = None
        self.foldLinePosition = None

        self.addOptions()

    def addOptions(self):
        self.OptionParser.add_option("--pageName", type="string")

        self.OptionParser.add_option(
            "--cardWidth", type="float", action="store")
        self.OptionParser.add_option("--cardWidthUnit", type="choice", action="store",
                                     choices=UNITS.keys())

        self.OptionParser.add_option(
            "--cardHeight", type="float", action="store")
        self.OptionParser.add_option("--cardHeightUnit", type="choice", action="store",
                                     choices=UNITS.keys())

        self.OptionParser.add_option(
            "--bleedSize", type="float", action="store")
        self.OptionParser.add_option("--bleedSizeUnit", type="choice", action="store",
                                     choices=UNITS.keys())

        self.OptionParser.add_option(
            "--minCardSpacing", type="float", action="store")
        self.OptionParser.add_option("--minCardSpacingUnit", type="choice", action="store",
                                     choices=UNITS.keys())

        self.OptionParser.add_option(
            "--minFoldLineSpacing", type="float", action="store")
        self.OptionParser.add_option("--minFoldLineSpacingUnit", type="choice", action="store",
                                     choices=UNITS.keys())

        self.OptionParser.add_option(
            "--pageMargin", type="float", action="store")
        self.OptionParser.add_option("--pageMarginUnit", type="choice", action="store",
                                     choices=UNITS.keys())

        self.OptionParser.add_option(
            "--gridSize", type="float", action="store")
        self.OptionParser.add_option("--gridSizeUnit", type="choice", action="store",
                                     choices=UNITS.keys())

        self.OptionParser.add_option(
            "--gridAligned", type="inkbool", action="store")
        self.OptionParser.add_option("--foldLineType", type="choice", action="store",
                                     choices=FOLD_LINE_TYPES)

    def getOptions(self):
        # Read all values and their units from the options and convert them to
        # document units
        self.pageWidth = self.unittouu(self.getDocumentWidth())
        self.pageHeight = self.unittouu(self.getDocumentHeight())
        self.cardWidth = self.unittouu(
            "{}{}".format(self.options.cardWidth,
                          self.options.cardWidthUnit))
        self.cardHeight = self.unittouu(
            "{}{}".format(self.options.cardHeight,
                          self.options.cardHeightUnit))
        self.bleedSize = self.unittouu(
            "{}{}".format(self.options.bleedSize,
                          self.options.bleedSizeUnit))
        self.gridSize = self.unittouu(
            "{}{}".format(self.options.gridSize,
                          self.options.gridSizeUnit))
        self.minCardSpacing = self.unittouu(
            "{}{}".format(self.options.minCardSpacing,
                          self.options.minCardSpacingUnit))
        self.minFoldLineSpacing = self.unittouu(
            "{}{}".format(self.options.minFoldLineSpacing,
                          self.options.minFoldLineSpacingUnit))
        self.pageMargin = self.unittouu(
            "{}{}".format(self.options.pageMargin,
                          self.options.pageMarginUnit))
        self.gridAligned = self.options.gridAligned
        self.foldLineType = self.options.foldLineType

    def calculatePositions(self):
        if self.foldLineType == VERTICAL_FOLD_LINE:
            self.horizontalPositions, self.foldLinePosition = calculatePositionsWithFoldLine(
                self.pageWidth,
                self.pageMargin,
                self.cardWidth,
                self.bleedSize,
                self.gridSize,
                self.minCardSpacing,
                self.minFoldLineSpacing,
                self.gridAligned)
        else:
            self.horizontalPositions = calculatePositionsWithoutFoldLine(
                self.pageWidth,
                self.pageMargin,
                self.cardWidth,
                self.bleedSize,
                self.gridSize,
                self.minCardSpacing,
                self.gridAligned)

        if self.foldLineType == HORIZONTAL_FOLD_LINE:
            self.verticalPositions, self.foldLinePosition = calculatePositionsWithFoldLine(
                self.pageHeight,
                self.pageMargin,
                self.cardHeight,
                self.bleedSize,
                self.gridSize,
                self.minCardSpacing,
                self.minFoldLineSpacing,
                self.gridAligned)
        else:
            self.verticalPositions = calculatePositionsWithoutFoldLine(
                self.pageHeight,
                self.pageMargin,
                self.cardHeight,
                self.bleedSize,
                self.gridSize,
                self.minCardSpacing,
                self.gridAligned)

    def createGroup(self, parent, label):
        group = inkex.etree.SubElement(parent, "g")
        group.set(inkex.addNS("label", "inkscape"), label)
        return group

    def createLayer(self, label, isVisible=True):
        layer = self.createGroup(self.document.getroot(), label)
        layer.set(inkex.addNS("groupmode", "inkscape"), "layer")
        if not isVisible:
            layer.set("style", "display:none")

        # The Inkscape y-axis runs from bottom to top, the SVG y-axis runs from
        # top to bottom. Therefore we need to transform all y coordinates.
        layer.set("transform", "matrix(1 0 0 -1 0 {})".format(self.pageHeight))

        # Lock the layer
        layer.set(inkex.addNS("insensitive", "sodipodi"), "true")

        return layer

    def createBleeds(self, parent):
        if self.bleedSize <= 0:
            return

        attributes = {"x": str(-self.bleedSize),
                      "y": str(-self.bleedSize),
                      "width": str(self.cardWidth + 2.0 * self.bleedSize),
                      "height": str(self.cardHeight + 2.0 * self.bleedSize),
                      "stroke": "gray",
                      "stroke-width": str(self.unittouu("0.25pt")),
                      "fill": "none"}

        for y in self.verticalPositions:
            for x in self.horizontalPositions:
                attributes["transform"] = "translate({},{})".format(x, y)
                inkex.etree.SubElement(parent, "rect", attributes)

    def createCards(self, parent):
        attributes = {"x": str(0),
                      "y": str(0),
                      "width": str(self.cardWidth),
                      "height": str(self.cardHeight),
                      "stroke": "gray",
                      "stroke-width": str(self.unittouu("1pt")),
                      "fill": "none"}

        for y in self.verticalPositions:
            for x in self.horizontalPositions:
                attributes["transform"] = "translate({},{})".format(x, y)
                inkex.etree.SubElement(parent, "rect", attributes)

    def createFoldLine(self, parent):
        attributes = {"stroke": "black",
                      "stroke-width": str(self.unittouu("0.25pt")),
                      "stroke-dasharray": "2,1",
                      "fill": "none"}

        if self.foldLineType == HORIZONTAL_FOLD_LINE:
            attributes["d"] = "M 0,{} H {}".format(
                self.foldLinePosition, self.pageWidth)
        elif self.foldLineType == VERTICAL_FOLD_LINE:
            attributes["d"] = "M {},0 V {}".format(
                self.foldLinePosition, self.pageHeight)
        else:
            return

        inkex.etree.SubElement(parent, "path", attributes)

    def createCropLines(self, parent):
        attributes = {"stroke": "black",
                      "stroke-width": str(self.unittouu("0.25pt")),
                      "fill": "none"}

        # (begin, end) pairs for vertical crop line between bleeds
        pairs = []
        begin = 0
        for y in self.verticalPositions:
            end = y - self.bleedSize
            pairs.append((begin, end))
            begin = end + self.cardHeight + 2.0 * self.bleedSize
        pairs.append((begin, self.pageHeight))

        # One crop line consists of many short strokes
        attributes["d"] = " ".join(["M 0,{} 0,{}".format(begin, end)
                                    for (begin, end) in pairs])

        # Shifted copies of the crop line
        for x in self.horizontalPositions:
            attributes["transform"] = "translate({},0)".format(x)
            inkex.etree.SubElement(parent, "path", attributes)
            attributes["transform"] = "translate({},0)".format(
                x + self.cardWidth)
            inkex.etree.SubElement(parent, "path", attributes)

        # (begin, end) pairs for horizontal crop line between bleeds
        pairs = []
        begin = 0
        for x in self.horizontalPositions:
            end = x - self.bleedSize
            pairs.append((begin, end))
            begin = end + self.cardWidth + 2.0 * self.bleedSize
        pairs.append((begin, self.pageWidth))

        # One crop line consists of many short strokes
        attributes["d"] = " ".join(["M {},0 {},0".format(begin, end)
                                    for (begin, end) in pairs])

        # Shifted copies of the crop line
        for y in self.verticalPositions:
            attributes["transform"] = "translate(0,{})".format(y)
            inkex.etree.SubElement(parent, "path", attributes)
            attributes["transform"] = "translate(0,{})".format(
                y + self.cardHeight)
            inkex.etree.SubElement(parent, "path", attributes)

    def createMargin(self, parent):
        if self.pageMargin <= 0:
            return

        attributes = {"x": str(self.pageMargin),
                      "y": str(self.pageMargin),
                      "width": str(self.pageWidth - 2.0 * self.pageMargin),
                      "height": str(self.pageHeight - 2.0 * self.pageMargin),
                      "stroke": "gray",
                      "stroke-width": str(self.unittouu("0.25pt")),
                      "stroke-dasharray": "0.5,0.5",
                      "fill": "none"}
        
        inkex.etree.SubElement(parent, "rect", attributes)

    def createMask(self, parent):
        attributes = {"stroke": "none",
                      "fill": "white",
                      "fill-rule": "evenodd"}

        path = "M {},{} {},{} {},{} {},{} Z".format(
            0, 0,
            self.pageWidth, 0,
            self.pageWidth, self.pageHeight,
            0, self.pageHeight)
        
        for y in self.verticalPositions:
            for x in self.horizontalPositions:
                path += " M {},{} {},{} {},{} {},{} Z".format(
                    x, y,
                    x + self.cardWidth, y,
                    x + self.cardWidth, y + self.cardHeight,
                    x, y + self.cardHeight)

        attributes["d"] = path                
        inkex.etree.SubElement(parent, "path", attributes)

    def effect(self):
        self.getOptions()
        self.calculatePositions()

        nonPrintingLayer = self.createLayer("(template) cards and bleeds")
        maskLayer = self.createLayer("(template) mask", isVisible=False)
        printingLayer = self.createLayer("(template) fold and crop lines")

        self.createFoldLine(printingLayer)
        self.createMargin(printingLayer)
        self.createMask(maskLayer)

        bleedsGroup = self.createGroup(nonPrintingLayer, "bleeds")
        self.createBleeds(bleedsGroup)

        cardsGroup = self.createGroup(nonPrintingLayer, "cards")
        self.createCards(cardsGroup)

        cropLinesGroup = self.createGroup(printingLayer, "crop lines")
        self.createCropLines(cropLinesGroup)



if __name__ == '__main__':
    playingCardsExtension = PlayingCardsExtension()
    playingCardsExtension.affect()
