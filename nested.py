from PIL import Image
import xml.etree.ElementTree as ET
from io import BytesIO
import webbrowser
import json
from jsonpath import jsonpath

with open(
          'json-doc/via_project_20Jul2022_23h54m_json_nested.json'
        ) as json_file:
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


div = {}
div_css = ""

# Build ElementTree #
container = ET.Element("div")
container.set('class', 'container')

div1 = ET.SubElement(container, "div")
div1.set('class', 'div1')
div2 = ET.SubElement(div1, "div")
div2.set('class', 'div2')

# Convert to XML #
tree = ET.ElementTree(container)
io = BytesIO()
tree.write(io)
xml = io.getvalue().decode('UTF8')

print(xml)
index_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        .container {
            position: relative;
            display: flex;
            background: url(""" + str(file_path) + """) no-repeat center;
            height: """ + str(h) + """px;
            width: """ + str(w) + """px;
            border: 5px solid black;
        }
        .div1 {
             position: relative;
             text-align: center;
             font-size: 10px;
             background-color: transparent;
             height: """ + str(height_value[1]) + """px;
             width: """ + str(width_value[1]) + """px;
             margin-left: """ + str(x_value[1]) + """px;
             margin-top: """ + str(y_value[1]) + """px;
             outline: 3px solid yellow;
         }
        .div2 {
             position: relative;
             text-align: center;
             font-size: 10px;
             background-color: transparent;
             height: """ + str(height_value[0]) + """px;
             width: """ + str(width_value[0]) + """px;
             margin-left: """ + str(x_value[0]-x_value[1]) + """px;
             margin-top: """ + str(y_value[0]-y_value[1]) + """px;
             outline: 3px solid yellow;
         }
    </style>
</head>
<body>
        """ + str(xml) + """
</body>
</html>
"""

GET_HTML = "nested.html"
f = open(GET_HTML, 'w')
f.write(index_page)
f.close()

webbrowser.open("nested.html")
