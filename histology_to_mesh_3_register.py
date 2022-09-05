'''
Part 3. Register contours
'''

import os
import sys
import numpy as np
import igl
sys.path.append("/Users/roberto/Documents/annex-ferret-histology/bin/microdraw.py/")
import microdraw as mic

def load_intermediate_mesh(destination):
    '''load intermediate mesh (registration target)'''
    path = os.path.join(destination, "5_intermediate_mesh.ply")
    verts, tris = igl.read_triangle_mesh(path)

    path = os.path.join(destination, "6_displacement.npz")
    displacement = np.load(path, allow_pickle=True)["displacement"]

    return verts, tris, displacement

def _register_contours(verts, tris, displacement, voxdim, destination):
    '''register microdraw contours to mesh slices'''
    path = os.path.join(destination, "1_all_regions.npz")
    all_regions = np.load(path, allow_pickle=True)["all_regions"].tolist()

    reg_contours = []
    for slice_index in range(all_regions["numSlices"]):
        print("Registering slice %i"%(slice_index))

        # slice annotations
        regions = mic.get_regions_from_dataset_slice(all_regions["slices"][slice_index])

        # corresponding mesh slice
        unique_verts, _, _, lines = mic.mesh.slice_mesh(
            verts, tris, (slice_index-displacement[2])*voxdim[2])

        if unique_verts is None:
            print("Mesh slice empty")
            continue

        manual = [region for name, region, _ in regions if name in ["Region 1", "Region 2"]]
        auto = [(unique_verts[line]/voxdim[0] + displacement)[:, :2] for line in lines]
        corresp = mic.find_contour_correspondences(manual, auto)

        registered = mic.register_contours(manual, auto) #, corresp)
        reg_contours.append(registered)
        print()

    return reg_contours

def register_contours(
    voxdim=None,
    destination=None,
    overwrite=False):
    '''register microdraw contours to mesh slices'''

    dst = os.path.join(destination, "7_registered_contours.npz")
    if not overwrite and os.path.exists(dst):
        print('''Skipping. There are previously computed registered \
contours (set overwrite=True to compute them again).''')
        return
    print("Registering contours")

    verts, tris, displacement = load_intermediate_mesh(destination)

    reg_contours = _register_contours(
        verts, tris, displacement, voxdim, destination)

    path = os.path.join(destination, "7_registered_contours.npz")
    np.savez_compressed(
        path,
        allow_pickle=True,
        registered_contours=reg_contours)
