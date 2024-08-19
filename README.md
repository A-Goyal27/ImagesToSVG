# Images To SVG
This script aims to make comparisons of images and zoomed versions quicker and easier.
## Inputs
- A folder containing the images that will be compared. The folder must ONLY contain the images that will be compared. The images should be in either .png or .jpg format. However, other filetypes should be supported as well.
- Specifications of where and how much to zoom in on the image.
- Specifications of where to put the zoomed image, will be under the main image by default.
## Output
- An .svg file with the images side-by-side and the zoomed images in the given location for easy comparison.
## Running the Code
Depending on which console/terminal you use, run:
```
python imagesToSVG.py inputFolder zoomXpos zoomYpos -uP bool -zW int -zH int -eX int -eY int -zP {TL, TR, BL, BR}
```
or
```
run imagesToSVG.py inputFolder zoomXpos zoomYpos -uP bool -zW int -zH int -eX int -eY int -zP {TL, TR, BL, BR}
```
.

The script uses [argparse](https://docs.python.org/3/library/argparse.html) for easy changes to be made to the output.

The positional (required) arguments are:
- inputFolder <- should be the directory or the folder of the images that will be compared. If using the directory, put it in quotes. The folder input will only work if the script and the folder are in the same directory.
- zoomXpos <- should be the starting x position of the zoom window.
- zoomYpos <- should be the starting y position of the zoom window.
All positional argument inputs should completely replace their name in the example code provided above. ex.
```
run imagesToSVG.py testInput 95 96
```
