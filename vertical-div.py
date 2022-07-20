from PIL import Image
import xml.etree.ElementTree as ET
from io import BytesIO
import webbrowser
import json
from jsonpath import jsonpath

with open(
          'json-doc/via_project_19Jul2022_22h46m_json_three_divs_vertical.json'
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

border = 5
div = {}
div_css = ""

# Build ElementTree #
root = ET.Element("div")
container = ET.SubElement(root, "div")
container.set('class', 'container')

for i in range(len(x_value)):
    div[i] = ET.SubElement(container, "div")
    div[i].set('class', 'div'+str(i))
    if i == 0:
        div_css = div_css + """.div""" + str(i) + """ {
            position:relative;
            background-color: transparent;
            height: """ + str(height_value[i]) + """px;
            width: """ + str(width_value[i]) + """px;
            margin-left: """ + str(x_value[i]) + """px;
            margin-top: """ + str(y_value[i]) + """px;
            box-sizing: border-box;
            border: """ + str(border) + """px solid yellow;
            display: block;
        }
        """
    else:
        div_css = div_css + """.div""" + str(i) + """ {
            position:relative;
            background-color: transparent;
            height: """ + str(height_value[i]) + """px;
            width: """ + str(width_value[i]) + """px;
            margin-left: """ + str(x_value[i]-x_value[i-1]-border) + """px;
            margin-top: """ + str(y_value[i]-y_value[i-1]-border) + """px;
            box-sizing: border-box;
            border: """ + str(border) + """px solid yellow;
            display: block;
        }
        """

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
        .container {
            position:relative;
            background: url(""" + str(file_path) + """) no-repeat center;
            height: """ + str(h) + """px;
            width: """ + str(w) + """px;
            border: """ + str(border) + """px solid black;
            display: block;
        }
        """ + str(div_css) + """
    </style>
</head>
<body>
        """ + str(xml) + """
</body>
</html>
"""

GET_HTML = "vertical-div.html"
f = open(GET_HTML, 'w')
f.write(index_page)
f.close()

webbrowser.open("vertical-div.html")
