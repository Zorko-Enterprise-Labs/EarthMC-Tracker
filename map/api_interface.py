if __name__ == "__main__":
    import map
else:
    import map.map as map

import datetime
import time
import os
from dataclasses import dataclass

defaultfolder = "maptiles/"
defaultzoomlevels = [1,2,3,4,5]
defaultdatetimeformat = "%d-%m-%y-%H-%M-%S"

@dataclass
class ZoomLevel:
    level : int
    imagecount : int
    parentpath : str

    def getfile(self, filename : str):
        path = os.path.join(self.parentpath, str(self.level), filename)
        print(path)
        if not os.path.isfile(path):
            return None
        filecontent = open(path, "rb").read()
        return filecontent

@dataclass
class SnapshotFolder:
    zoomlevels : list[ZoomLevel]
    folderpath : str
    prepath : str

    def getzoomlevel(self, zoomlevel : int):
        for level in self.zoomlevels:
            if level.level == zoomlevel:
                return level

def downloadsnapshot(path : str, prepath=defaultfolder, zoomlevels=defaultzoomlevels, verboselogging=True):
    outputfolder = os.path.join(prepath, path)
    map.download_all_tiles(outputfolder, ZOOM_LEVELS=zoomlevels, verboselogging=verboselogging)

def getsnapshot(path : str, prepath=defaultfolder):
    inputfolder = os.path.join(prepath, path)
    contens = os.listdir(inputfolder)

    zoomlevels = []
    for item in contens:
        zoomlevel = int(item)
        if zoomlevel:
            imagecount = len(os.listdir(os.path.join(inputfolder, item)))
            zoomlevel = ZoomLevel(zoomlevel, imagecount, inputfolder)
            zoomlevels.append(zoomlevel)

    return SnapshotFolder(
        zoomlevels, inputfolder, prepath
    )

def getsuggestedtilespath(datetimeformat=defaultdatetimeformat):
    date = datetime.datetime.now(datetime.timezone.utc).strftime(datetimeformat)
    return date

def downloadsnapshotbackground(path : str, id : int, onfinish : callable, prepath=defaultfolder, zoomlevels=defaultzoomlevels, verboselogging=True):
    downloadsnapshot(path, prepath=defaultfolder, zoomlevels=zoomlevels, verboselogging=verboselogging)
    onfinish(id)
downloadsnapshot(getsuggestedtilespath(), zoomlevels=[0,1,2,3,4,5])