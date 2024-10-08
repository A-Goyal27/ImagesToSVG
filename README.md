# Images To SVG
This script aims to make comparisons of images and zoomed versions quicker and easier. 

For instance, suppose you had a few different models that each generated a brain scan and you wanted to compare them. This script will nicely line up the images side-by-side and also display a zoomed-in version for more precise comparison.

I ran this code on Python 3.9. Older versions should work as well.

## Inputs
- A folder containing the images that will be compared. The folder must ONLY contain the images that will be compared.
  - The images should be in either .png or .jpg format. However, other filetypes should be supported as well.
  - The images will be sorted so it is recommended that they start with some sort of "order tag" (1, 2, 3; a, b, c; etc.). The ground truth should be ordered to be the last image in the folder.
- Specifications of how to create the zoom window for the image.
- Specifications of where to put the zoomed image, will be under the main image by default.

## Output
A .svg file with:
- The images side-by-side.
- The zoomed images in the given location.
- The residuals between the zoomed images and the ground truth's zoomed image. (the color bar goes from 0, 1)

## Running the Code
Depending on which console/terminal you use, run the line:
```
python imagesToSVG.py inputFolder startXzoom startYzoom -uP bool -zW int -zH int -eX int -eY int -zP {TL, TR, BL, BR}
```
or
```
run imagesToSVG.py inputFolder startXzoom startYzoom -uP bool -zW int -zH int -eX int -eY int -zP {TL, TR, BL, BR}
```
.

The script uses [argparse](https://docs.python.org/3/library/argparse.html) for easy changes to be made to the output.

The positional (required) arguments are:
- `inputFolder` <- should be the directory or the folder of the images that will be compared. If using the directory, put it in quotes. The folder input will only work if the script and the folder are in the same directory.
- `startXzoom` <- should be the starting x-position of the zoom window. Can be in either pixels or percentages.
- `startYzoom` <- should be the starting y-position of the zoom window. Can be in either pixels or percentages.

All positional argument inputs should completely replace their name in the example code provided above. ex.
```
python imagesToSVG.py testInput 95 96
```

The optional arguments are:
- `--usingPercentage`, `-uP` <- should be `True` if you are using percentages as the unit for the zoom window. By default it is `False`.
- `--zoomWidth`, `-zW` <- should be the width of the zoom window. Use if, and only if, you are using pixels as the unit of measurement for the zoom window.
- `--zoomHeight`, `-zH` <- should be the height of the zoom window. Use if, and only if, you are using pixels as the unit of measurement for the zoom window.
- `--endXzoom`, `-eX` <- should be the ending x position of the zoom window. Use if, and only if, you are using percentages as the unit of measurement for the zoom window.
- `--endYzoom`, `-eY` <- should be the ending y position of the zoom window. Use if, and only if, you are using percentages as the unit of measurement for the zoom window.
- `--zoomPlace`, `-zP` <- should be where the zoomed image should be placed. It can either be Top Left (TL), Top Right (TR), Bottom Left (BL), Bottom Right (BR) of the main image. By default, the image will be placed under the main image.

All optional arguments should be placed after their tag, or replace their data type in the example code above. ex.
```
python imagesToSVG.py testInput 50 50 -uP True -eX 80 -eY 80 -zP TL
```

For more information, run:
```
python imagesToSVG.py -h
```
or
```
run imagesToSVG.py -h
```
.
