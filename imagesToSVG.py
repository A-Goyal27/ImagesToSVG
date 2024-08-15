# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 09:42:28 2024

@author: aayan
"""

"""
***
PACKAGES AND CONSTANTS
***
"""
#the px : mm conversion is 1 : 0.26458333 or 480px/127mm
pxTOmm = 480/127

import xml.etree.ElementTree as ET
import os
from PIL import Image
import time
start = time.time()

"""
***
INPUT
-inputFolder should take in the directory of the folder that contains the images that will be compared
    -it cannot specify which images to compare so the folder must ONLY contain the images that will be compared
    -images should be the same size as well
-zoom inputs
    -zoomXpos, zoomYpos take in the starting position for the zoom window
    -zoomWidth, zoomHeight specify the size of the zoom window
***
"""
inputFolder = r"C:\Users\aayan\OneDrive\Documents\CIG Projec\testInput"
#the files in the folder should have some some order ("abc", "123", etc.)
#however for some reason the renamed version of the file that includes the "order tag" (ex. a_filename) is not being found unless the folder path is added which wasn't needed earlier

#position and size of zoom window
zoomXpos, zoomYpos = 190/2, 192/2 #pixels
zoomWidth, zoomHeight = 60, 60 #pixels

"""
***
FILE STUFF
***
"""
#getting a list of the directories to the images
imagePaths = []
for name in os.listdir(inputFolder):
    imagePaths.append(os.path.join(inputFolder, name))
    
imagePaths = sorted(imagePaths)

def getFileName(filepath):
    return os.path.basename(filepath).split('/')[-1]
#gets the filename because that is needed for the xlink:href in the svg

def getFileType(filepath):
    return os.path.splitext(filepath)[-1]

"""
***
CREATING MAIN IMAGES FOR SVG
***
"""
#creates the main images
mainImages = [] #empty list for the images that will be displayed
main_x, main_y = 0, 0
for img in imagePaths:
    #gets the size of the image
    image = Image.open(img)
    imgWidth, imgHeight = image.size
    
    imgDict = {'width': str(imgWidth/pxTOmm), 
               'height': str(imgHeight/pxTOmm), 
               'xlink:href':  getFileName(inputFolder) + "\\" + getFileName(img), #fixes the issue described under inputFolder, should work for everything
               'x': str(main_x), 
               'y': str(main_y), 
               "preserve_aspect_ratio":"none"
               }
    #each image is represented as a dictionary of its attributes
    mainImages.append(imgDict) #add the image to the list
    main_x+=float(imgDict["width"]) #increase the x position but NOT the y position

"""
***
CREATING ZOOMED IMAGES AND RECTANGLES FOR SVG
***
"""
#crop the image - does the cropped image need to be saved or no?
def cropImage(imgFilepath, cropXpos, cropYpos, cropWidth, cropHeight):
    image = Image.open(imgFilepath)
    crop_area = (cropXpos, cropYpos, cropWidth+cropXpos, cropHeight+cropYpos)
    return image.crop(crop_area)
    
#creating the list of zoomed images
zoomedImages = []
zoomed_x, zoomed_y = 0, mainImages[0]["height"] #starting point
nameTick = 0 #see below

#find a zoom scale value so that small zooms and big zooms all have a similar but scaled size in the end
def getZoomScale(zoomWidth, zoomHeight):
    baseZoom = 4/3
    avg = (zoomWidth + zoomHeight)/2
    return baseZoom * 95.5/avg
zoomScale = getZoomScale(zoomWidth, zoomHeight)

for img in imagePaths:
    cropped_image = cropImage(img, zoomXpos, zoomYpos, zoomWidth, zoomHeight) 
    #each cropped image needs a different name
    name = "cropped_image" + str(nameTick) + getFileType(img)
    cropped_image.save(name) #save the image so it can be referenced
    
    zoomedDict = {"width":str(zoomScale * zoomWidth/pxTOmm), #scale zoomed size so it makes sense with the zoom window
                 "height":str(zoomScale * zoomHeight/pxTOmm),
                 "xlink:href":name,
                 "x":str(zoomed_x),
                 "y":zoomed_y,
                 "preserve_aspect_ratio":"none",
                 }
    zoomedImages.append(zoomedDict)
    
    nameTick+=1
    zoomed_x+=float(mainImages[0]["width"]) #puts each zoom right under the respective image

#creating the red rectangles that show what part of the image was zoomed
zoomWindows = []
xOffset = mainImages[0]["width"] #where to put the next box so it is in the same place as the previous image
for i in range(len(imagePaths)):
    windowDict = {"x":str((zoomXpos/pxTOmm +float(xOffset)*i)), 
              "y": str(zoomYpos/pxTOmm), 
              "width":str(zoomWidth/pxTOmm), 
              "height":str(zoomHeight/pxTOmm),
              'style': 'fill:none;stroke:#ff0032;stroke-width:0.3'
              } 
    zoomWindows.append(windowDict)

"""
***
TOTAL WIDTH AND HEIGHT
***
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
print(f"Total Width: {round(tWidth)}")
print(f"Total Height: {round(tHeight)}")

"""
***
CREATING ROOT, NAMEDVIEW, AND LAYER ELEMENTS
***
"""
# Create the root element
svg = ET.Element('svg', {
    'width': str(tWidth),
    'height': str(tHeight),
    'viewBox': "0 0 " + str(tWidth/pxTOmm) + " " + str(tHeight/pxTOmm),
    #adapt the width, height, and viewbox to match the total width and total height
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
***
ADDING TO THE LAYER
***
"""
# Add images to the layer
for img in mainImages:
    ET.SubElement(layer, 'image', img)
    
for img in zoomedImages:
    ET.SubElement(layer, "image", img)

#display the file path/image name over the image
for img in mainImages:
    image_name = getFileName(img["xlink:href"])
    textLengthOffset = len(image_name)**0.5
    textVal = {"x": str(float(img["x"])+2), 
               "y":str(float(img["y"])-7), 
               "font_family":"Arial", 
               "font-size":str(12/pxTOmm), 
               "fill":"black", 
               "textLength":str(float(img["width"])-textLengthOffset), #a.. length = 25
               "lengthAdjust":"spacingAndGlyphs"}
    textToAdd = ET.SubElement(layer, "text", textVal)
    textToAdd.text = image_name

# Add rectangles to the layer
for rect in zoomWindows:
    ET.SubElement(layer, 'rect', rect)
    #since style, are constant in all rects it doesn't make sense to include them in the rectangles dict
    #however, because of that, "x": rect["x"] (pretty much remmaking the rect dict) is necessary

"""
***
GETTING THE SVG/XML and PDF
***
"""
# Convert the XML tree to a string
xml_str = ET.tostring(svg, encoding='utf-8', method='xml').decode('utf-8')

# Write to an XML file
with open('generated_comparison.svg', 'w') as f:
    f.write(xml_str)

#displays the amount of time the program took to run, also acts as a way to see if the program ran successfully
end = time.time()
print(f"This program took {round(end-start,3)} seconds to run.")