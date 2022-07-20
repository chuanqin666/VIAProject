from PIL import Image
import xml.etree.ElementTree as ET
from io import BytesIO
import webbrowser
import json
from jsonpath import jsonpath

with open('json-doc/via_project_18Jul2022_22h36m_json.json') as json_file:
#with open('json-doc/via_project_19Jul2022_22h46m_json_right_border.json') as json_file:
#with open('json-doc/via_project_19Jul2022_22h46m_json_right_bottom_border.json') as json_file:
    via_file = json.load(json_file)

# Extract element content from JSON #
filename_value = jsonpath(via_file, "$..filename")
size_value = jsonpath(via_file, "$..size")

name_shape_value = jsonpath(via_file, "$..shape_attributes.name")
x_value = jsonpath(via_file, "$..shape_attributes.x")
y_value = jsonpath(via_file, "$..shape_attributes.y")
width_value = jsonpath(via_file, "$..shape_attributes.width")
height_value = jsonpath(via_file, "$..shape_attributes.height")
element_region_value = jsonpath(via_file, "$..region_attributes.HTML element")

file_path = 'image/' + filename_value[0]

img = Image.open(file_path)
w = img.width
h = img.height

# Build ElementTree #
root = ET.Element("div")
div1 = ET.SubElement(root, "div")
div1.set('class', 'div1')
div2 = ET.SubElement(div1, "div")
div2.set('class', 'div2')

# Convert to XML #
tree = ET.ElementTree(root)
io = BytesIO()
tree.write(io)
xml = io.getvalue().decode('UTF8')

index_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        .div1 {
            position:relative;
            background: url(""" + str(file_path) + """) no-repeat center;
            height: """ + str(h) + """px;
            width: """ + str(w) + """px;
            border: 5px solid black;
            display: block;
        }
        .div2 {
            position:relative;
            background-color: transparent;
            height: """ + str(height_value[0]) + """px;
            width: """ + str(width_value[0]) + """px;
            margin-left: """ + str(x_value[0]) + """px;
            margin-top: """ + str(y_value[0]) + """px;
            box-sizing: border-box;
            border: 5px solid yellow;
            display: block;
        }
    </style>
</head>
<body>
        """ + str(xml) + """
</body>
</html>
"""

GET_HTML = "one-rectangle.html"
f = open(GET_HTML, 'w')
f.write(index_page)
f.close()

webbrowser.open("one-rectangle.html")
