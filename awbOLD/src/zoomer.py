#zoomView:
#given a societymodel, draws it at the chosen level of zoom granularity
import sys
import re

from wxPython.wx import *
from wxPython.ogl import *


DEFAULT_ZOOMLEVEL = 1

viewLevelData = [
{"BOXWIDTH":   10,"BOXHEIGHT":  6, "WIDTHSPACING": 4, "HEIGHTSPACING":  30,"HEIGHTSPACING": 30,"FONTSIZE":6},
{"BOXWIDTH":   20,"BOXHEIGHT": 12, "WIDTHSPACING":  8, "HEIGHTSPACING":  60,"HEIGHTSPACING": 60,"FONTSIZE":8},
{"BOXWIDTH":   50,"BOXHEIGHT": 30, "WIDTHSPACING":20, "HEIGHTSPACING": 150,"HEIGHTSPACING":150,"FONTSIZE":12},
{"BOXWIDTH": 100,"BOXHEIGHT": 60, "WIDTHSPACING":40, "HEIGHTSPACING": 300,"HEIGHTSPACING":300,"FONTSIZE":24},
]

ZEROLEVEL = 0
MAXWIDTH = 8000
MAXHEIGHT= 1000
BOXWIDTH = 50
BOXHEIGHT = 30
WIDTHSPACING = 20
HEIGHTSPACING = 150

CURRENTLEVEL = DEFAULT_ZOOMLEVEL

def setLevel(level=1): 
        global CURRENTLEVEL
        if level < 0: level = 0
        if level > 3: level = 3
        CURRENTLEVEL = level
def getLevel(): return CURRENTLEVEL
