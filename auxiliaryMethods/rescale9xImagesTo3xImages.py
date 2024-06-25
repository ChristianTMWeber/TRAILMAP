import ray
from ray.experimental import tqdm_ray

import skimage
import os
import tifffile
import time

from getTiffFileTuple import getTiffFileTuple
from tiffStackArray import tiffStackArray


import numpy as np

@ray.remote # this decorator tells Ray to parallelize this function
def rescaleImage(imagePath1, imagePath2, scaleFactor, outputPath, referenceIntensityArray = None):

    image1 = tifffile.imread(imagePath1).astype(np.float32)


    if imagePath2 is not None:
        image2 = tifffile.imread(imagePath2).astype(np.float32)

        # average the two images
        image = (image1 + image2)/2
    else: image = image1


    if scaleFactor != 1:

        scaledImage = skimage.transform.rescale(image.astype(np.float32 ), scaleFactor, order=1, mode='constant', cval=0, 
                                clip=True, anti_aliasing=True)
                                # preserve_range=False
                                #, anti_aliasing_sigma=None

    else:
        scaledImage = image

    if referenceIntensityArray is not None:
        scaledImage = skimage.exposure.match_histograms(scaledImage, referenceIntensityArray, channel_axis=None)

    tifffile.imwrite(outputPath, scaledImage.astype(np.uint16), compression ="zlib")

    #tifffile.imwrite(outputPath +"LZW", scaledImage.astype(np.uint16), compression ="LZW")

    del image, image1, scaledImage
    if imagePath2 is not None: del image2

    return None     

def getTrailmapReferenceArray(referenceImages = "/home/chweber/TRAILMAP/data/testing/example-chunk"):
    

    trailmapImageArray = tiffStackArray(referenceImages)[:]

    # turn the array into _some_ 2D shape for 'skimage.exposure.match_histograms' later on
    trailmapImageArray = np.reshape(trailmapImageArray, (-1, trailmapImageArray.shape[1]) )

    return trailmapImageArray

if __name__ == "__main__":

    doIntensityHistMatching = True

    averageImages = False

    scaleFactor =  1#0.7/1.8

    #imagePath = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH"
    #sourceImageasForHistMatching = "/home/chweber/TRAILMAP/data/testing/example-chunk"  

    imagePath = "/media/ssdshare2/general/Lorenzo/20240503_13_42_22_5617_WT_001/20240514_11_49_16_57622_WT_stitched/Ex_642_Ch2_MIP_stitched"
    sourceImagesForHistMatching = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_500umMIPs"



    tiffTuple = getTiffFileTuple( imagePath, ".tif{1,2}" )


    outputFolder = imagePath + "_rescaled_by_%.3f" % scaleFactor

    trailmapTargetIntesityArrayRayReference = None

    ray.init(num_cpus=16) # Initialize Ray with some number of workers

    if doIntensityHistMatching: 
        outputFolder += "_histMatched"

        trailmapTargetIntesityArray = getTrailmapReferenceArray(referenceImages = sourceImagesForHistMatching)

        trailmapTargetIntesityArrayRayReference = ray.put(trailmapTargetIntesityArray)

    os.makedirs(outputFolder, exist_ok=True)

    workScheduleForRayWorkers = []

    startTime = time.time()
    for index in range(0,len(tiffTuple)-1, 1 + averageImages):

        tiffPath1 = tiffTuple[index]
        if averageImages: tiffPath2 = tiffTuple[index+1]
        else: tiffPath2 = None

        outputPath = os.path.join(outputFolder, os.path.basename(tiffPath1))


        workScheduleForRayWorkers.append( rescaleImage.remote(tiffPath1, tiffPath2, scaleFactor, outputPath, referenceIntensityArray = trailmapTargetIntesityArrayRayReference))

      


        print("Scheduled: %i out of %i" %(index+1, len(tiffTuple)))

        #if index > 30: break


    rayoutput = ray.get(workScheduleForRayWorkers)

    ray.shutdown() # shutdown Ray to release resources and memory

    print("Time taken: %.2f" %(time.time()-startTime))

    

