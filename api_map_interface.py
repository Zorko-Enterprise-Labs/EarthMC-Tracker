import map.map as map
import datetime
import time
import os

defaultfolder = "maptiles/"
defaultzoomlevels = [1,2,3,4,5]
defaultdatetimeformat = "%d-%m-%y-%H-%M-%S"

def downloadsnapshot(path : str, prepath=defaultfolder, zoomlevels=defaultzoomlevels):
    outputfolder = os.path.join(prepath, path)
    map.download_all_tiles(outputfolder, ZOOM_LEVELS=zoomlevels)

def getsuggestedtilespath(datetimeformat=defaultdatetimeformat):
    date = datetime.datetime.now(datetime.UTC).strftime(datetimeformat)
    return date

print(downloadsnapshot(getsuggestedtilespath()))