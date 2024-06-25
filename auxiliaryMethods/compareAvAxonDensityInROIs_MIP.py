import numpy as np
import tifffile
import os
import re

import collections

import zipfile

import skimage

import roifile
import csv

import matplotlib.pyplot as plt

import ray

import time


def unzip_RIOs(ROI_parent_path):

    RIOfile_Names = set()

    Image_ROIpath_Map = {}

    for root, dirs, files in os.walk(ROI_parent_path):

        gotZip = False
        for file in files:
            if file.endswith(".zip"):
                gotZip = True
                zip_path = os.path.join(root, file)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(root)

        if gotZip:
            Image_ROIpath_Map[os.path.basename(root)] = root

        roi_files = [x for x in os.listdir(root) if x.endswith(".roi")]

        RIOfile_Names.update(roi_files)

    for root, dirs, files in os.walk(ROI_parent_path):

        if not any([x.endswith(".zip") for x in files]): continue

        for roi_files in RIOfile_Names:
            if roi_files not in files:
                print("ROI file %s not found in %s" %(roi_files, root))


    return Image_ROIpath_Map, sorted(list(RIOfile_Names))

def mapImageNamesToSegmentations(imagePath, segmentationPath):

    tiffEnding = "\.tif{1,2}"

    def getFilesWithEndingInFolder(folderPath, ending = "\.tif{1,2}" ):
        files = [x for x in os.listdir(folderPath) if re.search(ending,x)]
        return files

    #    images = [x for x in os.listdir(impagePath) if re.search(tiffTag,x)]

    images        = sorted(getFilesWithEndingInFolder(imagePath))
    segmentations = sorted(getFilesWithEndingInFolder(segmentationPath))

    imageToSegmentationMap = {}

    for img, seg in zip(images, segmentations):

        # remove file ending of img
        img = re.sub(tiffEnding,"",img)

        imageToSegmentationMap[img] = os.path.join(segmentationPath, seg)

    return imageToSegmentationMap

def yieldSegmentationTiffs(segmentationPath):

    tiffEnding = "\.tif{1,2}"

    def getFilesWithEndingInFolder(folderPath, ending = "\.tif{1,2}" ):
        files = [x for x in os.listdir(folderPath) if re.search(ending,x)]
        return files

    segmentations = sorted(getFilesWithEndingInFolder(segmentationPath))

    for seg in segmentations:

        yield os.path.join(segmentationPath, seg)

def get_ROI_Mask(ROI_file, maskSize):

    roiObj = roifile.ImagejRoi.fromfile(ROI_file)

    ROICoordinates = roiObj.coordinates()

    mask = np.zeros(maskSize, dtype=bool)

    maskPolygon = skimage.draw.polygon(ROICoordinates[:,1], ROICoordinates[:,0],maskSize)

    mask[maskPolygon] = 1

    return mask

@ray.remote # this decorator tells Ray to parallelize this function
def get_AxonCountWithinRoi(ROIpath, segmentation, ROI_file):

    segmentationArray = tifffile.imread(segmentation)

    # check if file exists
    if os.path.exists(os.path.join(ROIpath,ROI_file)):
        ROI_mask = get_ROI_Mask( os.path.join(ROIpath,ROI_file), segmentationArray.shape)
    else:
        ROI_mask = np.zeros(segmentationArray.shape, dtype=bool)

    roiVoxelContent = segmentationArray[ROI_mask]

    return ROI_file, roiVoxelContent



def calculateDensityInROI(ROIpath_segmentationTuple, ROIFileNames):

    ROI_axonCountDict = collections.defaultdict(list)

    workScheduleForRayWorkers = []

    for ROIpath, segmentation in ROIpath_segmentationTuple:

        for ROI_file in ROIFileNames:

            #print( ROIpath, segmentation, ROI_file )

            workScheduleForRayWorkers.append( get_AxonCountWithinRoi.remote(ROIpath, segmentation, ROI_file))

    startTime = time.time()
    print("Starting the work")
    rayoutput = ray.get(workScheduleForRayWorkers)
    print("Got the output in %.2f" %(time.time()-startTime) )

    for ROI_file, roiAxons in rayoutput:

        ROI_axonCountDict[ROI_file].extend(roiAxons)
    
    axonDensityDict = calculateAxonDensityFromCounts(ROI_axonCountDict)

    return axonDensityDict


def calculateAxonDensityFromCounts(ROI_axonCountDict):

    axonDensityDict = {}

    for ROI_fileName , axonCounts in ROI_axonCountDict.items():
        axonCounts = np.array(axonCounts)

        axonDensity = np.mean(axonCounts)

        axonDensityDict[ROI_fileName] = axonDensity

    return axonDensityDict





def writeAxonDensityToCSV(output_file = "axonDensity.csv"):

    # save the axonDensityDict to a csv file
    # Specify the path to the output CSV file

    # Write the axonDensityDict to the CSV file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ROI_fileName', 'axonDensity'])
        for ROI_fileName, axonDensity in axonDensityDict.items():
            writer.writerow([ROI_fileName, axonDensity])

    print("Axon density data saved to", output_file)

    

if __name__ == "__main__":

    ray.init(num_cpus=32) # Initialize Ray with some number of workers


    ### Wild type ###

    # images
    wildTypeData = {
    "images"        :"/media/ssdshare2/general/Lorenzo/20240503_13_42_22_5617_WT_001/20240514_11_49_16_57622_WT_stitched/Ex_642_Ch2_MIP_stitched",
    "segmentation"  :"/media/ssdshare2/general/Lorenzo/20240503_13_42_22_5617_WT_001/20240514_11_49_16_57622_WT_stitched/Ex_642_Ch2_MIP_stitched_rescaled_by_1.000_histMatched_SlaytonSegmentation/axon_tiffs",
    "RIO_zip"       :"/media/ssdshare2/general/Lorenzo/20240503_13_42_22_5617_WT_001/20240514_11_49_16_57622_WT_stitched/labled_Ex_642_Ch2_MIP_stitched"
    }



    ### Knock In ###
    # images
    knockInData = {
    "images"        :"/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_500umMIPs",
    "segmentation"  :"/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_500umMIPs_SlaytonSegmentation/axon_tiffs",
    "RIO_zip"       :"/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/labeled_639nm_DBH_500umMIPs"
    }

    #currentDict = wildTypeData

    for currentDict in [wildTypeData, knockInData]:

        currentDict["imgToSegMap"] =  mapImageNamesToSegmentations(currentDict["images"], currentDict["segmentation"])

        Image_ROIpath_Map, RIOfile_Names =unzip_RIOs(currentDict["RIO_zip"])

        currentDict["Image_ROIpath_Map"] = Image_ROIpath_Map
        currentDict["RIOfile_Names"] = RIOfile_Names

        # get tuples of (ROI_path, segmentationImagePath)
        relevantSegmentations = [(currentDict["Image_ROIpath_Map"][imgName],currentDict["imgToSegMap"][imgName]) for imgName in sorted(currentDict["Image_ROIpath_Map"])]   

        axonDensityDict = calculateDensityInROI(relevantSegmentations, currentDict["RIOfile_Names"])

        currentDict["axonDensityDict"] = axonDensityDict


    brainRegionAbreviationMap={
        "ACB": "Nucleus\nAccumbens",
        "HY": "Hypothalamus",
        "HPF": "Hippocampal\nFormation",
        "CTX": "Cortex",
        "CP": "Caudate\nPutamen",
        "TH": "Thalamus",
        }

    # Iterate over the dictionaries and plot the bar plots

    roiKeys = sorted(list(wildTypeData["axonDensityDict"].keys()))

    xTickLabels = [brainRegionAbreviationMap[x.removesuffix('.roi')] for x in roiKeys] 
    X_axis = np.arange(len(xTickLabels)) 

    wildTypeAxonDensities = [wildTypeData["axonDensityDict"][x]*100 for x in roiKeys]
    knockInAxonDensities = [knockInData["axonDensityDict"][x]*100 for x in roiKeys]

    axonDensityDict = currentDict["axonDensityDict"]
    ROI_fileNames = list(axonDensityDict.keys())
    axonDensities = list(axonDensityDict.values())


    plt.figure()
    
    # Create a bar plot
    plt.bar(X_axis - 0.2, wildTypeAxonDensities, 0.4, label = 'Wild type') 
    plt.bar(X_axis + 0.2, knockInAxonDensities, 0.4, label = 'App knock-in') 

    #plt.xlabel('ROI_fileName')
    #plt.ylabel('Axon Density')
    plt.ylabel('Norepinephrine axon\nfiber volume fraction [%]', fontsize=16)

    # add a legend
    plt.legend(loc='upper left', fontsize=12)

    #plt.title('Axon Density')
    #plt.xticks(rotation=90)
    plt.xticks(X_axis, xTickLabels, rotation=30, horizontalalignment='right', fontsize=12)
    plt.yticks(fontsize=12)

    plt.ylim(plt.ylim()[0], plt.ylim()[1] * 1.05)

        #plt.show()
    plt.savefig("AxonDensityInROIs.png",bbox_inches='tight')
    plt.close()







    pass