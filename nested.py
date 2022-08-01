from PIL import Image
import xml.etree.ElementTree as ET
from io import BytesIO
import webbrowser
import json
from jsonpath import jsonpath
from collections import defaultdict

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

xy2_value = {}
x2_value = {}
y2_value = {}
for i in range(len(x_value)):
    x2_value[i] = x_value[i] + width_value[i]
    y2_value[i] = y_value[i] + height_value[i]
print(x2_value, y2_value)

value = defaultdict(list)
for i in range(len(y_value)):
    value[i+1].append(x_value[i])
    value[i+1].append(y_value[i])
    value[i+1].append(width_value[i])
    value[i+1].append(height_value[i])
    value[i+1].append(x2_value[i])
    value[i+1].append(y2_value[i])
print(value.keys())
print(value)
print(sorted(value.items()))
print(list(value.items()))
# xy = dict(zip(x_value, y_value))
# print(xy)
# xy_value = dict(sorted(xy.items()))
# print(xy_value)

file_path = 'image/' + filename_value[0]

img = Image.open(file_path)
w = img.width
h = img.height

div = {}
div_css = ""

# Build ElementTree #
container = ET.Element("div")
container.set('class', 'container')

for i in range(len(x_value)-1):
    for n in range(i+1, len(x_value)):
        if x_value[i] < x_value[n] < x2_value[n] < x2_value[i] and \
                y_value[i] < y_value[n] < y2_value[n] < y2_value[i]:
            div[i] = ET.SubElement(container, "div")
            div[i].set('class', 'div div'+str(i+1))
            div[n] = ET.SubElement(div[i], "div")
            div[n].set('class', 'div div'+str(n+1))
        elif x_value[n] < x_value[i] < x2_value[i] < x2_value[n] and \
                y_value[n] < y_value[i] < y2_value[i] < y2_value[n]:
            div[n] = ET.SubElement(container, "div")
            div[n].set('class', 'div div'+str(n+1))
            div[i] = ET.SubElement(div[n], "div")
            div[i].set('class', 'div div'+str(i+1))
        else:
            div[i] = ET.SubElement(container, "div")
            div[i].set('class', 'div div'+str(i+1))
            div[n] = ET.SubElement(container, "div")
            div[n].set('class', 'div div'+str(n+1))

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
        .container {
            position: relative;
            display: flex;
            background: url(""" + str(file_path) + """) no-repeat center;
            height: """ + str(h) + """px;
            width: """ + str(w) + """px;
            border: 5px solid black;
        }
        .div2 {
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
        .div1 {
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
