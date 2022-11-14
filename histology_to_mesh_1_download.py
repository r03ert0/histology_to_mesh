'''
Part 1: Download and save all regions from microdraw
'''

import os
import sys
import numpy as np
sys.path.append("./bin/microdraw.py/")
import microdraw as mic

def download_from_microdraw_and_save(
        project,
        source,
        token,
        destination,
        overwrite=False):
    '''download and save region data for a given source, project'''

    dst = os.path.join(destination, "1_all_regions.npz")
    if not overwrite and os.path.exists(dst):
        print('''Skipping. There are previously downloaded regions \
(set overwrite=True to download them again).''')
        return
    print("Downloading all regions")

    if not os.path.exists(destination):
        os.makedirs(destination, exist_ok=True)

    all_regions = mic.download_all_regions_from_dataset(source, project, token)
    np.savez_compressed(dst, all_regions=all_regions)
