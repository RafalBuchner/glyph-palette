import AppKit
from mojo.events import addObserver, removeObserver, EditingTool
import vanilla, math
from mojo.extensions import setExtensionDefault, getExtensionDefault
from glyphsRepresentation import GlyphRepr
from mojo.drawingTools import *
from mojo.UI import UpdateCurrentGlyphView, CurrentGlyphWindow, OpenSpaceCenter, getDefault

def isNumEven(num):
    if (num % 2) == 0:
       return True
    else:
       return False
class SettingsGet:
    def __init__(self, value):
        self.value = value
    def get(self):
        if self.value:
            return 1
        else: return 0
class ShowGlyphPalette:
    bcColor = AppKit.NSColor.grayColor()
    fill = getDefault("glyphViewFillColor")
    attr = {
                AppKit.NSFontAttributeName: AppKit.NSFont.fontWithName_size_("Monaco", 8.0),
                AppKit.NSForegroundColorAttributeName: AppKit.NSColor.whiteColor()
            }
    key = "com.rafalbuchner.ShowGlyphPalette"

    def __init__(self):
        # self.debugW = vanilla.FloatingWindow((0,0,100,100))
        # self.debugW.bind("close",self.closingDebug)
        # self.debugW.open()
        self.isCursorAbove = False
        self.glyphList = []
        self.methodsToDraw = []
        self.methodsToDrawBackground = []
        self.itemsCallbacks = {'show related cluster': self.showGlyphsWithCurrentCB, 'show related in back': self.showRelatedInBackCB}
        self.items = {'show related cluster': True, 'show related in back': True}
        self.loadSettings()
        addObserver(self, "glyphAdditionContextualMenuItemsCB", "glyphAdditionContextualMenuItems")
        addObserver(self, "currentGlyphChangedCB", "currentGlyphChanged")
        addObserver(self, "drawCB", "draw")
        addObserver(self, "drawBackgroundCB", "drawBackground")
        addObserver(self, "mouseMovedCB", "mouseMoved")
        addObserver(self, "mouseDownCB", "mouseDown")

    # def closingDebug(self, info):
    #     removeObserver(self, "glyphAdditionContextualMenuItems")
    #     removeObserver(self, "currentGlyphChanged")
    #     removeObserver(self, "draw")
    #     removeObserver(self, "drawBackground")
    #     removeObserver(self, "mouseMoved")
    #     removeObserver(self, "mouseDown")

    def drawRelatedGlyphWindow(self, cursor, glyph, view):
        view._drawTextInRect(f"name:  {glyph.name}\nwidth: {glyph.width}",
        self.attr, cursor, yOffset=10, xOffset=10, drawBackground=True, position="left", backgroundColor=self.bcColor)

    def mouseDownCB(self, point):
        if point['clickCount'] == 2:
            if self.isCursorAbove:
                CurrentGlyphWindow().setGlyphByName(self.glyphBelowName)

    def mouseMovedCB(self, info):

        self.cursor = (info['point'].x, info['point'].y)
        self.isCursorAbove = False
        if self.items['show related cluster']:
            for glyphRepr in self.glyphList:
                if glyphRepr.isInside(self.cursor):
                    self.view = info["view"]
                    self.glyphBelowName = glyphRepr.name
                    self.isCursorAbove = True

                    break
            UpdateCurrentGlyphView()

    def currentGlyphChangedCB(self, sender):
        self.glyph = CurrentGlyph()
        if self.glyph is None:
            return
        font = self.glyph.font
        self.glyphList = []
        self.clusterWidth = []
        for glyph in font:
            try:
                for component in glyph.components:
                    if component.baseGlyph == self.glyph.name:
                        # glyphRepr = GlyphRepr(font[glyph.name],origin=(self.glyph.width/2, self.glyph.bounds[-1]/2),fillColor=self.fill,shift=None,offset=font.info.ascender*1)
                        glyphRepr = GlyphRepr(font[glyph.name],origin=(0, 0),fillColor=self.fill,shift=None,offset=font.info.ascender*1)

                        self.glyphList += [glyphRepr]

                        self.clusterWidth += [font[glyph.name].width]
                

            except:
                print(f"glyph <{glyph.name}> contains corrupted component")
        if len(self.glyphList) > 0:
            scale = 3/len(self.glyphList)
            # for i, glyphRepr in enumerate(self.glyphList):
            #         glyphRepr.origin = (self.glyph.width/2-sum(self.clusterWidth)*scale/2+sum(self.clusterWidth[:i])*scale,
            #                             self.glyph.bounds[-1]/2)
            if scale > .4:
                scale = .4
            for glyph in self.glyphList:
                glyph.scale = scale

    @staticmethod
    def appendMethodToDrawingMethods(sender, method,drawingMethods):
        if sender.get() == 1:
            if method not in drawingMethods:
                drawingMethods.append(method)
                UpdateCurrentGlyphView()
        else:
            if method in drawingMethods:
                drawingMethods.remove(method)
                UpdateCurrentGlyphView()

    def showRelatedInBackCB(self, sender):
        ShowGlyphPalette.appendMethodToDrawingMethods(sender, self.showRelatedInBackDraw, self.methodsToDrawBackground)

    def showGlyphsWithCurrentCB(self, sender):
        ShowGlyphPalette.appendMethodToDrawingMethods(sender, self.showGlyphsWithCurrentDraw, self.methodsToDrawBackground)

    def showRelatedInBackDraw(self, scale):
        for glyphRepr in self.glyphList:
            glyph = self.glyph.font[glyphRepr.name]

            shift = (self.glyph.width - glyph.width)/2
            glyphReprBack = GlyphRepr(
                glyph,
                origin=(shift, 0),
                fillColor = self.fill,
                shift=shift,
                offset=0)
            stroke(None)
            glyphReprBack.draw()

    def drawPreviewCB(self, scale):
        pass

    def showGlyphsWithCurrentDraw(self, scale):
        ### THIS
        def _getGlyphWidth(glyphRepr):
            return glyphRepr.glyph.width
        if self.glyphList:

            # for i, glyphRepr in enumerate(self.glyphList):
            for i, glyphRepr in enumerate(self.glyphList):
                print(sum(self.clusterWidth))
                glyphRepr.origin = (self.glyph.width/2-sum(self.clusterWidth)*glyphRepr.scale/2+sum(self.clusterWidth[:i])*glyphRepr.scale,
                                    self.glyph.bounds[-1]/2)
                stroke(None)

                glyphRepr.draw()

    def drawCB(self, scale):
        if self.isCursorAbove:
            glyph = self.glyph.font[self.glyphBelowName]
            self.drawRelatedGlyphWindow(self.cursor, glyph, self.view)

        for method in self.methodsToDraw:
            method(scale)

    def drawBackgroundCB(self, scale):
        for method in self.methodsToDrawBackground:
            method(scale)

    def loadSettings(self):
        # loading settings
        zero_settings = self.items
        settings = getExtensionDefault(self.key, fallback=self.items)
        if settings:
            for name in settings:
                self.items[name] = settings[name]
            else:
                self.items = zero_settings
        else:
            self.items = zero_settings

    def savingSettings(self):
        setExtensionDefault(self.key, self.items)


    def glyphAdditionContextualMenuItemsCB(self, info):
        menuItems = info['additionContextualMenuItems']
        showGlyphPaletteMenuItems = []
        tool = info["tool"]
        if isinstance(tool, EditingTool):

            for title in self.items:
                temp = title.replace(" ","_")
                value = self.items[title]
                checkboxMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("regular", '', '')
                MenuTextAttributes = {AppKit.NSFontAttributeName: AppKit.NSFont.menuFontOfSize_(14)}
                t =  AppKit.NSAttributedString.alloc().initWithString_attributes_(title, MenuTextAttributes)
                checkbox = vanilla.CheckBox((0, 0, 100, 22), t, value=value, callback=self.checkboxCallback)
                setattr(self, temp, checkbox)
                view =checkbox.getNSButton()
                view.setFrame_(((0, 0), (200, 30)))
                checkboxMenuItem.setView_(view)
                showGlyphPaletteMenuItems += [checkboxMenuItem]
                cb = self.itemsCallbacks.get(title)
                if cb is not None:
                    cb(checkbox)

            showGlyphPaletteMenuItems += [
                ("print out palette", self.printOutClusterCallback),
                ("open palette in SpaceCenter", self.openClusterInSpaceCenterCallback),
                ("select palette in font", self.selectClusterCallback)
            ]
        menuItems += [("Glyph Palette", showGlyphPaletteMenuItems)]
    def selectClusterCallback(self, sender):
        self.glyph.font.selectedGlyphNames = [glyph.glyph.name for glyph in self.glyphList]



    def openClusterInSpaceCenterCallback(self, sender):
        spaceCenter = OpenSpaceCenter(self.glyph.font)
        spaceCenter.setPre([glyph.glyph.name for glyph in self.glyphList])


    def printOutClusterCallback(self, sender):
        print([glyph.glyph.name for glyph in self.glyphList])

    def checkboxCallback(self, obj):
        value = False
        if obj.get() == 1:
            value = True
        self.items[obj.getTitle()] = value
        self.savingSettings()

        self.itemsCallbacks[obj.getTitle()](obj)


ShowGlyphPalette()
