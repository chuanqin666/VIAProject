from PIL import Image
import xml.etree.ElementTree as ET
from io import BytesIO
import webbrowser
import json
from jsonpath import jsonpath
from collections import defaultdict

with open(
        'json-doc/via_project_27Jul2022_9h13m_json_full.json'
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

xy = sorted(value.items(), key=lambda k: (k[1][1], k[1][0]))

xy_column = {}
for i in range(len(xy) - 1):
    for n in range(i + 1, len(xy)):
        if xy[i][1][0] < xy[n][1][0] \
                < xy[n][1][4] < xy[i][1][4] \
                and xy[i][1][1] < xy[n][1][1] \
                < xy[n][1][5] < xy[i][1][5]:
            xy_column[i] = xy[i]
            for k in range(len(xy)):
                if xy_column[i][1][0] < xy[k][1][0] \
                        < xy[k][1][4] < xy_column[i][1][4] \
                        and xy_column[i][1][1] < xy[k][1][1] \
                        < xy[k][1][5] < xy_column[i][1][5]:
                    xy[k][1].append(xy_column[i][0])
                    xy[k][1].append(i + 1)

for i in range(len(xy)):
    if len(xy[i][1]) <= 6:
        xy[i][1].append(0)
        xy[i][1].append(0)

xy2 = sorted(xy, key=lambda k: (k[1][len(k[1]) - 1], k[1][0]))

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
height = 0
width = 0
flag = 0
div = {}
div[0] = ET.Element("div")
div[0].set('class', 'container')
for i in range(len(xy2)):
    div[xy2[i][0]] = ET.SubElement(div[xy2[i][1][len(xy2[i][1]) - 2]], "div")
    div[xy2[i][0]].set('class', 'div div' + str(xy2[i][0]))
    div[xy2[i][0]].text = str(xy2[i][0])
    if i == 0:
        div_css = div_css + """.div""" + str(xy2[i][0]) + """ {
            left: """ + str(xy2[i][1][0]) + """px;
            top: """ + str(xy2[i][1][1]) + """px;
            width: """ + str(xy2[i][1][2]) + """px;
            height: """ + str(xy2[i][1][3]) + """px;
        }
        """
    elif xy2[i][1][len(xy2[i][1]) - 1] == \
            xy2[i - 1][1][len(xy2[i - 1][1]) - 1]:
        if xy2[i - 1][1][5] > xy2[i][1][1] >= xy2[i - 1][1][1] \
                or xy2[i][1][5] > xy2[i - 1][1][1] >= xy2[i][1][1]:
            width += xy2[i - 1][1][2]
            div_css = div_css + """.div""" + str(xy2[i][0]) + """ {
            left: """ + str(xy2[i][1][0] - width) + """px;
            top: """ + str(xy2[i][1][1] - height) + """px;
            width: """ + str(xy2[i][1][2]) + """px;
            height: """ + str(xy2[i][1][3]) + """px;
        }
        """
            if xy2[i][1][3] > xy2[flag][1][3]:
                flag = i
        else:
            if xy2[i][1][len(xy2[i][1]) - 1] == 0:
                width = 0
            height += xy2[flag][1][3]
            flag = i
            div_css = div_css + """.div""" + str(xy2[i][0]) + """ {
            clear: both;
            left: """ + str(xy2[i][1][0] - width) + """px;
            top: """ + str(xy2[i][1][1] - height) + """px;
            width: """ + str(xy2[i][1][2]) + """px;
            height: """ + str(xy2[i][1][3]) + """px;
        }
        """
    else:
        flag = i
        width = xy[xy2[i][1][len(xy2[i][1]) - 1] - 1][1][0]
        height = xy[xy2[i][1][len(xy2[i][1]) - 1] - 1][1][1]
        div_css = div_css + """.div""" + str(xy2[i][0]) + """ {
            clear: both;
            left: """ + str(xy2[i][1][0] - width) + """px;
            top: """ + str(xy2[i][1][1] - height) + """px;
            width: """ + str(xy2[i][1][2]) + """px;
            height: """ + str(xy2[i][1][3]) + """px;
        }
        """

# Convert to XML #
tree = ET.ElementTree(div[0])
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
        """ + div_css + """
    </style>
</head>
<body>
        """ + str(xml) + """
</body>
</html>
"""

GET_HTML = "full.html"
f = open(GET_HTML, 'w')
f.write(index_page)
f.close()

webbrowser.open("full.html")
