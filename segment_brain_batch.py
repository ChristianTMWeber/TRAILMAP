from inference import *
from models import *
import sys
import os
import shutil
import argparse # to parse command line options

from auxiliaryMethods.rescale9xImagesTo3xImages import rescaleImagesFromFolder



def initilizeArgParser( parser = argparse.ArgumentParser(
    description="") ):

    parser.add_argument("foldersToSegment", type=str,nargs='*',
        help="List of folders that we want to segment" )

    parser.add_argument("-o","--outputFolders", type=str, nargs='*', required = False , 
        help="Folder where we store the segmentation map \
        This is an optional argument.\
        If this argument is not provided, we will output the each segmentation map to \
        <path_to_n-th_input>\\seg-<top_level_n-th_input>.")

    parser.add_argument( "--doRescale", default=False, action= 'store_true' , required = False , 
    help = "The trailmap algorithm was trained on images with an resolution \
    of about 1.8 micro meter along x and y. \
    Thus it only works well with images that have a similar resolution. \
    Use this option '--doRescale' together with '--rescaleFactor' to automatically \
    rescale the images to a suitable resolutoin" )

    parser.add_argument( "--rescaleFactor", type=str, default=0.7/1.8, required = False , 
    help = "Sets the factor by which we downscale the resolution when the\
     '--doRescale' options is used. \
    To downscale from a 9x maginification to the appropriate resultion use \
    a factor of 0.7/1.8 ~ 0.39. \
    0.7 is here the source resolution of about 0.7 micro meter along x and y\
    and 1.8 micro meter is the target resolution.\
    So scaling factors smaller than one will reduce the resolution." )


    parser.add_argument( "--nCPUs", type=int, default=None, required = False , 
    help = "Number of CPU cores we use for the rescaling. \
    By default we use a quarter of the available logical CPU cores." )
    


    args = parser.parse_args()


    if args.outputFolders is not None:
        assert len(args.foldersToSegment) == len(args.outputFolders), \
        "should have same number of input folders as output folders"

    return args


if __name__ == "__main__":


    #import pdb; pdb.set_trace()

    args = initilizeArgParser()

    base_path = os.path.abspath(__file__ + "/..")

    #input_batch = sys.argv[1:]
    ## Verify each path is a directory
    #for input_folder in input_batch:
    #    if not os.path.isdir(input_folder):
    #        raise Exception(input_folder + " is not a directory. Inputs must be a folder of files. Please refer to readme for more info")

    # Load the network
    weights_path = base_path + "/data/model-weights/trailmap_model.hdf5"

    model = get_net()
    model.load_weights(weights_path)

    for folderIndex , input_folder in enumerate(args.foldersToSegment):

        #import pdb; pdb.set_trace() # import the debugger and instruct it to stop here

        input_folder = os.path.realpath(input_folder)

        assert os.path.isdir(input_folder)

        # Remove trailing slashes
        input_folder = os.path.normpath(input_folder)


        # setup the rescaling
        rescale_name = "rescale-" + os.path.basename(input_folder)
        rescale_dir = os.path.dirname(input_folder)
        rescale_folder = os.path.join(rescale_dir, rescale_name)

        nCPUs = args.nCPUs
        if args.nCPUs is None: nCPUs = os.cpu_count()//4 


        if args.doRescale:
            rescaleImagesFromFolder( input_folder , rescale_folder,  scaleFactor = args.rescaleFactor, nCPUs = nCPUs )

        # Output folder name

        if args.outputFolders is None:
            output_name = "seg-" + os.path.basename(input_folder)
            output_dir = os.path.dirname(input_folder)
            output_folder = os.path.join(output_dir, output_name)

        else:

            output_folder = os.path.realpath( args.outputFolders[folderIndex] )

        #print( "\n\n\nUSING TEMP OUTPUT FOLDER\n\n\n")
        #output_folder="/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/Chung_59405_9x-1umZstep_RightHemi_DBH/647nm_DBH_segmentation"


        # Create output directory. Overwrite if the directory exists
        if os.path.exists(output_folder):
            print(output_folder + " already exists. Will be overwritten")
            shutil.rmtree(output_folder)

        os.makedirs(output_folder)

        segmentationInput = input_folder

        if args.doRescale: segmentationInput=rescale_folder

        # Segment the brain
        segment_brain(segmentationInput, output_folder, model)

