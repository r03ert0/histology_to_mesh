'''Part 2: Mesh from the downloaded regions'''

import os
import sys
import nibabel as nib
import matplotlib.pyplot as plt
from scipy.ndimage import distance_transform_edt
from skimage.filters import gaussian
from skimage import measure
import igl
import numpy as np

sys.path.append("./bin/microdraw.py/")
import microdraw as mic
mic.version()

def load_all_regions(path):
    '''load all regions from file'''
    return np.load(path, allow_pickle=True)["all_regions"].tolist()

def save_reference_image(all_regions, destination):
    '''save reference with all regions'''
    path = os.path.join(destination, "2_all_regions.svg")
    fig = plt.figure()
    mic.draw_all_dataset(all_regions)
    plt.savefig(path)
    plt.close(fig)

def compute_mask_volume(all_regions, regions, voxdim):
    '''make mask nifti'''

    verts_mic, _ = mic.dataset_as_volume(all_regions)
    vmin_mic, vmax_mic = np.min(verts_mic, axis=0), np.max(verts_mic, axis=0)
    vmin_mic = np.floor(vmin_mic)
    vmax_mic = np.ceil(vmax_mic)
    center_mic = (vmax_mic + vmin_mic)/2
    print("contours min:", vmin_mic)
    print("contours max:", vmax_mic)
    print("contours center:", center_mic)

    # voxdim = np.array([0.1, 0.1, 1.25])
    nii_mic = mic.dataset_to_nifti(all_regions, voxdim=voxdim, region_name=regions)
    print("nifti shape:", nii_mic.shape)
    print("nifti sum:", np.sum(nii_mic.get_fdata())/1000)

    return nii_mic, center_mic

def compute_sdf(mask):
    '''make SDF'''
    img_mic = mask.get_fdata()
    nimg_mic = img_mic == 0
    pos_mic = distance_transform_edt(img_mic)
    neg_mic = distance_transform_edt(nimg_mic)
    res_mic = pos_mic - neg_mic

    return gaussian(res_mic, sigma=5)

def save_sdf_as_nii(img, voxdim, destination):
    '''save sdf as nifti volume'''
    affine = np.eye(4)
    affine[0, 0] = voxdim[0]
    affine[1, 1] = voxdim[1]
    affine[2, 2] = voxdim[2]
    nii = nib.Nifti1Image(img.astype(np.float32), affine=affine)
    path = os.path.join(destination, "4_sdf.nii.gz")
    nib.save(nii, path)

def compute_mesh(sdf, voxdim, original_center):
    '''make the intermediate mesh'''

    print("@todo: compute_mesh in hm_2 is identical to make_mesh in hm_5")

    v_marching_cubes, f_marching_cubes, _, _ = measure.marching_cubes(
        sdf, 0, spacing=voxdim,
        gradient_direction="ascent")

    # transform to match space
    mesh_center = (np.min(v_marching_cubes, axis=0) + np.max(v_marching_cubes, axis=0))/2
    print("mesh center:", mesh_center)
    displacement = original_center - mesh_center/voxdim

    # decimate
    success, verts, f_1, _, _ = igl.decimate(v_marching_cubes, f_marching_cubes, 10000)
    print("decimation success:", success)

    # improve triangulation
    edge_lengths = igl.edge_lengths(verts, f_1)
    _, tris = igl.intrinsic_delaunay_triangulation(edge_lengths, f_1)

    return verts, tris, displacement

def make_intermediate_mesh(
        regions=None,
        voxdim=None,
        destination=None,
        overwrite=False):
    '''make intermediate mesh from microdraw regions'''

    dst = os.path.join(destination, "6_displacement.npz")
    if not overwrite and os.path.exists(dst):
        print('''Skipping. There is a previously computed mesh \
(set overwrite=True to compute it again).''')
        return
    print("Making intermediate mesh")

    path = os.path.join(destination, "1_all_regions.npz")
    all_regions = load_all_regions(path)

    save_reference_image(all_regions, destination)

    nii_mic, original_center = compute_mask_volume(all_regions, regions, voxdim)
    path = os.path.join(destination, "3_mask.nii.gz")
    nib.save(nii_mic, path)

    smo_mic = compute_sdf(nii_mic)

    save_sdf_as_nii(smo_mic, voxdim, destination)

    verts, tris, displacement = compute_mesh(smo_mic, voxdim, original_center)
    path = os.path.join(destination, "5_intermediate_mesh.ply")
    igl.write_triangle_mesh(path, verts, tris, force_ascii=False)
    path = os.path.join(destination, "6_displacement.npz")
    np.savez_compressed(path, displacement=displacement)
