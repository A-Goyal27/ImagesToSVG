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
import matplotlib.pyplot as plt
import matplotlib.colorbar as cbar
from skimage import io, color
import numpy as np
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
parser.add_argument("inputFolder", type=str, help="Input the directory of the folder (or just the folder) of the images to be compared. Note-if inputting a directory: put the directory in quotes. Note-The ground truth should be the last file in the folder.")
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

#this will end the program if the necessary zoom measurements are not specified
if ((inputZoomWidth == None or inputZoomHeight == None) and (inputXend == None or inputYend == None)):
    print("The code needs zoom measurements. The args for the zoom measurements depends on which unit you are using. Run 'imagesToSVG.py -h' for more info.")
    sys.exit()


"""
***
FILE STUFF
***
"""
#normalize filepath
normalized_directory = os.path.normpath(inputFolder)

#getting a list of the directories to the images
imagePaths = []
for name in os.listdir(normalized_directory):
    imagePaths.append(os.path.join(normalized_directory, name))
    
imagePaths = sorted(imagePaths)

#gets the filename because that is needed for the xlink:href in the svg
def getFileName(filepath):
    return os.path.basename(filepath).split('\\\\')[-1]

#gets filetype
def getFileType(filepath):
    return os.path.splitext(filepath)[-1]

"""
***
CREATING MAIN IMAGES FOR SVG
***
"""
#creates the main images
mainImages = [] #empty list for the images that will be displayed
main_x, main_y = 0, 0 #starting positions
for img in imagePaths:
    #gets the size of the image
    image = Image.open(img)
    imgWidth, imgHeight = image.size
    
    #each image is represented as a dictionary of its attributes
    imgDict = {'width': str(imgWidth/pxTOmm), 
               'height': str(imgHeight/pxTOmm), 
               'xlink:href':  getFileName(normalized_directory) + "\\" + getFileName(img), #fixes the issue described under inputFolder, should work for everything
               'x': str(main_x), 
               'y': str(main_y), 
               "preserve_aspect_ratio":"none"
               }
    
    mainImages.append(imgDict) #add the image to the list
    main_x+=float(imgDict["width"]) #increase the x position but NOT the y position

"""
***
CREATING ZOOMED IMAGES, ERROR MAPS, AND RECTANGLES FOR SVG
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

zoomedImages = [] #creating the list of zoomed images
zoomBorders = [] #empty list for borders for the zoomed images (is only used if the image is placed)
errorMaps = [] #empty list for the error maps
imageTick = 0
zoomed_x, zoomed_y = 0, float(mainImages[imageTick]["height"])*pxTOmm #the y technically doesn't need to be converted but for consistency it is helpful
nameTick = 0 

#find a zoom scale value so that small zooms and big zooms all have a similar but scaled size in the end
def getZoomScale(zoomWidth, zoomHeight): #will return a value to make sure the zoomed image's width is half of the main image
    #image = Image.open(imgFilepath)  #same as above    
    imgWidth, imgHeight = image.size
    comparison= (imgWidth + imgHeight)/4 #comparison with the "mid-point" of this image
    
    return comparison/zoomWidth

#gets the ground truth zoom stuff figured out earlier so I can use it to compare for error maps, assumes GT is the last file in the folder
def getGTcropped(): 
    #just rehashing of code later in the program
    if usingPercentage:
        zoomXpos, zoomYpos, zoomWidth, zoomHeight = percentToPix(inputXzoom, inputYzoom, inputXend, inputYend)
    else:
        zoomXpos, zoomYpos, zoomWidth, zoomHeight = inputXzoom, inputYzoom, inputZoomWidth, inputZoomHeight
    
    image = Image.open(imagePaths[-1])
    crop_area = (zoomXpos, zoomYpos, zoomWidth+zoomXpos, zoomHeight+zoomYpos)
    croppedGT = image.crop(crop_area)
    name = "cropped_image" + str(len(imagePaths)-1) + ".png"
    croppedGT.save(name)
    groundTruth = io.imread(name)
    if image.mode == "RGB":
        groundTruth = color.rgb2gray(groundTruth)
    return groundTruth

#creating the color bar and saving it as a png
def getColorBar(cmap):
    data = np.random.rand(10, 10) #just random data
    # Create a figure and axis for the color bar
    fig, ax = plt.subplots(figsize=(2, 5))  # Adjust the size to make it suitable for the color bar
    # Create a color map and a color bar based on the data
    norm = plt.Normalize(vmin=np.min(data), vmax=np.max(data))  # Normalize based on data range (0-1)
    # Add the color bar to the figure
    colorbar = cbar.ColorbarBase(ax, cmap=cmap, norm=norm, orientation='vertical')
    # Save the color bar as a PNG file
    plt.savefig('color_bar.png', bbox_inches='tight', pad_inches=0.1)

groundTruth = getGTcropped()
cmap = "Reds" #colorway for the residuals
getColorBar(cmap)

#zoomed images, borders, and error maps
#all done in one loop because they use similar x/y positions
for img in imagePaths:
    #opens the image because all of the associated functions need the image open
    image = Image.open(img) 
    
    #convert to pixels from percentage if needed
    if usingPercentage:
        zoomXpos, zoomYpos, zoomWidth, zoomHeight = percentToPix(inputXzoom, inputYzoom, inputXend, inputYend)
    else:
        zoomXpos, zoomYpos, zoomWidth, zoomHeight = inputXzoom, inputYzoom, inputZoomWidth, inputZoomHeight
    
    #get the zoom scale
    zoomScale = getZoomScale(zoomWidth, zoomHeight)
    
    cropped_image = cropImage(zoomXpos, zoomYpos, zoomWidth, zoomHeight) 
    #each cropped image needs a different name
    name = "cropped_image" + str(nameTick) + ".png"
    #save the image so it can be referenced
    cropped_image.save(name)
    
    #the zoom placement stuff
    if zoomedPlace == None: #by default the zoom just appears under the main images
        placedZoom = False #just a boolean for record keeping
        pass
    else:
        zoomScale /= 2.3
        placedZoom = True
        #makes the zoom smaller and puts it in the top left
        if zoomedPlace == "TL":
            zoomed_y = 0
        #makes the zoom smaller and puts it in the top right
        elif zoomedPlace == "TR":
            zoomed_x += image.size[0] - (zoomScale * zoomWidth) -1
            zoomed_y = 0
        #makes the zoom smaller and puts it in the bottom left
        elif zoomedPlace == "BL":
            zoomed_y = image.size[1] - (zoomScale * zoomHeight) - 1
        #makes the zoom smaller and puts it in the bottom right
        elif zoomedPlace == "BR":
            zoomed_x += image.size[0] - (zoomScale * zoomWidth) -1
            zoomed_y = image.size[1] - (zoomScale * zoomHeight) -1
        
        #add a little border around the zomed image so it is easier to see
        zoomBorder = {"x":str(zoomed_x/pxTOmm), 
                  "y": str(zoomed_y/pxTOmm), 
                  "width": str(zoomScale * (1+zoomWidth)/pxTOmm), 
                  "height":str(zoomScale * (1+zoomHeight)/pxTOmm),
                  'style': 'fill:none;stroke:#32dd22;stroke-width:0.3'
                  }
        zoomBorders.append(zoomBorder)
    
    #spacing stuff
    if placedZoom:
        offset=1
    else:
        offset=0
    
    #create and add zoomed image dict
    zoomedDict = {"width":str(zoomScale * zoomWidth/pxTOmm), #scale zoomed size so it makes sense with the zoom window
                 "height":str(zoomScale * zoomHeight/pxTOmm),
                 "xlink:href":name,
                 "x":str((offset+zoomed_x)/pxTOmm),
                 "y":str((offset+zoomed_y)/pxTOmm),
                 "preserve_aspect_ratio":"none",
                 }
    zoomedImages.append(zoomedDict)
    
    #the x offset for the right needs to be reset so we don't overadd
    if zoomedPlace == "TR" or zoomedPlace == "BR":
        zoomed_x -= image.size[0] - zoomScale * zoomWidth -1
    
    #error maps only if the zoomed image isn't placed
    if not placedZoom:
        currentImage = io.imread(name)
        
        #convert to grayscale if needed
        if image.mode == 'RGB': #checking if the parent image is grayscale because it is easier and if the parent is grayscale then the zoomed will be as well
            currentImage = color.rgb2gray(currentImage)
        
        #generate error map
        error_map = np.abs(currentImage - groundTruth)
        
        #Normalize the error map
        if name != "cropped_image" + str(len(imagePaths)-1) + ".png": #it should only normalize if the images are different (otherwise you get a divide by 0 error)
            min_value = np.min(error_map)
            max_value = np.max(error_map)
        
            normalized_error_map = (error_map - min_value) / (max_value - min_value)
        else:
            normalized_error_map = error_map #I know it wouldn't be normalized in this case but for naming consistency this is how it is
            
            #getting the color bar size to be exact
            cBar = Image.open("color_bar.png")
            cBarW, cBarH = cBar.size
            cBarRatio = cBarW/cBarH
            #creating the color bar dict
            color_bar = {"width":str(zoomScale*zoomHeight*cBarRatio/pxTOmm),
                            "height":str(zoomScale*zoomHeight/pxTOmm),
                            "xlink:href":"color_bar.png",
                            "x":str((offset+zoomed_x+zoomWidth*zoomScale)/pxTOmm),
                            "y":str((offset+zoomed_y)/pxTOmm),
                            "preserve_aspect_ratio":"meet",
                            }
            #the color bar should have the same height as the zoom images but a scaled width
        
        #save the error map
        mapName = "error_map" + str(nameTick) +".png"
        plt.imsave(mapName,normalized_error_map, cmap=cmap)
        
        #create the error map dict for the svg and add it
        errorMapDict = {"width":str(zoomScale*zoomWidth/pxTOmm),
                        "height":str(zoomScale*zoomHeight/pxTOmm),
                        "xlink:href":mapName,
                        "x":str((offset+zoomed_x+zoomWidth*zoomScale)/pxTOmm),
                        "y":str((offset+zoomed_y)/pxTOmm),
                        "preserve_aspect_ratio":"none",
                        }
        errorMaps.append(errorMapDict)
        
    #zoom spacing
    zoomed_x+=float(mainImages[imageTick]["width"]) *pxTOmm
    zoomed_y = float(mainImages[imageTick]["height"]) * pxTOmm
    
    nameTick+=1
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
    
    totalOffset += xOffset #just makes it generalizable to different image sizes
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
    
    sumWidth *= pxTOmm #needs to end in pixels
    return sumWidth

def totalHeight(mainImg, zoomImg):
    #this function assumes all images in a given group have the same height
    if not placedZoom:
        sumHeight = float(mainImg[0]["height"]) + float(zoomImg[0]["height"])
    else: #if the zoomed image is placed then it does not add height
        sumHeight = float(mainImg[0]["height"])
    
    sumHeight *= pxTOmm
    return sumHeight

tWidth = round(totalWidth(mainImages))
tHeight = round(totalHeight(mainImages, zoomedImages))
print(f"Total Width: {tWidth}")
print(f"Total Height: {tHeight}")

"""
***
CREATING ROOT, NAMEDVIEW, AND LAYER ELEMENTS
***
"""
# Create the root element
svg = ET.Element('svg', {
    #adapt the width, height, and viewbox to match the total width and total height
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
***
ADDING TO THE LAYER
***
"""
# Add images to the layer
for img in mainImages:
    ET.SubElement(layer, 'image', img)
    
for img in zoomedImages:
    ET.SubElement(layer, "image", img)
    
for img in errorMaps:
    ET.SubElement(layer, "image", img)

#display the file path/image name over the image
for img in mainImages:
    image_name = getFileName(img["xlink:href"])
    textLengthOffset = len(image_name)**0.5 #numbers are arbitrary
    textVal = {"x": str(float(img["x"])+2), 
               "y":str(float(img["y"])-7), 
               "font_family":"Arial", 
               "font-size":str(12/pxTOmm), 
               "fill":"black", 
               "textLength":str(float(img["width"])-textLengthOffset), 
               "lengthAdjust":"spacingAndGlyphs"}
    textToAdd = ET.SubElement(layer, "text", textVal)
    textToAdd.text = image_name

# Add rectangles to the layer
for rect in zoomWindows:
    ET.SubElement(layer, 'rect', rect)

if placedZoom:
    for border in zoomBorders:
        ET.SubElement(layer, "rect", border)
        
#add color bar
if not placedZoom:
    ET.SubElement(layer, "image", color_bar)

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