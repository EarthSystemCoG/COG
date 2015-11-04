# CoG module to manage image thumbnails

import os
import Image

THUMBNAIL_EXT = "png"
THUMBNAIL_SIZE_SMALL = 35,35
THUMBNAIL_SIZE_BIG = 60,60

def getThumbnailPath(filePath):
    
    dir, fileName = os.path.split(filePath)
    name, extension = os.path.splitext(fileName)
    thumbnailPath = os.path.join(dir, "%s.thumbnail.%s" % (name, THUMBNAIL_EXT) )
    return thumbnailPath
    
    
def generateThumbnail(filePath, thumbnail_size):
        
    thumbnailPath = getThumbnailPath(filePath)
    if not os.path.exists(thumbnailPath) or os.path.getsize(thumbnailPath)==0:
        try:
            im = Image.open(filePath)
            if im.mode != "RGB":
                im = im.convert("RGB")
            im.thumbnail(thumbnail_size)
            im.save(thumbnailPath, "PNG")
        except IOError as error:
            print "Cannot create thumbnail for", filePath
            print error

def deleteThumbnail(filePath):
    thumbnailPath = getThumbnailPath(filePath)
    if os.path.exists(thumbnailPath):
        try:
            os.remove(thumbnailPath)
        except IOError as error:
            print "Cannot delete thumbnail for", filePath
            print error
            
def deleteImageAndThumbnail(obj):
    '''Method to delete an object image and thumbnail simultaneously.'''
    deleteThumbnail(obj.image.path)
    obj.image.delete()
