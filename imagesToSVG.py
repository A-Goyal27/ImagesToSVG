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
#the px : mm conversion is 1 : 0.26458333 or 480px/127mm, SVGs use mm by default
pxTOmm = 480/127

#packages
import argparse
import sys
import xml.etree.ElementTree as ET
import os
from PIL import Image
import time
start = time.time()

"""
***
INPUT
-the input folder must ONLY contain the images that will be compared
-default run for ME: run imagesToSVG.py testInput 95 96 -zW 60 -zH 60
***
"""
#hardcoded inputs
# =============================================================================
# inputFolder = r"C:\Users\aayan\OneDrive\Documents\CIG Projec\testInput" 
# inputFolder = "testInput" #i guess full directory isn't needed
# #the files in the folder should have some some order ("abc", "123", etc.)
# #however for some reason the renamed version of the file that includes the "order tag" (ex. a_filename) is not being found unless the folder path is added which wasn't needed earlier
# 
# #position and size of zoom window
# 
# usingPercentage = False
# inputXzoom, inputYzoom = 190/2, 192/2 #pixels or percent
# inputZoomWidth, inputZoomHeight = 60, 60 #pixels
# inputXend, inputYend = 80, 80 #percent
# zoomedPlace = "TL"
# =============================================================================

#argparse stuff - getting the inputs 
parser = argparse.ArgumentParser(description="This script takes in a folder of images and zoom specifications. It outputs an SVG with the images side-by-side and the zoomed in version.")
parser.add_argument("inputFolder", type=str, help="Input the directory of the folder (or just the folder) of the images to be compared. Note-if inputting a directory: put the directory in quotes")
parser.add_argument("-uP","--usingPercentage", type=bool, default=False, help="Sets zoom units to percentage if 'True'. By default it is 'False'.")
parser.add_argument("startXzoom", type=int, help="Starting x coord of zoom (can be percentage or exact pixel)")
parser.add_argument("startYzoom", type=int, help="Starting y coord of zoom (can be percentage or exact pixel)")
parser.add_argument("-zW","--zoomWidth", type=int, help="Width of zoom window (must be specified if using pixels)", default=None)
parser.add_argument("-zH", "--zoomHeight", type=int, help="Height of zoom window (must be specified if using pixels)", default=None)
parser.add_argument("-eX", "--endXzoom", type=int, help="Ending x coord of zoom window (must be specified if using percentages)", default=None)
parser.add_argument("-eY", "--endYzoom", type=int, help="Ending y coord of zoom window (must be specified if using percentages)", default=None)
parser.add_argument("-zP", "--zoomPlace", type=str, choices=["TL", "TR", "BL", "BR"], default=None, help="Specifies where to put the zoomed image. If left blank the image will appear under the main image. It can be Top Left (TL), Top Right (TR), Bottom Left (BL), or Bottom Right (BR).")

#saving the inputs
args = parser.parse_args()
usingPercentage = args.usingPercentage
inputXzoom, inputYzoom = args.startXzoom, args.startYzoom
inputZoomWidth, inputZoomHeight = args.zoomWidth, args.zoomHeight
inputXend, inputYend = args.endXzoom, args.endYzoom
inputFolder = args.inputFolder
zoomedPlace = args.zoomPlace

if ((inputZoomWidth == None or inputZoomHeight == None) and (inputXend == None or inputYend == None)):
    print("The code needs zoom measurements. The args for the zoom measurements depends on which unit you are using. Run 'imagesToSVG.py -h' for more info.")
    sys.exit()
    #this will end the program if the necessary zoom measurements are not specified


"""
***
FILE STUFF
***
"""
normalized_directory = os.path.normpath(inputFolder) #normalize filepath

#getting a list of the directories to the images
imagePaths = []
for name in os.listdir(normalized_directory):
    imagePaths.append(os.path.join(normalized_directory, name))
    
imagePaths = sorted(imagePaths)

def getFileName(filepath):
    return os.path.basename(filepath).split('\\\\')[-1]
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
               'xlink:href':  getFileName(normalized_directory) + "\\" + getFileName(img), #fixes the issue described under inputFolder, should work for everything
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

#convert percentage of image to exact pixel amount
def percentToPix(startXpercent, startYpercent, endXpercent, endYpercent):
    #image = Image.open(imgFilepath) #this is done in the loop where this command is needed
    imgWidth, imgHeight = image.size
    pixXstart, pixYstart = (startXpercent/100) * imgWidth, (startYpercent/100) * imgHeight
    pixXend, pixYend = (endXpercent/100) * imgWidth, (endYpercent/100) * imgHeight
    pixXsize, pixYsize = pixXend - pixXstart, pixYend-pixYstart
    return pixXstart, pixYstart, pixXsize, pixYsize

#crop the image
def cropImage(cropXpos, cropYpos, cropWidth, cropHeight):
    #image = Image.open(imgFilepath)  #same as above
    crop_area = (cropXpos, cropYpos, cropWidth+cropXpos, cropHeight+cropYpos)
    return image.crop(crop_area)
    
#creating the list of zoomed images
zoomedImages = []
zoomBorders = [] #empty list for borders for the zoomed images (is only used if the image is placed)
imageTick = 0
zoomed_x, zoomed_y = 0, float(mainImages[imageTick]["height"])*pxTOmm #the y technically doesn't need to be converted but for consistency it is helpful
nameTick = 0 #see below

#find a zoom scale value so that small zooms and big zooms all have a similar but scaled size in the end
def getZoomScale(zoomWidth, zoomHeight): #will have the width be exactly half of the parent image
    #most of these numbers are just a result of trial and error
    imgWidth, imgHeight = image.size
    comparison= (imgWidth + imgHeight)/4 
    
    zoomAvg = (zoomWidth + zoomHeight)/2
    return comparison/zoomAvg

for img in imagePaths:
    #opens the image because all of the associated functions need the image open
    image = Image.open(img) 
    
    #convert to pixels from percentage if needed
    if usingPercentage:
        zoomXpos, zoomYpos, zoomWidth, zoomHeight = percentToPix(inputXzoom, inputYzoom, inputXend, inputYend)
    else:
        zoomXpos, zoomYpos, zoomWidth, zoomHeight = inputXzoom, inputYzoom, inputZoomWidth, inputZoomHeight
    
    zoomScale = getZoomScale(zoomWidth, zoomHeight) #get the zoom scale
    
    cropped_image = cropImage(zoomXpos, zoomYpos, zoomWidth, zoomHeight) 
    #each cropped image needs a different name
    name = "cropped_image" + str(nameTick) + getFileType(img)
    cropped_image.save(name) #save the image so it can be referenced
    nameTick+=1
    
    if zoomedPlace == None: #by default the zoom just appears under the main images
        placedZoom = False #just a boolean for record keeping
        pass
    else:
        zoomScale /= 2.3
        placedZoom = True
        if zoomedPlace == "TL":
            #makes the zoom smaller and puts it in the top left
            zoomed_y = 0
        elif zoomedPlace == "TR":
            #makes the zoom smaller and puts it in the top right
            zoomed_x += image.size[0] - (zoomScale * zoomWidth) -1
            zoomed_y = 0
        elif zoomedPlace == "BL":
            #makes the zoom smaller and puts it in the bottom left
            zoomed_y = image.size[1] - (zoomScale * zoomHeight) - 1
        elif zoomedPlace == "BR":
            #makes the zoom smaller and puts it in the bottom right
            zoomed_x += image.size[0] - (zoomScale * zoomWidth) -1 
            zoomed_y = image.size[1] - (zoomScale * zoomHeight) - 1
        zoomBorder = {"x":str(zoomed_x/pxTOmm), 
                  "y": str(zoomed_y/pxTOmm), 
                  "width": str(zoomScale * (1+zoomWidth)/pxTOmm), 
                  "height":str(zoomScale * (1+zoomHeight)/pxTOmm),
                  'style': 'fill:none;stroke:#32dd22;stroke-width:0.3'
                  } #add a little border around the zomed image so it is easier to see
        zoomBorders.append(zoomBorder)
    
    zoomedDict = {"width":str(zoomScale * zoomWidth/pxTOmm), #scale zoomed size so it makes sense with the zoom window
                 "height":str(zoomScale * zoomHeight/pxTOmm),
                 "xlink:href":name,
                 "x":str((1+zoomed_x)/pxTOmm),
                 "y":str((1+zoomed_y)/pxTOmm),
                 "preserve_aspect_ratio":"none",
                 }
    zoomedImages.append(zoomedDict)
    
    if zoomedPlace == "TR" or zoomedPlace == "BR":
        zoomed_x -= image.size[0] - zoomScale * zoomWidth #the x offset for the right needs to be reset so we don't overadd
    
    #puts each zoom right under the respective image
    zoomed_x+=float(mainImages[imageTick]["width"]) *pxTOmm
    zoomed_y = float(mainImages[imageTick]["height"]) * pxTOmm
    
    imageTick+=1

#creating the red rectangles that show what part of the image was zoomed
zoomWindows = []
imageTick = 0
xOffset = float(mainImages[imageTick]["width"])
totalOffset = 0 #where to put the next box so it is in the same place as the previous image
for img in imagePaths:
    windowDict = {"x":str((zoomXpos/pxTOmm + totalOffset)), 
              "y": str(zoomYpos/pxTOmm), 
              "width":str(zoomWidth/pxTOmm), 
              "height":str(zoomHeight/pxTOmm),
              'style': 'fill:none;stroke:#ff0032;stroke-width:0.3'
              } 
    zoomWindows.append(windowDict)
    
    #just makes it generalizable to different image sizes
    totalOffset += xOffset
    imageTick += 1



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
    if placedZoom:
        sumHeight = float(mainImg[0]["height"]) + float(zoomImg[0]["height"])
    else:
        sumHeight = float(mainImg[0]["height"])
    
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

if len(zoomBorders) > 0:
    for border in zoomBorders:
        ET.SubElement(layer, "rect", border)

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