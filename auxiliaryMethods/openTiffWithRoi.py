import tifffile
import numpy as np

import struct
import skimage

import matplotlib.pyplot as plt

from skimage.draw import polygon

## https://github.com/dwaithe/ijpython_roi
## python -m pip install ijroipytiff
#import ijroipytiff
#import ijroipytiff.ijpython_decoder as ijpython_decoder
#from ijroipytiff.ijpython_decoder import decode_ij_roi
#from ijroipytiff.ij_roi import Roi
#from ijroipytiff.ij_ovalroi import OvalRoi


def create_mask_from_metadata(image_shape, interpreted_data):
    mask = np.zeros(image_shape, dtype=np.uint8)
    
    # Example of how to interpret the metadata (assuming polygon coordinates are encoded)
    # This step will vary based on actual metadata structure
    coordinates = []  # Replace this with actual extraction logic
    for i in range(0, len(interpreted_data), 2):
        x = interpreted_data[i]
        y = interpreted_data[i+1]
        coordinates.append((x, y))
    
    rr, cc = polygon([coord[1] for coord in coordinates], [coord[0] for coord in coordinates], mask.shape)
    mask[rr, cc] = 1
    return mask



# Helper function to interpret IJMetadata
def interpret_ij_metadata(ij_metadata):
    try:
        # Assume IJMetadata is a binary string
        data = struct.unpack('B' * len(ij_metadata), ij_metadata)
        return data
    except Exception as e:
        print("Error interpreting IJMetadata:", e)
        return None

if __name__ == "__main__":


    tiffPath = "/home/chweber/ssd1_chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_sagittal_section_bran_region_labeling/max projection/MAX_639nm_DBH_rescaled_by_0.389_8bit_xSlices_2350_to_3100.tif"

    tiffArray = tifffile.imread(tiffPath)

    tifffile.TiffFile(tiffPath)

    metaDataDict = {}

    with tifffile.TiffFile(tiffPath) as tif:
        # Print TIFF file information
        #tif_info = tif.info()

        for tag in tif.pages[0].tags: 
            metaDataDict[tag.name] = tag.value


    overlay0 = interpret_ij_metadata(metaDataDict['IJMetadata']['Overlays'][0])

    mask = create_mask_from_metadata(tiffArray.shape, overlay0)


    #plt.imshow(mask)
    #plt.savefig("mask.png")

    interpret_ij_metadata(metaDataDict['IJMetadata']['ROI'])





    # Open the image with ImageJ
    #image = IJ.openImage(tiffPath)
    #roi = image.getRoi()

    #roiFile = "/home/chweber/ssd1_chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_sagittal_section_bran_region_labeling/zstack/639nm_DBH_rescaled_by_0.389_8bit_xSlices_2350_to_3100.roi"
    #roiFile = "/home/chweber/ssd1_chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_sagittal_section_bran_region_labeling/max projection/MAX_639nm_DBH_ROI_set/TH.roi"
    roiFile = "/home/chweber/ssd1_chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_sagittal_section_bran_region_labeling/max projection/MAX_639nm_DBH_ROI_set/HY.roi"

    #https://github.com/cgohlke/roifile
    #python -m pip install -U "roifile[all]"

    import roifile

    roi2 = roifile.ImagejRoi.fromfile(roiFile)

    plt.figure()
    roi2.plot()
    plt.savefig("roi.png")


    ROICoordinates = roi2.coordinates()
    #ROICoordinates.appen(ROICoordinates[0,:]) # close the polygon

    mask = np.zeros(tiffArray.shape, dtype=np.uint8)

    maskPolygon = skimage.draw.polygon(ROICoordinates[:,1], ROICoordinates[:,0],tiffArray.shape)

    mask[maskPolygon] = 1

    plt.figure()
    plt.imshow(mask)
    plt.savefig("mask.png")
    pass