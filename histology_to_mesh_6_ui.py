'''
Generate an web tool for manually aligning contours
to form a 3D model
'''

import os
import sys
import numpy as np
from tqdm import tqdm

def make_svg(registered_contours):
    '''Convert the contours to SVG'''
    svg = ""
    # for slce, c in enumerate(registered_contours):
    nslices = len(registered_contours)
    for ind1 in tqdm(range(nslices)):
        slice_index = nslices - ind1 - 1
        contour = registered_contours[slice_index]
        if contour is None:
            continue

        group = ""
        for point in contour:
            path_data = []
            for ind2, (xcoord, ycoord) in enumerate(point):
                if ind2 == 0:
                    path_data.append(f"M{xcoord},{ycoord}")
                else:
                    path_data.append(f"L{xcoord},{ycoord}")
            group += f'<path class="contour" d="{"".join(path_data)}Z" style="transform-origin: 500px 500px; transform: rotate(0deg) translate(0px,0px)"/>\n'

        svg += f'''
            <g id="s{slice_index}" style="transform-origin: center center; transform: rotateX(0deg) rotateY(0deg) translateZ({10*(nslices/2-ind1)}px)">
                <g class="group" style="transform-origin: 500px 500px; transform: rotate(0deg) translateX(0px) translateY(0px)">
                    {group}
                </g>
            </g>
            '''

    svg = f'''
    <svg id="contours" width="100%" height="100%" viewBox="0 0 1000 1000">
    {svg}
    </svg>
    '''
    return svg

def make_js(svg, nslices):
    '''Add the UI javascript code'''
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{current_dir}/ui_template.html") as file:
        html = file.read()
        html = html.replace("<svg></svg>", svg)
        html = html.replace("let nslices;", f"let nslices = {nslices};")
    return html

def make_ui(input_file, output_file):
    registered_contours = np.load(input_file, allow_pickle=True)["registered_contours"].tolist()
    print(f"{len(registered_contours)} registered contours")
    svg = make_svg(registered_contours)
    html = make_js(svg, len(registered_contours))
    with open(output_file, "w") as file:
        file.write(html)

def main(argv):
    '''Main function: called from the terminal'''

    if len(argv) != 3:
        print('''
        ui_register_contours.py

        Usage:
          python ui_register_contours.py input output

        Where:
          input: path to source registered_contours.npz file.
          output: path to a Web UI for registering the contours.
        ''')
        return

    _,input_file, output_file = argv

    make_ui(input_file, output_file)

if __name__ == "__main__":
    main(sys.argv)
