#!/bin/bash



TiffSource="/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Autofluorescence-MOAB_4x/445nm_Autofluorescence/*.tif*"

PrecompTiffTarget="/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Autofluorescence-MOAB_4x/445nm_Autofluorescence_precomp"

NeuroGlancerName="Tsai_MouseBrain57611_Autofluorescence"





### setup the necessary conda environment
source /home/build/anaconda3/bin/activate chunglab-stack
conda activate chunglab-stack

### precompute the tiffs, those precomputed tiffs will be linked against the database

time precomputed-tif --source "$TiffSource"  --dest "$PrecompTiffTarget" --format blockfs --n-cores 20 --levels 8

### link against the database
python /media/share7/add_source.py --name $NeuroGlancerName --directory $PrecompTiffTarget 

### get the neuroglancer url
/media/share7/neuroglancer_url.py $NeuroGlancerName green 60