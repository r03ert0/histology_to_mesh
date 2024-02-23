'''
Part 5. Mesh from registered contours' SDF
'''
import os
import numpy as np
import nibabel as nib
from scipy.ndimage import distance_transform_edt
import igl
from skimage.filters import gaussian
from skimage import measure, transform, restoration

def make_sdf(destination, scale=1.0, z_padding = 20):
    '''make sdf from mask'''
    path = os.path.join(destination, "8_final_mask.nii.gz")
    nii_registered = nib.load(path)
    img_registered = nii_registered.get_fdata()

    print('''@todo The mask volume is tight around the object.
    The sdf here and its smoothing could use some offset.
    ''')

    img_padded = np.zeros((
        img_registered.shape[0],
        img_registered.shape[1],
        img_registered.shape[2] + 2*z_padding
    ))
    img_padded[:,:,z_padding:-z_padding] = img_registered

    # make sdf volume
    # nimg_padded = img_padded == 0
    # pos_registered = distance_transform_edt(img_padded)
    # neg_registered = distance_transform_edt(nimg_padded)
    # res_registered = pos_registered - neg_registered
    res_registered = np.array(img_padded, dtype=np.float32)

    # rescaling
    img1 = transform.rescale(gaussian(res_registered, sigma=[4, 4, 2]), [1, 1, scale])
    print("img1:", img1.min(), img1.max(), img1.sum())

    # simple copy
    res = img1

    # # high-pass filtering
    # img2 = gaussian(img1, sigma=[8, 8, 4])
    # print("img2:", img2.min(), img2.max(), img2.sum())
    # res = (img1 - 0.85 * img2)
    # print("rescaled:", res.min(), res.max(), res.sum())

    # # non-local means: 6h to finish!
    # res = restoration.denoise_nl_means(img1, fast_mode=True)

    # shift boundary
    res -= 5.0 # nctx
    # res -= 0.5 # gw

    # sigmoidal clipping
    half_width = 2.0
    a = -np.log(1/3)/half_width
    res = 2/(1 + np.exp(-a * res)) - 1

    # rescaling values, to save as int16
    res *= 1000

    # print("clipped:", res.min(), res.max())

    return res

def make_mesh(sdf, voxdim, original_center, level=0):
    '''make the final mesh'''
    print("@todo: make_mesh in hm_5 is identical to compute_mesh in hm_2")
    v_registered, f_registered, _, _ = measure.marching_cubes(
        sdf, spacing=voxdim, level=level,
        gradient_direction="ascent")

    # transform to match space
    mesh_center = (np.min(v_registered, axis=0) + np.max(v_registered, axis=0))/2
    print("mesh center:", mesh_center)
    displacement = original_center - mesh_center/voxdim

    # decimate
    success, verts, f_1, _, _ = igl.decimate(v_registered, f_registered, 20000)
    print("decimation success:", success)

    # improve triangulation
    edge_lengths = igl.edge_lengths(verts, f_1)
    _, tris = igl.intrinsic_delaunay_triangulation(edge_lengths, f_1)

    return verts, tris, displacement

def make_final_mesh(
        voxdim=None,
        destination=None,
        level=0,
        overwrite=False):
    '''make final mesh'''

    dst = os.path.join(destination, "10_final_mesh.ply")
    if not overwrite and os.path.exists(dst):
        print('''Skipping. There is a previously computed final \
mesh (set overwrite=True to compute it again).''')
        return
    print("Computing the final mesh")

    scale = 4.0
    z_padding = 20
    sdf = make_sdf(destination, scale, z_padding)
    if len(sdf.shape) == 4:
        sdf = sdf[:,:,:,0]
    affine = np.eye(4)
    affine[0, 0] = voxdim[0]
    affine[1, 1] = voxdim[1]
    affine[2, 2] = voxdim[2]/scale
    print(affine)
    print(sdf.shape)
    nii = nib.Nifti1Image(sdf.astype(np.int16), affine=affine)
    nib.save(nii, os.path.join(destination, "8_final_sdf_padded.nii.gz"))

    path = os.path.join(destination, "9_contours_center.npz")
    original_center = np.load(path, allow_pickle=True)["contours_center"]

    verts, tris, displacement = make_mesh(sdf, [voxdim[0], voxdim[1], voxdim[2]/scale], original_center, level)
    igl.write_triangle_mesh(dst, verts, tris, force_ascii=False)
    path = os.path.join(destination, "11_displacement.npz")
    np.savez_compressed(path, displacement=displacement)

