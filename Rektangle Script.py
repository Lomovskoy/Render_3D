# -*- coding: utf-8 -*-
from PIL import Image

scr_x = 200
scr_y = 200

img = Image.new('RGB', (scr_x+1,scr_y+1), "black")
canvas = img.load()


class Point(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def show(self, color = None):
        canvas[self.x, scr_y - self.y] = color or (255, 255, 255)

    def copy(self):
        return Point(self.x, self.y)

        
points = [Point(20, 30),Point(120, 60),Point(70, 130)]

for p in points:
    p.show()

def triang(coords):
    a,b,c = sorted(coords, key = lambda p: p.y)
    p1 = a.copy()
    delta_p1 = float(b.x - a.x)/(b.y - a.y)
    p2 = a.copy()
    delta_p2 = float(c.x - a.x)/(c.y - a.y)
    for y in (b.y, c.y):
        while p1.y < y:
            if p1.x > p2.x:
                p3 = p2.copy()
                x = p1.x
            else:
                p3 = p1.copy()
                x = p2.x
            while p3.x < x:
                p3.show()
                p3.x += 1
            p1.y += 1
            p1.x += delta_p1
            p2.show()
            p2.y += 1
            p2.x += delta_p2
        delta_p1 = float(c.x - b.x)/(c.y - b.y)


triang(points)

img.show()
