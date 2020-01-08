from fontTools.pens.pointInsidePen import PointInsidePen
from mojo.drawingTools import *
import math

class GlyphRepr:

    def __init__(self, glyph, origin, fillColor=(0,0,0,1), shift=None,offset=0):
        self.bcColor = 0, 0, 1, .3
        self.glyph = glyph
        self.name = glyph.name
        self.fill = fillColor
        self.origin = origin
        if shift is not None:
            self.shift = shift
        else:
            self.shift = -glyph.width/2
        self.rotation = 0
        self.offset = offset
        self.areaRect = (0, self.glyph.font.info.descender, self.glyph.width, self.glyph.font.info.ascender-self.glyph.font.info.descender)
        self.scale = 1

    def isInside(self, cursor):
        pen = PointInsidePen(None, cursor)
        for i, point in enumerate(self.activeAreaRect):
            if i == len(self.activeAreaRect) - 1:
                pen.lineTo(point)
                pen.closePath()
                break
            elif i == 0:
                pen.moveTo(point)
            else:
                pen.lineTo(point)
        result = pen.getResult()
        if result:
            self.bcColor = 0, 0, 1, .3
        else: self.bcColor = 1, 0, 0, .3
        return result



    def draw(self):
        save()
        fill(*self.fill)
        scale(self.scale)
        translate(self.origin[0]/self.scale, self.origin[1]/self.scale)
        # rotate(math.degrees(self.rotation))
        translate(self.shift,0)
        translate(0, self.offset/self.scale)
        drawGlyph(self.glyph)
        restore()

    @property
    def activeAreaRect(self):
        activeAreaRect = []
        x,y,w,h = self.areaRect
        for point in [
                (x, y),
                (x+w, y),
                (x+w, y+h),
                (x,   y+h)
            ]:

            point = (point[0]*self.scale, point[1]*self.scale)
            point = GlyphRepr.movePointTo(point,(self.origin[0],self.origin[1]))
            point = GlyphRepr.movePointTo(point,(self.shift*self.scale,0))
            point = GlyphRepr.movePointTo(point,(0, self.offset))
            point = GlyphRepr.rotatePoint(point, self.rotation, (self.origin[0],self.origin[1]))
            activeAreaRect += [point]
        return activeAreaRect

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, radians):
        self._rotation = radians

    @staticmethod
    def movePointTo(p, offset) -> tuple:
        x,y = p
        ox, oy = offset
        return (x+ox, y+oy)

    @staticmethod
    def angle(p1, p2):
        p1x, p1y = p1
        p2x, p2y = p2
        return math.atan2(p2x - p1x, p2y - p1y)

    @staticmethod
    def rotatePoint(P, radians, originPoint):
        alfa = radians
        px,py=P
        originPointX, originPointY = originPoint

        x = ( px - originPointX ) * math.cos( alfa ) - ( py - originPointY ) * math.sin( alfa ) + originPointX
        y = ( px - originPointX ) * math.sin( alfa ) + ( py - originPointY ) * math.cos( alfa ) + originPointY

        return x, y
if __name__ == "__main__":
    def dp(p):
        x,y = p
        s = 10
        r = s/2
        rect(x-r,y-r,s,s)

    f  = CurrentFont()
    g1 = f['W']

    gr = GlyphRepr(g1,origin=(-30, 70),fillColor=(1,0,0,.8),shift=None,offset=220)
    translate(500, 200)
    scale(.8)
    gr.scale = .2
    gr.rotation = radians(13)

    save()
    fill(None)
    stroke(0,0,1,.3)
    strokeWidth(7)
    line((-1000,0),(1000,0))
    line((0,-1000),(0,1000))

    cursor = (-30, 430)
    dp(cursor)
    print(gr.isInside(cursor))
    gr.draw()
