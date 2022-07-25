from PIL import Image
import xml.etree.ElementTree as ET
from io import BytesIO
import webbrowser
import json
from jsonpath import jsonpath

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

file_path = 'image/' + filename_value[0]

img = Image.open(file_path)
w = img.width
h = img.height


div = {}
div_css = ""

# Build ElementTree #
container = ET.Element("div")
container.set('class', 'container')
column1 = ET.SubElement(container, "div")
column1.set('class', 'column1')
column2 = ET.SubElement(container, "div")
column2.set('class', 'column2')
column3 = ET.SubElement(column2, "div")
column3.set('class', 'column3')

for i in range(len(x_value)):
    if x_value[i] < 141:
        div[i] = ET.SubElement(column1, "div")
        div[i].set('class', 'div div'+str(i+1))
        div[i].text = str(i+1)
    elif y_value[i] == 77:
        div[i] = ET.SubElement(column3, "div")
        div[i].set('class', 'div div'+str(i+1))
        div[i].text = str(i+1)
    else:
        div[i] = ET.SubElement(column2, "div")
        div[i].set('class', 'div div'+str(i+1))
        div[i].text = str(i+1)

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
            display: flex;
            position: relative;
            background: url(""" + str(file_path) + """) no-repeat center;
            height: """ + str(h) + """px;
            width: """ + str(w) + """px;
            border: 5px solid black;
        }
        .column1 {
            display: flex;
            flex-direction:column;
            position: relative;
            background-color: transparent;
            height: """ + str(h) + """px;
            width: """ + str(x_value[0]) + """px;
        }
        .column2 {
            display: flex;
            position: relative;
            flex-direction:column;
            background-color: transparent;
            height: """ + str(h) + """px;
            width: """ + str(w-x_value[0]) + """px;
        }
        .column3 {
            order: 5;
            display: flex;
            position: relative;
            background-color: transparent;
            flex:1;
            margin-left: """ + str(x_value[0]-x_value[0]) + """px;
            margin-top: """ + str(y_value[0]-y_value[4]-height_value[4]) + """px;
        }
        .div {
            position: relative;
            text-align: center;
            font-size: 10px;
            background-color: transparent;
            outline: 3px solid yellow;
        }
        .div1 {
            order: 6;
            height: """ + str(height_value[0]) + """px;
            width: """ + str(width_value[0]) + """px;
        }
        .div2 {
            order: 1;
            height: """ + str(height_value[1]) + """px;
            width: """ + str(width_value[1]) + """px;
            margin-left: """ + str(x_value[1]) + """px;
            margin-top: """ + str(y_value[1]) + """px;
        }
        .div3 {
            order: 3;
            height: """ + str(height_value[2]) + """px;
            width: """ + str(width_value[2]) + """px;
            margin-left: """ + str(x_value[2]-x_value[0]) + """px;
            margin-top: """ + str(y_value[2]) + """px;
        }
        .div4 {
            order: 7;
            height: """ + str(height_value[3]) + """px;
            width: """ + str(width_value[3]) + """px;
            margin-left: """ + str(x_value[3]-x_value[0]-width_value[0]) + """px;
        }
        .div5 {
            order: 4;
            height: """ + str(height_value[4]) + """px;
            width: """ + str(width_value[4]) + """px;
            margin-left: """ + str(x_value[4]-x_value[0]) + """px;
            margin-top: """ + str(y_value[4]-y_value[2]-height_value[2]) + """px;
        }
        .div6 {
            order: 9;
            height: """ + str(height_value[5]) + """px;
            width: """ + str(width_value[5]) + """px;
            margin-left: """ + str(x_value[5]-x_value[0]) + """px;
            margin-top: """ + str(y_value[5]-y_value[7]-height_value[7]) + """px;
        }
        .div7 {
            order: 2;
            height: """ + str(height_value[6]) + """px;
            width: """ + str(width_value[6]) + """px;
            margin-left: """ + str(x_value[6]) + """px;
            margin-top: """ + str(y_value[6]-y_value[1]-height_value[1]) + """px;
        }
        .div8 {
            order: 8;
            height: """ + str(height_value[7]) + """px;
            width: """ + str(width_value[7]) + """px;
            margin-left: """ + str(x_value[7]-x_value[0]) + """px;
            margin-top: """ + str(y_value[7]-y_value[3]-height_value[3]) + """px;
        }
    </style>
</head>
<body>
        """ + str(xml) + """
</body>
</html>
"""

GET_HTML = "horizontalvertical.html"
f = open(GET_HTML, 'w')
f.write(index_page)
f.close()

webbrowser.open("horizontalvertical.html")
