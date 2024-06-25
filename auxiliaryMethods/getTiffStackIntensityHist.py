
import matplotlib.pyplot as plt
import numpy as np
import os

import time

import ray
from ray.experimental import tqdm_ray

import tifffile

from getTiffFileTuple import getTiffFileTuple

@ray.remote # this decorator tells Ray to parallelize this function
def getHistogram(tiffPath, nBins , binRange, brainMaskPath = None):

    tiffArray = tifffile.imread(tiffPath)

    if brainMaskPath is not None:

        brainMask = tifffile.imread(brainMaskPath)

        tiffArray = tiffArray[brainMask > 0]

        del brainMask
        

    tempHist = np.histogram(tiffArray.flatten(), bins=nBins, range=binRange)

    del tiffArray

    return tempHist 

@ray.remote # this decorator tells Ray to parallelize this function
def saveBinaryMaskAfterThreshold(imagePath, threshold, scaleTo = 255, saveAs = None):

    imgArray = tifffile.imread(imagePath)

    thresholdedArray = imgArray > threshold

    pixelsAboveThreshold = np.sum(thresholdedArray)
    fractionalFill = float(pixelsAboveThreshold) / imgArray.size

    if scaleTo is not None:
        thresholdedArray = thresholdedArray.astype(np.uint8)*scaleTo

    if saveAs is not None:
        tifffile.imwrite(saveAs, thresholdedArray, compression ="zlib")


    del imgArray, thresholdedArray , pixelsAboveThreshold

    return fractionalFill

if __name__ == "__main__":

    imagePath = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Autofluorescence-MOAB_4x/561nm_MOAB"

    brainMaskPath = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Autofluorescence-MOAB_4x/445nm_Autofluorescence_brainVolume"

    task="thresholdMap"
    #task="histogramming"

    tiffTuple = getTiffFileTuple( imagePath, ".tif")

    brainMaskTuple = getTiffFileTuple( brainMaskPath, ".tiff")

    threshold = 125

    outputFolder = imagePath + "_thresholdMapAt_%i" %(threshold)

    os.makedirs(outputFolder, exist_ok = True)

    nBins = 10000
    binRange = (0, nBins)

    hist = np.zeros(nBins, dtype=np.uint64)

    binEdges = np.linspace(0, 10000, nBins+1)

    ray.init(num_cpus=30) # Initialize Ray with some numberof workers
    workScheduleForRayWorkers = []



    startTime = time.time()

    for index , (tiffPath, brainMaskPath) in enumerate( zip(tiffTuple,brainMaskTuple)):

        if task == "thresholdMap":
            workScheduleForRayWorkers.append( saveBinaryMaskAfterThreshold.remote(tiffPath, threshold, scaleTo = 255, saveAs = os.path.join(outputFolder, os.path.basename(tiffPath)) ))
        elif task == "histogramming":
            workScheduleForRayWorkers.append( getHistogram.remote(tiffPath, nBins , binRange) )

        

        #tiffArray = tiffArray.astype(np.float32)

        #tempHist = getHistogram(tiffArray, nBins , binRange)


        print("Scheduled: %i out of %i" %(index+1, len(tiffTuple))) 

        #if index > 100: break

    
    #tempHists = []
    # add progress bar:
    # https://discuss.ray.io/t/use-tqdm-ray-in-remote-tasks/11175
    rayoutput = ray.get(workScheduleForRayWorkers)

    ray.shutdown() # shutdown Ray to release resources and memory

    print("Time taken: %f" %(time.time()-startTime))

    

    if task == "thresholdMap":

        print("Fractional fill: %f" %(np.mean(rayoutput)))

    elif task == "histogramming":

        for tempHist in rayoutput:
            hist = hist+tempHist[0]

        print("Making histograms")

        # plot this hist histogram as bar graph
        plt.figure()
        plt.bar(binEdges[:-1], hist, width=1)
        plt.savefig("histogram_tiffstack.png")

        # make y axis logarithmic
        #plt.figure()
        #plt.bar(binEdges[:-1], hist, width=1)
        plt.yscale('log')
        plt.savefig("histogram_tiffstack_log.png")

        plt.figure()
        plt.bar(binEdges[0:100], hist[0:100], width=1)
        plt.savefig("histogram_tiffstack0_100.png")

        plt.yscale('log')
        plt.savefig("histogram_tiffstack0_100_log.png")

        plt.figure()
        plt.bar(binEdges[0:200], hist[0:200], width=1)
        plt.savefig("histogram_tiffstack0_200.png")

        plt.yscale('log')
        plt.savefig("histogram_tiffstack0_200_log.png")

        plt.figure()
        plt.bar(binEdges[0:1000], hist[0:1000], width=1)
        plt.savefig("histogram_tiffstack0_1000.png")

        plt.yscale('log')
        plt.savefig("histogram_tiffstack0_1000_log.png")
        

    pass