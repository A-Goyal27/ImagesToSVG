# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 09:42:28 2024

@author: aayan
"""

"""
PACKAGES AND CONSTANTS
"""
#the px : mm conversion is 1 : 0.26458333 or 480px/127mm
pxTOmm = 480/127

import xml.etree.ElementTree as ET
import os
from PIL import Image
import time
start = time.time()

"""
INPUT AND FILE STUFF
-inputFolder should take in the directory of the folder that contains the images that will be compared
    -it cannot specify which images to compare so the folder must ONLY contain the images that will be compared
"""
inputFolder = r"C:\Users\aayan\OneDrive\Documents\CIG Projec\testInput"
#the files in the folder should have some some order ("abc", "123", etc.)
#however for some reason the renamed version of the file that includes the "order tag" (ex. a_filename) is not being found unless testInput\ is added, out\ wasn't needed for the other ones

#getting a list of the directories to the images
imagePaths = []
for name in os.listdir(inputFolder):
    imagePaths.append(os.path.join(inputFolder, name))
    
imagePaths = sorted(imagePaths)

#imagesToInput = ['testInput/zerofill_echo_0_120.png', 'jony/b_psnr_echo_0_120.png', 'johny/ssim_echo_0_120_crop2.png', 'psnr_ssim_echo_0_120_crop2.png', 'gt_echo_0_120_crop2.png'] 
#takes in file paths for the images
mainImages = [] #empty list for the images that will be displayed

def getFileName(filepath):
    return os.path.basename(filepath).split('/')[-1]
#gets the filename because that is needed for the xlink:href in the svg

"""
CREATING IMAGES FOR SVG
"""
x, y = 0, 0
for img in imagePaths:
    #gets the size of the image
    image = Image.open(img)
    width, height = image.size
    
    imgDict = {'width': str(width/pxTOmm), 
               'height': str(height/pxTOmm), 
               'xlink:href':  getFileName(inputFolder) + "\\" + getFileName(img), #fixes the issue described under inputFolder, should work for everything
               'x': str(x), 
               'y': str(y), 
               "preserve_aspect_ratio":"none"}
    #each image is represented as a dictionary of its attributes
    mainImages.append(imgDict) #add the image to the list
    x+=float(imgDict["width"]) #increase the x position but NOT the y position

zoomedImages = [
    {'width': '31.75', 'height': '31.75', 'xlink:href': 'out/zerofill_echo_0_120_crop.png', 'x': '15.875', 'y': mainImages[0]['height']}, #the y val should = the height of the main images
    {'width': '31.75', 'height': '31.75', 'xlink:href': 'out/psnr_echo_0_120_crop.png', 'x': '63.5', 'y': mainImages[0]['height']},
    {'width': '31.75', 'height': '31.75', 'xlink:href': 'out/ssim_echo_0_120_crop.png', 'x': '111.125', 'y': mainImages[0]['height']},
    {'width': '31.75', 'height': '31.75', 'xlink:href': 'out/psnr_ssim_echo_0_120_crop.png', 'x': '158.75', 'y': mainImages[0]['height']},
    {'width': '31.75', 'height': '31.75', 'xlink:href': 'out/gt_echo_0_120_crop.png', 'x': '206.375', 'y': mainImages[0]['height']},
    ]
#in the future it might be relevant if the only input is the main image file path

"""
TOTAL WIDTH AND HEIGHT
"""
#finding the total width and height based on the images given
def totalWidth(images):
    sumWidth = 0
    for img in images:
      sumWidth += float(img["width"])
    
    sumWidth *= pxTOmm #needs to end in pixels, here the images are stored with mm but if in the future the image unit is px, then this step is not needed
    return sumWidth

def totalHeight(mainImg, zoomImg):
    #this function assumes all images in a given group have the same height
    sumHeight = float(mainImg[0]["height"]) + float(zoomImg[0]["height"])
    
    sumHeight *= pxTOmm
    return sumHeight

tWidth = totalWidth(mainImages)
tHeight = totalHeight(mainImages, zoomedImages)
print(f"Total Width: {tWidth}")
print(f"Total Height: {tHeight}")

"""
CREATING ROOT, NAMEDVIEW, AND LAYER
"""
# Create the root element
svg = ET.Element('svg', {
    'width': str(tWidth),
    'height': str(tHeight),
    'viewBox': "0 0 " + str(tWidth/pxTOmm) + " " + str(tHeight/pxTOmm),
    'version': '1.1',
    'id': 'svg5',
    'xmlns:inkscape': 'http://www.inkscape.org/namespaces/inkscape',
    'xmlns:sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
    'xmlns:xlink': 'http://www.w3.org/1999/xlink',
    'xmlns': 'http://www.w3.org/2000/svg',
    'xmlns:svg': 'http://www.w3.org/2000/svg',
})

# Add the namedview element
namedview = ET.SubElement(svg, 'sodipodi:namedview', {
    'id': 'namedview7',
    'pagecolor': '#ffffff',
    'bordercolor': '#666666',
    'borderopacity': '1.0',
    'inkscape:pageshadow': '2',
    'inkscape:pageopacity': '0.0',
    'inkscape:pagecheckerboard': '0',
    'inkscape:document-units': 'px',
    'showgrid': 'false',
    'units': 'px',
    'inkscape:snap-bbox': 'false',
    'inkscape:zoom': '1.5554293',
    'inkscape:cx': '214.0888',
    'inkscape:cy': '27.966556',
    'inkscape:window-width': '1786',
    'inkscape:window-height': '1099',
    'inkscape:window-x': '257',
    'inkscape:window-y': '507',
    'inkscape:window-maximized': '0',
    'inkscape:current-layer': 'layer1',
})

# Add the layer group
layer = ET.SubElement(svg, 'g', {
    'inkscape:label': 'Layer 1',
    'inkscape:groupmode': 'layer',
    'id': 'layer1',
})

"""
ADDING TO THE LAYER
"""
# Add images to the layer
for img in mainImages:
    ET.SubElement(layer, 'image', img)
    
# =============================================================================
# for img in zoomedImages:
#     ET.SubElement(layer, "image", img)
# =============================================================================

#display the file path/image name over the image
for img in mainImages:
    textVal = {"x": str(float(img["x"])+2), "y":str(float(img["y"])-10), "font_family":"Arial", "font-size":str(12/pxTOmm), "fill":"black", "textLength":str(float(img["width"])-2), "lengthAdjust":"spacingAndGlyphs"}
    textToAdd = ET.SubElement(layer, "text", textVal)
    textToAdd.text = getFileName(img["xlink:href"])


# List of rectangles with their attributes
rectangles = [
    {'x': '18.141666', 'y': '18.141666'},
    {'x': '66.29583', 'y': '18.141666'},
    {'x': '113.92083', 'y': '18.141666'},
    {'x': '161.54584', 'y': '18.141666'},
    {'x': '209.17084', 'y': '18.141666'},
]

# Add rectangles to the layer
for rect in rectangles:
    ET.SubElement(layer, 'rect', {
        'style': 'fill:none;stroke:#ff0032;stroke-width:0.3',
        'width': '17.197916',
        'height': '17.197916',
        'x': rect['x'],
        'y': rect['y'],
    })
    #since style, width, and height are constant in all rects it doesn't make sense to include them in the rectangles dict
    #however, because of that, "x": rect["x"] (pretty much remmaking the rect dict) is necessary

"""
GETTING THE SVG/XML
"""
# Convert the XML tree to a string
xml_str = ET.tostring(svg, encoding='utf-8', method='xml').decode('utf-8')

# Write to an XML file
with open('generated_comparison.svg', 'w') as f:
    f.write(xml_str)

end = time.time()
print(f"Took {end-start} seconds to run.")