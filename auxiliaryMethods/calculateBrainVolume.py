import tifffile
import os
import skimage


from getTiffFileTuple import getTiffFileTuple
from getTiffFileTuple import yieldTiffFileTuple

import matplotlib.pyplot as plt

import numpy as np

import collections


import csv



def getThresholdedArray(imgArray, threshold, scaleTo = None):

    flattenedArray = imgArray > threshold

    if scaleTo is not None:
        flattenedArray = flattenedArray.astype(np.uint8)*scaleTo
    return flattenedArray


def getImageFlatteningThreshold(imageArray):
    # we take the flattening threshold as the first local minimum of the images intensity array

    histogram = np.histogram(imageArray.flatten(), bins=int(np.max(imageArray)//2), range = (0, int(np.max(imageArray)) ) )  

    smoothed_hist = skimage.filters.gaussian(histogram[0].astype(np.float32), sigma=1)

    localMaxima = skimage.feature.peak_local_max(smoothed_hist, min_distance=1)

    localMinima = skimage.feature.peak_local_max(-smoothed_hist, min_distance=1)

    # check that the frist local mininmum is within the first two local maxima
    assert (localMaxima[0] < localMinima[-1]) and (localMaxima[1] > localMinima[-1])

    flatteningThreshold = localMinima[-1]

    return flatteningThreshold


def smoothOutBrainMap( brainMap, sigma = 5, threshold = 100, scaleTo = 255):
    brainMapSmoothed = skimage.filters.gaussian(brainMap.astype(np.float32), sigma=sigma)

    brainImageSmoothedFlat = getThresholdedArray(brainMapSmoothed, threshold, scaleTo = scaleTo) 

    return brainImageSmoothedFlat


def writeAccountingDictToCSV(accountingDict, csvPath):
    with open(csvPath, mode='w') as csvFile:
        fieldnames = accountingDict.keys()
        writer = csv.DictWriter(csvFile, fieldnames=fieldnames)

        writer.writeheader()

        #.writerows(zip(*accountingDict.values()))


        for index in range(len(accountingDict["tiffPath"])):
            row = {}
            for key in fieldnames:
                row[key] = accountingDict[key][index]
            writer.writerow(row)

    return None


if __name__ == "__main__":

    accountingDict = collections.defaultdict(list)


    autoFlourescentPath = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Autofluorescence-MOAB_4x/445nm_Autofluorescence"
    # get the tiff files
    tiffFileTuple = getTiffFileTuple( imagePath = autoFlourescentPath , fileType = "tiff")
    
    # get the tiff files
    #tiffFileTuple = yieldTiffFileTuple( imagePath = autoFlourescentPath , fileType = "tiff")


    for index, tiffPath in enumerate(tiffFileTuple):

        #if index % 1000 != 0: continue

        accountingDict["tiffPath"].append(tiffPath)
        accountingDict["tiffName"].append( os.path.basename(tiffPath))

        outputFolder = os.path.dirname(tiffPath)+"_brainVolume"

        os.makedirs(outputFolder, exist_ok = True)

        tiffArray = tifffile.imread(tiffPath)

        tiffArray = skimage.filters.gaussian(tiffArray.astype(np.float32), sigma=5)


        #brainThreshold = getImageFlatteningThreshold(tiffArray)
        brainThreshold = 14
        accountingDict["brainThreshold"].append(brainThreshold)

        brainMap = getThresholdedArray(tiffArray, brainThreshold)

        accountingDict["brainVolume"].append(np.sum(brainMap))
        accountingDict["totalVolume"].append(np.prod(brainMap.shape))


        brainImageSmoothedFlat = smoothOutBrainMap( brainMap.astype(np.float32)*255, sigma = 5, threshold = 100, scaleTo = 255)
        

        tifffile.imwrite(os.path.join(outputFolder, os.path.basename(tiffPath)), 
                        brainImageSmoothedFlat, compression ="zlib")
        
        # plot and save a histogram of tiffArray
        #plt.figure()
        #plt.hist(tiffArray.flatten(), bins=int(np.max(tiffArray)//2), range = (0, int(np.max(tiffArray)) ))
        #plt.savefig(os.path.join(outputFolder, os.path.basename(tiffPath).replace(".tiff","_histogram.png")))

        print("Finished processing %i out of %i" %(index, len(tiffFileTuple)))

    writeAccountingDictToCSV(accountingDict, os.path.join(outputFolder, "accountingDict.csv"))

