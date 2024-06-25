import tifffile
import os
import numpy as np

import roifile
import skimage

import matplotlib.pyplot as plt

import re

from tiffStackArray import tiffStackArray

import collections


def getListOfRoiFiles(roiFolder):
    roiFiles = []
    for root, dirs, files in os.walk(roiFolder):
        for file in files:
            if file.endswith(".roi"):
                roiFiles.append(os.path.join(root, file))
    return roiFiles


def get_ROI_Mask(ROI_file, maskSize):

    roiObj = roifile.ImagejRoi.fromfile(ROI_file)

    ROICoordinates = roiObj.coordinates()

    mask = np.zeros(maskSize, dtype=bool)

    maskPolygon = skimage.draw.polygon(ROICoordinates[:,1], ROICoordinates[:,0],maskSize)

    mask[maskPolygon] = 1

    return mask


def get_ROI_Masks_from_Folder(roiFolder, maskSize):

    roiFiles = getListOfRoiFiles(roiFolder)

    roiMasks = {}
    for roiFile in roiFiles:
        roiMasks[os.path.basename(roiFile)] = get_ROI_Mask(roiFile, maskSize)

    return roiMasks


def plot_ROI_Mask(ROI_mask_dict):

    for roiName, roiMask in ROI_mask_dict.items():
        plt.figure()
        plt.imshow(roiMask)
        plt.title(roiName)
        plt.savefig(roiName+".png")
        plt.close()

    return None


def determineTIFFSlice( annotationTiffFolder ):

    # get name of last folder in path
    folderName = os.path.basename(annotationTiffFolder)

    # regular expression for digits before "_to_"
    sliceStart = re.search(r'\d+(?=_to_)', folderName).group()
    sliceEnd = re.search(r'(?<=_to_)\d+', folderName).group()

    selectiveSlice = slice(int(sliceStart), int(sliceEnd)+1)

    if "xSlices" in folderName:
        sliceTuple = (slice(None),slice(None),selectiveSlice)
        sliceDimension = 2
    elif "ySlices" in folderName:
        sliceTuple = (slice(None),selectiveSlice,slice(None))
        sliceDimension = 1
    else:
        raise ValueError("This function only works for x or y slices")
    
    return sliceTuple, sliceDimension

if __name__ == "__main__":

    tiffPath = "/home/chweber/ssd1_chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_sagittal_section_bran_region_labeling/max projection/MAX_639nm_DBH_rescaled_by_0.389_8bit_xSlices_2350_to_3100.tif"


    # create a np array of size 3 by 3 filled with random values
    randomArray = np.random.rand(3, 3)


    tempTiffArray = tifffile.imread(tiffPath)

    axonDensityDict = collections.defaultdict(list)

    # the folder that that contains the files on which Lorenzo based the annotations
    annotationInputFolder = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_rescaled_by_0.389_8bit_xSlices_2350_to_3100"
    # slice the segmentation tiff stack this way to match the dimension of the annotation tiff stack
    # the sliceDimension is the dimension that is sliced, the sliceTuple is the actual slice
    sliceTuple, sliceDimension = determineTIFFSlice( annotationInputFolder )

    roiFolder = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_sagittal_section_bran_region_labeling/max projection/MAX_639nm_DBH_ROI_set"
    ROI_mask_dict = get_ROI_Masks_from_Folder(roiFolder, tempTiffArray.shape)
    plot_ROI_Mask(ROI_mask_dict)



    segmentationTiffPath = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_rescaled_by_0.389_histMatched_segmented"

    segmentation_zStack = tiffStackArray(segmentationTiffPath)
    segmentation_Array = segmentation_zStack[sliceTuple]

    for index in range(segmentation_Array.shape[sliceDimension]):

        localSliceTuple = [slice(None),slice(None),slice(None)]
        localSliceTuple[sliceDimension] = slice(index,index+1)

        current2dArray = segmentation_Array[ tuple(localSliceTuple) ]

        for roiName, roiMask in ROI_mask_dict.items():

            roiAxons = current2dArray[roiMask]
            axonDensityDict[roiName].append(roiAxons.mean())


    for roiName, roiDensityList in axonDensityDict.items():
        print(roiName, np.mean(roiDensityList), np.std(roiDensityList))

    # Plotting the contents of axonDensityDict as bar graphs


    brainRegionAbreviationMap={
        "ACB": "Nucleus\nAccumbens",
        "HY": "Hypothalamus",
        "HPF": "Hippocampal\nFormation",
        "CTX": "Cortex",
        "CP": "Caudate\nPutamen",
        "TH": "Thalamus",
        }

    axonDensityDictForPlot = {}
    for roiName, roiDensityList in axonDensityDict.items():
        newKey = brainRegionAbreviationMap[roiName.removesuffix('.roi')]
        axonDensityDictForPlot[newKey] = np.mean(roiDensityList)*100

    plt.figure()
    plt.bar(axonDensityDictForPlot.keys(), axonDensityDictForPlot.values() )
    #plt.xlabel('ROI Name')
    plt.ylabel('Norepinephrine axon\nfiber volume fraction [%]', fontsize=16)
    #plt.title('App knock-in mouse, ', fontsize=16)
    plt.xticks(rotation=30, horizontalalignment='right', fontsize=12)
    plt.yticks(fontsize=12)

    plt.savefig("AxonDensityInROIs.png",bbox_inches='tight')
    plt.close()


    pass