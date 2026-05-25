import map.map as map
import datetime
import time
import os

defaultfolder = "maptiles/"
defaultzoomlevels = [1,2,3,4,5]

def takesnapshot(path : str, prepath=defaultfolder, zoomlevels=defaultzoomlevels):
    outputfolder = os.path.join(prepath, path)
    print(outputfolder)
    map.download_all_tiles(outputfolder, ZOOM_LEVELS=zoomlevels)