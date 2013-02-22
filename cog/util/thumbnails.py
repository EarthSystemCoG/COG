# CoG module to manage image thumbnails

import os
import Image

THUMBNAIL_EXT = "jpeg"
THUMBNAIL_WIDTH = 25
THUMBNAIL_HEIGHT = 25

def getThumbnailPath(filePath):
    
    dir, fileName = os.path.split(filePath)
    name, extension = os.path.splitext(fileName)
    thumbnailPath = os.path.join(dir, "%s.thumbnail.%s" % (name, THUMBNAIL_EXT) )
    return thumbnailPath
    
    
def generateThumbnail(filePath):
        
    thumbnailPath = getThumbnailPath(filePath)
    if not os.path.exists(thumbnailPath) or os.path.getsize(thumbnailPath)==0:
        print 'Generating thumbnail: %s' % thumbnailPath
        try:
            im = Image.open(filePath)
            if im.mode != "RGB":
                im = im.convert("RGB")
            size = THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT
            im.thumbnail(size)
            im.save(thumbnailPath, "JPEG")
        except IOError as error:
            print "Cannot create thumbnail for", filePath
            print error

def deleteThumbnail(filePath):
    thumbnailPath = getThumbnailPath(filePath)
    if os.path.exists(thumbnailPath):
        print 'Deleting thumbnail: %s' % thumbnailPath
        try:
            os.remove(thumbnailPath)
        except IOError as error:
            print "Cannot delete thumbnail for", filePath
            print error