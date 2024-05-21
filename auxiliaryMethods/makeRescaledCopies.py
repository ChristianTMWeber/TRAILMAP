import os
import tifffile
import skimage

import numpy as np

import matplotlib.pyplot as plt

from tiffStackArray import tiffStackArray


import copy


def writeOutImages(tiffArray , outputFolder, imgOffset = 0):

    os.makedirs(outputFolder, exist_ok=True)

    counter = 0 

    for tiffIndex in range(0, tiffArray.shape[0]):

        image = tiffArray[tiffIndex,:,:].astype(np.float32)

        image_rescaled = skimage.transform.resize(image, [303,303] , anti_aliasing=True)

        
        image_rescaled = image_rescaled.astype(np.uint16)

        outputFileName = "image_%i.tiff" %(tiffIndex + imgOffset)

        outputFilePath = os.path.join(outputFolder, outputFileName )

        tifffile.imwrite(outputFilePath, image_rescaled)

        print(outputFileName)

    print("done!")

    return None


if __name__ == "__main__":

    TrailmapImages = "/home/chweber/TRAILMAP/data/testing/example-chunk"

    trailmapImageArray = tiffStackArray(TrailmapImages)[:]

    minTrailmap = np.min(trailmapImageArray)
    maxTrailmap = np.max(trailmapImageArray)

    UO1_images = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_hpf"
    UO1ImageArray = tiffStackArray(UO1_images)[:]

    # scale the UO1 images to the range of the Trailmap images
    #UO1ImageArray_TrailmapRange = (UO1ImageArray - np.min(UO1ImageArray)) / np.max(UO1ImageArray) * (maxTrailmap - minTrailmap) + minTrailmap


    #UO1ImageArray_TrailmapMean = UO1ImageArray - np.mean(UO1ImageArray) + np.mean(trailmapImageArray)
    UO1ImageArray_TrailmapMeanStd = (UO1ImageArray - np.mean(UO1ImageArray))/np.std(UO1ImageArray)*np.std(trailmapImageArray) + np.mean(trailmapImageArray)
    
    UO1ImageArray_TrailmapHistMatched = skimage.exposure.match_histograms(UO1ImageArray, trailmapImageArray, channel_axis=None)

    #UO1ImageArray_TrailmapMeanStd_clipped = copy.copy(UO1ImageArray_TrailmapMeanStd)
    #UO1ImageArray_TrailmapMeanStd_clipped[ UO1ImageArray_TrailmapMeanStd > np.max(trailmapImageArray)] = np.max(trailmapImageArray)


    UO1ImageArray6500 = (UO1ImageArray - np.min(UO1ImageArray[0,:,:])) / np.max(UO1ImageArray[0,:,:]) * 6500

    # transform UO1ImageArray so that it follows the distribution of TrailmapImageArray via the inverse cumulative distribution function
    #UO1ImageArray_TrailmapCDF = np.interp(np.sort(UO1ImageArray), np.sort(trailmapImageArray), np.linspace(0,1,len(trailmapImageArray)))


    UO1ImageArray_TrailmapMeanStdImageWise = UO1ImageArray.astype(np.float64)
    for x in range(0, UO1ImageArray.shape[0]):
        UO1ImageArray_TrailmapMeanStdImageWise[x,:,:] = (UO1ImageArray[x,:,:] - np.mean(UO1ImageArray[x,:,:]))/np.std(UO1ImageArray[x,:,:])*np.std(trailmapImageArray) + np.mean(trailmapImageArray)
    UO1ImageArray_TrailmapMeanStdImageWise[ UO1ImageArray_TrailmapMeanStdImageWise > np.max(trailmapImageArray)] = np.max(trailmapImageArray)


    arrayDict = { "Trailmap" : trailmapImageArray, "UO1" : UO1ImageArray, 
                  "UO1_TrailmapMeanStd" : UO1ImageArray_TrailmapMeanStd, 
                  'UO1ImageArray_TrailmapHistMatched' : UO1ImageArray_TrailmapHistMatched,
                  "UO1ImageArray_TrailmapMeanStdImageWise" : UO1ImageArray_TrailmapMeanStdImageWise}


    #arrayDict = { "Trailmap" : trailmapImageArray, "UO1" : UO1ImageArray, "UO1_TrailmapRange" : UO1ImageArray_TrailmapRange,
    #              "UO1_TrailmapMean" : UO1ImageArray_TrailmapMean, "UO1_TrailmapMeanStd" : UO1ImageArray_TrailmapMeanStd,
    #              "UO1ImageArray6500" : UO1ImageArray6500, "UO1ImageArray_TrailmapMeanStdImageWise" : UO1ImageArray_TrailmapMeanStdImageWise}

    histDict = {}
    for key in arrayDict.keys():
        histDict[key] = np.histogram(arrayDict[key], bins=1000, range=(0,1e4))


    #get the 95th percentile of all the histograms
    percentileDict = {}
    for key in histDict.keys():
        percentileDict[key] = np.percentile(arrayDict[key], 99)
        
    # plot the histograms in histDict in a single plot using plt.bar
    fig, ax = plt.subplots(2,1)
    for key in histDict.keys():
        ax[0].bar(histDict[key][1][:-1], histDict[key][0]/np.max(histDict[key][0]), width=histDict[key][1][1] - histDict[key][1][0], alpha=0.5, label=key)

    ax[0].set_xlim(0, max(list(percentileDict.values())) )


    # add axes labels common do both subplots
    ax[0].set_xlabel("Pixel intensity")
    ax[0].set_ylabel("Frequency")
    # add title to the first subplot
    ax[0].set_title("Histograms of pixel intensities in Trailmap and UO1 images")


    for key in histDict.keys():
        ax[1].bar(histDict[key][1][:-1], histDict[key][0]/np.sum(histDict[key][0]), width=histDict[key][1][1] - histDict[key][1][0], alpha=0.5, label=key)
    
    ax[1].set_yscale('log')  # Set y-axis to logarithmic scale
    ax[1].set_xlabel("Pixel intensity")
    ax[1].set_ylabel("Frequency")
    ax[1].legend()


    # add a title to the plot

    # save the plot to file
    fig.savefig("histograms.png")




    writeOutImages(arrayDict["UO1_TrailmapMean"]            , "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_hpf_TrailmapMean_rescaled", imgOffset = 1500)
    writeOutImages(arrayDict["UO1_TrailmapMeanStd_clipped"] , "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_hpf_TrailmapMeanStd_rescaled", imgOffset = 1500)
    writeOutImages(arrayDict["UO1ImageArray_TrailmapMeanStdImageWise"] , "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_hpf_TrailmapMeanStdPerImage_rescaled", imgOffset = 1500)
    writeOutImages(arrayDict["UO1ImageArray_TrailmapHistMatched"] , "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_hpf_TrailmapHistMatched_rescaled", imgOffset = 1500)

    





    inputFolder = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_hpf"

    outputFolder = inputFolder + "_rescaled_for_Trailmap"

    os.makedirs(outputFolder, exist_ok=True)

    counter = 0 


    maxRange = 1

    minRange=0

    #for file in sorted(os.listdir(inputFolder)): 
    for fileIndex in range(1500,1623+64):

        file = "image_%i.tiff" %fileIndex
        
        image = tifffile.imread(os.path.join(inputFolder,file))

        #image_rescaled = skimage.transform.rescale(image, 0.1723 , anti_aliasing=True)
        image_rescaled = skimage.transform.resize(image, [303,303] , anti_aliasing=True)



        if counter ==0: 
            maxRange =  np.max(image_rescaled)
            minRange =  np.min(image_rescaled)

        #image_rescaled = skimage.exposure.equalize_hist(image_rescaled, nbins=256, mask=None)

        image_rescaled = (image_rescaled - minRange) / maxRange * 65000

        #image_rescaled = (image_rescaled - np.min(image_rescaled)) / np.max(image_rescaled) * 6500

        image_rescaled = image_rescaled.astype(np.uint16)

        #image_rescaled *= 255 

        #image_rescaled = image_rescaled.astype(np.uint8)

        outputFileName = os.path.join(outputFolder, file)

        #import pdb; pdb.set_trace()

        tifffile.imwrite(outputFileName, image_rescaled)

        print(file)

        counter += 1
        


    #os.path.dirname(inputFolder)

    print("done!")
