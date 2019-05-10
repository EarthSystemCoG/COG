# CoG module to manage image thumbnails

import os
from PIL import Image
import shutil
from django.conf import settings
from cog.models.constants import DEFAULT_IMAGES
from cog.models.constants import UPLOAD_DIR_PHOTOS

import logging

log = logging.getLogger(__name__)

THUMBNAIL_EXT = "png"
THUMBNAIL_EXT2 = "jpeg" # old extension
THUMBNAIL_SIZE_SMALL = 35,35
THUMBNAIL_SIZE_BIG = 60,60

# Builds the expected path for the thumbnail of an image.
# If mustExist=True, the method will first try .png, then .jpeg, 
# then default to unkwnon.png
def getThumbnailPath(filePath, mustExist=False):
    
    # thumbnail is located in the same directory as the image,
    # but has different name and extension
    directory, fileName = os.path.split(filePath)
    name, extension = os.path.splitext(fileName)
    thumbnailPath = os.path.join(directory, "%s.thumbnail.%s" % (name, THUMBNAIL_EXT) )
    
    # check for thumbnail existence, if not found try some other file 
    if mustExist:
        
        photoDirPath = os.path.join( getattr(settings,'MEDIA_ROOT'), UPLOAD_DIR_PHOTOS)
        
        # try '.png'
        tdir, tname = os.path.split(thumbnailPath)
        fullPath = os.path.join(photoDirPath, tname)
                
        # try '.jpeg'
        if not os.path.exists(fullPath):
            fullPath = fullPath.replace(THUMBNAIL_EXT, THUMBNAIL_EXT2)
            if os.path.exists(fullPath):
                thumbnailPath = thumbnailPath.replace(THUMBNAIL_EXT, THUMBNAIL_EXT2)
            else:
                thumbnailPath = getattr(settings,'STATIC_URL') + DEFAULT_IMAGES['User']
    
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
            log.error("Cannot create thumbnail for %s, using full image instead. Error: %s" % (filePath, str(error)))
            shutil.copy(filePath, thumbnailPath)

def deleteThumbnail(filePath):
    thumbnailPath = getThumbnailPath(filePath)
    if os.path.exists(thumbnailPath):
        try:
            os.remove(thumbnailPath)
        except IOError as error:
            log.error("Cannot delete thumbnail for %s. Error %s" % (filePath, str(error)))
            
def deleteImageAndThumbnail(obj):
    '''Method to delete an object image and thumbnail simultaneously.'''
    deleteThumbnail(obj.image.path)
    obj.image.delete()
