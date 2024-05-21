import os
import tifffile
import skimage

import ray # for parallel processing


import time

import zarr

import re

import numpy as np

import matplotlib.pyplot as plt

from tiffStackArray import tiffStackArray

import ray

import gc # garbage collection

def getTiffFileTuple( imagePath : str , fileType : str) -> tuple:
    # get all the tiff files in a given folder

    if isinstance(imagePath,str): 
        imagePath = os.path.abspath( imagePath )
    else: raise Exception("'imagePath' is not of type 'str', it is if type %s" %(str(type(imagePath))))

    if isinstance(imagePath,str) and os.path.isfile(imagePath):
        return tuple([imagePath])
    
    # otherwise we presume to have the path to a folder with multiple tiff files
    tiffFileList = []
    for file in sorted(os.listdir(imagePath)):

        # use regular expressions to be specific and flexible in defining file endings
        matchedFileTypes = re.findall(fileType,file)
        if len(matchedFileTypes) == 0 : continue # file did not match our fileType

        if file.endswith(matchedFileTypes[-1]):
            # double check that the regular expression match actually occured at the end of the file
            tiffFileList.append( os.path.join(imagePath,file))

    if len(tiffFileList) == 0 : 
        raise Exception("No files found whose ending matches '%s' in \n%s" %(fileType, imagePath))

    return tuple(tiffFileList)


#@ray.remote
def scaleAndWriteOutImages(tiffPath, outputFolder,  trailmapArray = None):

    tiffArray = tifffile.imread(tiffPath)

    tiffArrayHistMatched = tiffArray
    if trailmapArray is not None:
        tiffArrayHistMatched = skimage.exposure.match_histograms(tiffArray, trailmapArray, channel_axis=None)

    tiffArrayScaled = skimage.transform.downscale_local_mean(tiffArrayHistMatched, (3,3), cval=0, clip=True)

    outputFilePath = os.path.join(outputFolder, os.path.basename(tiffPath) )
    tifffile.imwrite(outputFilePath, tiffArrayScaled.astype(np.uint16) )


    del tiffArray , tiffArrayHistMatched , tiffArrayScaled  # free up memory

    #gc.collect()

    return None

    


def writeOutImages(tiffList , outputFolder, imgOffset = 0, trailmapArray = None):
    # trailmapArray is used to scale the images to the range of the trailmap images

    os.makedirs(outputFolder, exist_ok=True)
    
    startTime = time.time()

    workScheduleForRayWorkers = []
    for index , tiffPath in enumerate(tiffList):

        #if index < 1500: continue
        #if index >= 1700: break



        #tiffArray = tifffile.imread(tiffPath)
        #tiffArrayHistMatched = tiffArray
        #if trailmapArray is not None:
        #    tiffArrayHistMatched = skimage.exposure.match_histograms(tiffArray, trailmapArray, channel_axis=None)
        #tiffArrayScaled = skimage.transform.downscale_local_mean(tiffArrayHistMatched, (3,3), cval=0, clip=True)
        #outputFilePath = os.path.join(outputFolder, os.path.basename(tiffPath) )
        #tifffile.imwrite(outputFilePath, tiffArrayScaled.astype(np.uint16) )


        #workScheduleForRayWorkers.append( scaleAndWriteOutImages.remote(tiffPath,outputFolder,trailmapArray) )

        scaleAndWriteOutImages(tiffPath, outputFolder,  trailmapArray = None)

        #pass

        

        #image = tiffList[tiffIndex,:,:].astype(np.float32)
        #image_rescaled = skimage.transform.resize(image, [303,303] , anti_aliasing=True)
        #image_rescaled = image_rescaled.astype(np.uint16)
        #outputFileName = "image_%i.tiff" %(tiffIndex + imgOffset)
        #outputFilePath = os.path.join(outputFolder, outputFileName )
        #tifffile.imwrite(outputFilePath, image_rescaled)

        print(os.path.basename(tiffPath), time.time() - startTime)

    #completedRayWork = ray.get(workScheduleForRayWorkers)

    print("Elapsed time for all work: ", time.time() - startTime)

    return None


if __name__ == "__main__":

    #ray.init(num_cpus=1) # Initialize Ray with some numberof workers

    TrailmapImages = "/home/chweber/TRAILMAP/data/testing/example-chunk"

    trailmapImageArray = tiffStackArray(TrailmapImages)[:]

    trailmapImageArray = np.reshape(trailmapImageArray, (-1, trailmapImageArray.shape[1]) )


    # DBH images
    DBH_imagePath = "/home/chweber/ssd1_chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH" 

    DHB_imageList  = getTiffFileTuple( DBH_imagePath , "\.tif{1,2}")

    outputFolder = "/home/chweber/ssd1_chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_rescaledForTrailmap"

    writeOutImages(DHB_imageList , outputFolder, imgOffset = 0, trailmapArray = trailmapImageArray)

    ray.shutdown()
    print("done!")

