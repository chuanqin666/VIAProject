from PIL import Image
import xml.etree.ElementTree as ET
from io import BytesIO
import webbrowser
import json
from jsonpath import jsonpath
from collections import defaultdict

with open(
        'json-doc/via_project_20Jul2022_23h48m_json_horizontalvertical.json'
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

x2_value = {}
y2_value = {}
for i in range(len(x_value)):
    x2_value[i] = x_value[i] + width_value[i]
    y2_value[i] = y_value[i] + height_value[i]

value = defaultdict(list)
for i in range(len(y_value)):
    value[i + 1].append(x_value[i])
    value[i + 1].append(y_value[i])
    value[i + 1].append(width_value[i])
    value[i + 1].append(height_value[i])
    value[i + 1].append(x2_value[i])
    value[i + 1].append(y2_value[i])

xy = sorted(value.items(), key=lambda n: (n[1][1], n[1][0]))

file_path = 'image/' + filename_value[0]

img = Image.open(file_path)
w = img.width
h = img.height

div_css = """.container {
            display: block;
            position: relative;
            background: url(""" + str(file_path) + """) no-repeat center;
            height: """ + str(h) + """px;
            width: """ + str(w) + """px;
            border: 5px solid black;
        }
        .div {
            position: relative;
            text-align: center;
            font-size: 10px;
            display: block;
            float: left;
            background-color: transparent;
            outline: 3px solid yellow;
        }
        """
# Build ElementTree #
container = ET.Element("div")
container.set('class', 'container')

height = 0
width = 0
flag = 0
div = {}
for i in range(len(xy)):
    div[i] = ET.SubElement(container, "div")
    div[i].set('class', 'div div' + str(i + 1))
    div[i].text = str(xy[i][0])
    if i == 0:
        div_css = div_css + """.div""" + str(i + 1) + """ {
            left: """ + str(xy[i][1][0]) + """px;
            top: """ + str(xy[i][1][1]) + """px;
            width: """ + str(xy[i][1][2]) + """px;
            height: """ + str(xy[i][1][3]) + """px;
        }
        """
    elif xy[i - 1][1][5] > xy[i][1][1] >= xy[i - 1][1][1]:
        width += xy[i-1][1][2]
        div_css = div_css + """.div""" + str(i + 1) + """ {
            left: """ + str(xy[i][1][0] - width) + """px;
            top: """ + str(xy[i][1][1] - height) + """px;
            width: """ + str(xy[i][1][2]) + """px;
            height: """ + str(xy[i][1][3]) + """px;
        }
        """
        if xy[i][1][3] > xy[flag][1][3]:
            flag = i
    else:
        width = 0
        height += xy[flag][1][3]
        flag = i
        div_css = div_css + """.div""" + str(i + 1) + """ {
            clear: both;
            left: """ + str(xy[i][1][0]) + """px;
            top: """ + str(xy[i][1][1] - height) + """px;
            width: """ + str(xy[i][1][2]) + """px;
            height: """ + str(xy[i][1][3]) + """px;
        }
        """

# Convert to XML #
tree = ET.ElementTree(container)
io = BytesIO()
tree.write(io)
xml = io.getvalue().decode('UTF8')

index_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        """ + div_css + """
    </style>
</head>
<body>
        """ + str(xml) + """
</body>
</html>
"""

GET_HTML = "block.html"
f = open(GET_HTML, 'w')
f.write(index_page)
f.close()

webbrowser.open("block.html")
