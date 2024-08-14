# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 09:42:28 2024

@author: aayan
"""

#this is chatGPT's way of creating the comparison.svg file
#certain valeus (like width) will need to be changed to match the images being loaded
#just use this to understand how you would generate the .xml file in python, DONT JUST COPY AND PASTE
#test comment

#the px : mm conversion is 1 : 0.26458333 or 480px/127mm
pxTOmm = 480/127

import xml.etree.ElementTree as ET

# List of images with their attributes
mainImages = [
    {'width': '47.625', 'height': '47.625', 'xlink:href': 'out/zerofill_echo_0_120_crop2.png', 'x': '0', 'y': '0'},
    #{'width': '31.75', 'height': '31.75', 'xlink:href': 'out/zerofill_echo_0_120_crop.png', 'x': '15.875', 'y': '47.625'},
    {'width': '47.625', 'height': '47.625', 'xlink:href': 'out/psnr_echo_0_120_crop2.png', 'x': '47.625', 'y': '0'},
    #{'width': '31.75', 'height': '31.75', 'xlink:href': 'out/psnr_echo_0_120_crop.png', 'x': '63.5', 'y': '47.625'},
    {'width': '47.625', 'height': '47.625', 'xlink:href': 'out/ssim_echo_0_120_crop2.png', 'x': '95.25', 'y': '0'},
    #{'width': '31.75', 'height': '31.75', 'xlink:href': 'out/ssim_echo_0_120_crop.png', 'x': '111.125', 'y': '47.625'},
    {'width': '47.625', 'height': '47.625', 'xlink:href': 'out/psnr_ssim_echo_0_120_crop2.png', 'x': '142.875', 'y': '0'},
    #{'width': '31.75', 'height': '31.75', 'xlink:href': 'out/psnr_ssim_echo_0_120_crop.png', 'x': '158.75', 'y': '47.625'},
    {'width': '47.625', 'height': '47.625', 'xlink:href': 'out/gt_echo_0_120_crop2.png', 'x': '190.5', 'y': '0'},
    #{'width': '31.75', 'height': '31.75', 'xlink:href': 'out/gt_echo_0_120_crop.png', 'x': '206.375', 'y': '47.625'},
]
#the width and height of the image just changes the size, not the zoom so that information is not needed
#each image is represented as a dictionary of its attributes

zoomedImages = [
    {'width': '31.75', 'height': '31.75', 'xlink:href': 'out/zerofill_echo_0_120_crop.png', 'x': '15.875', 'y': '47.625'}, #the y val should = the height of the main images
    {'width': '31.75', 'height': '31.75', 'xlink:href': 'out/psnr_echo_0_120_crop.png', 'x': '63.5', 'y': '47.625'},
    {'width': '31.75', 'height': '31.75', 'xlink:href': 'out/ssim_echo_0_120_crop.png', 'x': '111.125', 'y': '47.625'},
    {'width': '31.75', 'height': '31.75', 'xlink:href': 'out/psnr_ssim_echo_0_120_crop.png', 'x': '158.75', 'y': '47.625'},
    {'width': '31.75', 'height': '31.75', 'xlink:href': 'out/gt_echo_0_120_crop.png', 'x': '206.375', 'y': '47.625'},
    ]
#split into main and zoom to see if it works
#in the future it might be relevant if the only input is the main image file path

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
    
# Create the root element
svg = ET.Element('svg', {
    'width': str(totalWidth(mainImages)),
    'height': str(totalHeight(mainImages, zoomedImages)),
    'viewBox': '0 0 238.12499 79.375005',
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

# Add images to the layer
for img in mainImages:
    ET.SubElement(layer, 'image', img)
    
for img in zoomedImages:
    ET.SubElement(layer, "image", img)

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

# Convert the XML tree to a string
xml_str = ET.tostring(svg, encoding='utf-8', method='xml').decode('utf-8')

# Write to an XML file
with open('generated_comparison.svg', 'w') as f:
    f.write(xml_str)
    
print("ran")