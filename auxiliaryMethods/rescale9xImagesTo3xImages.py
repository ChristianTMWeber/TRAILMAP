import ray
from ray.experimental import tqdm_ray

import skimage
import os
import tifffile
import time

import numpy as np

import remote
import re


from auxiliaryMethods.rescale9xImagesTo3xImages import rescaleImages

def getTiffFileTuple( imagePath : str , fileType : str = ".tif{1,2}") -> tuple:
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


@ray.remote # this decorator tells Ray to parallelize this function
def rescaleImage(imagePath1, imagePath2, scaleFactor, outputPath, referenceIntensityArray = None):

    image1 = tifffile.imread(imagePath1).astype(np.float32)


    # half the z-resolution by avereging pairs of z-slices
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

def getTrailmapReferenceArray(referenceImages = "../data/testing/example-chunk"):
    

    trailmapImageArray = tiffStackArray(referenceImages)[:]

    # turn the array into _some_ 2D shape for 'skimage.exposure.match_histograms' later on
    trailmapImageArray = np.reshape(trailmapImageArray, (-1, trailmapImageArray.shape[1]) )

    return trailmapImageArray


def rescaleImagesFromFolder( folderWithImages , outputFolder,  scaleFactor = 0.7/1.8, nCPUs = os.cpu_count()//4 ):
    # nCPUs = os.cpu_count()//4 - presume we have hyperthreading, 
    #                             use half of physical cores



    # get images with reference intensity distribution
    script_path = os.path.dirname(os.path.abspath(__file__))
    referenceHistograms = os.path.join(script_path,"../data/testing/example-chunk")

    trailmapTargetIntesityArray = getTrailmapReferenceArray(referenceImages = referenceHistograms)

    # create a reference to the array for use with the ray workers
    trailmapTargetIntesityArrayRayReference = ray.put(trailmapTargetIntesityArray)


    # setup ray workers
    ray.init(num_cpus=nCPUs) # Initialize Ray with some number of workers

    # get images
    tiffTuple = getTiffFileTuple( folderWithImages, ".tif{1,2}" )

    os.makedirs(outputFolder, exist_ok=True)

    averageZStackPairs = False


    workScheduleForRayWorkers = []

    for index in range(0,len(tiffTuple)-1, 1 + averageZStackPairs):

        tiffPath1 = tiffTuple[index]
        if averageZStackPairs: tiffPath2 = tiffTuple[index+1]
        else: tiffPath2 = None

        outputPath = os.path.join(outputFolder, os.path.basename(tiffPath1))


        workScheduleForRayWorkers.append( rescaleImage.remote(tiffPath1, tiffPath2, scaleFactor, outputPath, referenceIntensityArray = trailmapTargetIntesityArray))

        print("Scheduled: %i out of %i" %(index+1, len(tiffTuple)))

        #if index > 30: break


    rayoutput = ray.get(workScheduleForRayWorkers)

    ray.shutdown() # shutdown Ray to release resources and memory

    return outputFolder

if __name__ == "__main__":

    # get images with reference intensity distribution
    script_path = os.path.dirname(os.path.abspath(__file__))
    referenceHistograms = os.path.join(script_path,"../data/testing/example-chunk")


    rescaleImagesFromFolder( referenceHistograms , outputFolder,  scaleFactor = 0.7/1.8, nCPUs = 6 )




    print("Time taken: %.2f" %(time.time()-startTime))

    

