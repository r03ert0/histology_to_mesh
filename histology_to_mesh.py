'''histology_to_mesh.py'''

import sys
import os
import histology_to_mesh_1_download as io
import histology_to_mesh_2_intermediate_mesh as mesh
import histology_to_mesh_3_register as register
import histology_to_mesh_4_mask as mask
import histology_to_mesh_5_final_mesh as final
import histology_to_mesh_6_ui as ui

def histology_to_mesh_wf2(
    voxdim=None,
    level=0,
    destination=None,
    overwrite=False
):
    '''
    Histology-to-mesh, workflow 2:
    Starting from registered contours, build a final 3D mesh
    with an html UI for further manual adjustment.
    '''

    destination = os.path.expanduser(destination)
    destination = os.path.abspath(destination)

    print(f"     voxdim: {voxdim}")
    print(f"      level: {level}")
    print(f"destination: {destination}")
    print(f"  overwrite: {overwrite}")
    
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

def histology_to_mesh_wf1(
    project=None,
    source=None,
    token=None,
    regions=None,
    voxdim=None,
    level=0,
    destination=None,
    overwrite=False,
    skip_step=[False, False, False, False, False, False],
):
    '''
    Histology-to-mesh, workflow 1:
    Download Microdraw annotations, align them in low frequency, and
    build a final 3D mesh with an html UI for further manual adjustment.
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

    if skip_step[0] is False:
        print("1. download")
        io.download_from_microdraw_and_save(
            project=project,
            source=source,
            token=token,
            destination=destination,
            overwrite=overwrite
        )

    if skip_step[1] is False:
        print("2. make intermediate mesh")
        mesh.make_intermediate_mesh(
            regions=regions,
            voxdim=voxdim,
            destination=destination,
            overwrite=overwrite
    )

    if skip_step[2] is False:
        print("3. register contours")
        register.register_contours(
            voxdim=voxdim,
            destination=destination,
            overwrite=overwrite)
    
    if skip_step[3] is False:
        print("4. compute final mask")
        mask.compute_final_mask(
            voxdim=voxdim,
            destination=destination,
            overwrite=overwrite
        )

    if skip_step[4] is False:
        print("5. make final mesh")
        final.make_final_mesh(
            voxdim=voxdim,
            level=level,
            destination=destination,
            overwrite=overwrite
        )

    if skip_step[5] is False:
        print("6. make ui for manual adjustment")
        ui.make_ui(
            os.path.join(destination, "7_registered_contours.npz"),
            os.path.join(destination, "12_ui.html")
        )

    print("done.")

def main(argv):
  '''convenience histology_to_mesh call from the command line'''
  _, project, source, token, regions, voxdim, destination, overwrite = argv

  regions = regions.split(",")
  voxdim = [float(s) for s in voxdim.split(",")]
  overwrite = overwrite=="True"

  histology_to_mesh_wf1(project, source, token, regions,
    voxdim, destination, overwrite)

if __name__ == "__main__":
  main(sys.argv)