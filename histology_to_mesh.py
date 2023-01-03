'''histology_to_mesh.py'''

import sys
import os
import histology_to_mesh_1_download as io
import histology_to_mesh_2_intermediate_mesh as mesh
import histology_to_mesh_3_register as register
import histology_to_mesh_4_mask as mask
import histology_to_mesh_5_final_mesh as final
import histology_to_mesh_6_ui as ui

def histology_to_mesh(
    project=None,
    source=None,
    token=None,
    regions=None,
    voxdim=None,
    level=0,
    destination=None,
    overwrite=False
):
    '''
    3D mesh reconstruction from Microdraw segmentation
    '''

    destination = os.path.expanduser(destination)
    destination = os.path.abspath(destination)

    print(f"    project: {project}")
    print(f"     source: {source}")
    print(f"      token: {token}")
    print(f"    regions: {regions}")
    print(f"     voxdim: {voxdim}")
    print(f"      level: {level}")
    print(f"destination: {destination}")
    print(f"  overwrite: {overwrite}")

    print("1. download")
    io.download_from_microdraw_and_save(
        project=project,
        source=source,
        token=token,
        destination=destination,
        overwrite=overwrite
    )

    print("2. make intermediate mesh")
    mesh.make_intermediate_mesh(
        regions=regions,
        voxdim=voxdim,
        destination=destination,
        overwrite=overwrite
    )

    print("3. register contours")
    register.register_contours(
        voxdim=voxdim,
        destination=destination,
        overwrite=overwrite)
    
    print("4. compute final mask")
    mask.compute_final_mask(
        voxdim=voxdim,
        destination=destination,
        overwrite=overwrite
    )

    print("5. make final mesh")
    final.make_final_mesh(
        voxdim=voxdim,
        level=level,
        destination=destination,
        overwrite=overwrite
    )

    print("6. make ui for manual adjustment")
    ui.make_ui(
        os.path.join(destination, "7_registered_contours.npz"),
        os.path.join(destination, "12_ui.html")
    )
    print("done.")

def main(argv):
  '''convenience histology_to_mesh call from the command line'''
  _, project, source, token, regions, voxdim, level, destination, overwrite = argv

  regions = regions.split(",")
  voxdim = [float(s) for s in voxdim.split(",")]
  overwrite = overwrite=="True"

  print(f"    project: {project}")
  print(f"     source: {source}")
  print(f"      token: {token}")
  print(f"    regions: {regions}")
  print(f"     voxdim: {voxdim}")
  print(f"      level: {level}")
  print(f"destination: {destination}")
  print(f"  overwrite: {overwrite}")

  histology_to_mesh(project, source, token, regions,
    voxdim, level, destination, overwrite)

if __name__ == "__main__":
  main(sys.argv)