from PIL import Image
import xml.etree.ElementTree as ET
from io import BytesIO
import webbrowser
import json
from jsonpath import jsonpath
from collections import defaultdict
import sys

with open(sys.argv[1]) as json_file:
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

x2_value = {}   # All the rectangle's right-bottom X coordinate
y2_value = {}   # All the rectangle's right-bottom Y coordinate
for i in range(len(x_value)):
    x2_value[i] = x_value[i] + width_value[i]
    y2_value[i] = y_value[i] + height_value[i]

value = defaultdict(list)
# Add data to value. #
for i in range(len(y_value)):
    value[i + 1].append(x_value[i])
    value[i + 1].append(y_value[i])
    value[i + 1].append(width_value[i])
    value[i + 1].append(height_value[i])
    value[i + 1].append(x2_value[i])
    value[i + 1].append(y2_value[i])

# Sort in left-top Y coordinate first, then sort in left-top X coordinate. #
xy = sorted(value.items(), key=lambda k: (k[1][1], k[1][0]))

xy_column = {}  # All outer rectangles
for i in range(len(xy) - 1):
    for n in range(i + 1, len(xy)):
        # if it is an outer rectangle. #
        if (xy[i][1][0] <= xy[n][1][0]
            < xy[n][1][4] <= xy[i][1][4]
            and xy[i][1][1] <= xy[n][1][1]
            < xy[n][1][5] <= xy[i][1][5]) \
                and not (xy[i][1][0] == xy[n][1][0]
                         and xy[n][1][4] == xy[i][1][4]
                         and xy[i][1][1] == xy[n][1][1]
                         and xy[n][1][5] == xy[i][1][5]):
            xy_column[i] = xy[i]
            for k in range(len(xy)):
                # Check all inner rectangles of each outer rectangle. #
                if (xy_column[i][1][0] <= xy[k][1][0]
                    < xy[k][1][4] <= xy_column[i][1][4]
                    and xy_column[i][1][1] <= xy[k][1][1]
                    < xy[k][1][5] <= xy_column[i][1][5]) \
                        and not (xy_column[i][1][0] == xy[k][1][0]
                                 and xy[k][1][4] == xy_column[i][1][4]
                                 and xy_column[i][1][1] == xy[k][1][1]
                                 and xy[k][1][5] == xy_column[i][1][5]):
                    if len(xy[k][1]) <= 6:
                        xy[k][1].append(xy_column[i][0])
                        xy[k][1].append(i + 1)
                    else:
                        xy[k][1][6] = xy_column[i][0]
                        xy[k][1][7] = i + 1

# If it is the outermost rectangle, add two values 0 #
for i in range(len(xy)):
    if len(xy[i][1]) == 6:
        xy[i][1].append(0)
        xy[i][1].append(0)

# Sort in outer rectangle number first, then sort in left-top X coordinate. #
# [0]:Left-top X [1]:Left-top Y [2]:Width
# [3]:Height [4]:Right-bottom X [5]:Right-bottom Y
# [6]:The number of outer rectangle in the JSON file(as div number)
# [7]:The number of outer rectangle in xy{}
xy_sorted = sorted(xy, key=lambda k: (k[1][7], k[1][0]))

# Finally adjust xy_sorted, sort in Left-top X if in the same row.
for i in range(len(xy_sorted) - 1):
    for n in range(i + 1, len(xy_sorted)):
        if xy_sorted[i][1][7] == xy_sorted[n][1][7]:
            if xy_sorted[i][1][1] > xy_sorted[n][1][5]:
                temp = xy_sorted[i]
                xy_sorted[i] = xy_sorted[n]
                xy_sorted[n] = temp
for i in range(len(xy_sorted) - 1):
    for n in range(i + 1, len(xy_sorted)):
        if xy_sorted[i][1][7] == xy_sorted[n][1][7]:
            if (xy_sorted[i][1][5] > xy_sorted[n][1][1]
                    >= xy_sorted[i][1][1]
                    or xy_sorted[n][1][5] > xy_sorted[i][1][1]
                    >= xy_sorted[n][1][1]):
                if xy_sorted[i][1][0] > xy_sorted[n][1][0]:
                    temp = xy_sorted[i]
                    xy_sorted[i] = xy_sorted[n]
                    xy_sorted[n] = temp

# Get the height and width of the image. #
file_path = 'image/' + filename_value[0]
img = Image.open(file_path)
w = img.width
h = img.height

# div_css records all the divs' style. #
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
top = 0    # Height needs to be subtracted
left = 0    # Width needs to be subtracted
flag = 0
div = {}
div[0] = ET.Element("div")
div[0].set('class', 'container')
for i in range(len(xy_sorted)):
    # Create all divs #
    div[xy_sorted[i][0]] = ET.SubElement(div[xy_sorted[i][1][6]], "div")
    div[xy_sorted[i][0]].set('class', 'div div' + str(xy_sorted[i][0]))
    div[xy_sorted[i][0]].text = str(xy_sorted[i][0])
    # If it is the first rectangle in xy_sorted, establish it directly. #
    if i == 0:
        div_css = div_css + """.div""" + str(xy_sorted[i][0]) + """ {
            left: """ + str(xy_sorted[i][1][0]) + """px;
            top: """ + str(xy_sorted[i][1][1]) + """px;
            width: """ + str(xy_sorted[i][1][2]) + """px;
            height: """ + str(xy_sorted[i][1][3]) + """px;
        }
        """
    # If two rectangles belong to the same outer rectangle. #
    elif xy_sorted[i][1][7] == xy_sorted[i - 1][1][7]:
        # Check if the two rectangles are in the same row:
        # The first rectangle is higher than the second rectangle
        # OR the second rectangle is higher than the first rectangle
        # AND the second rectangle is completely after the first rectangle
        if (xy_sorted[i - 1][1][5] > xy_sorted[i][1][1]
            >= xy_sorted[i - 1][1][1]
            or xy_sorted[i][1][5] > xy_sorted[i - 1][1][1]
            >= xy_sorted[i][1][1]) \
                and xy_sorted[i - 1][1][4] <= xy_sorted[i][1][0]:
            left += xy_sorted[i - 1][1][2]
            div_css = div_css + """.div""" + str(xy_sorted[i][0]) + """ {
            left: """ + str(xy_sorted[i][1][0] - left) + """px;
            top: """ + str(xy_sorted[i][1][1] - top) + """px;
            width: """ + str(xy_sorted[i][1][2]) + """px;
            height: """ + str(xy_sorted[i][1][3]) + """px;
        }
        """
            # Check which rectangle's right-bottom Y coordinate is larger. #
            if xy_sorted[i][1][3] > xy_sorted[flag][1][3]:
                flag = i
        # if the two rectangles are not in the same row. #
        else:
            if xy_sorted[i][1][7] == 0:
                left = 0
            top += xy_sorted[flag][1][3]
            flag = i
            div_css = div_css + """.div""" + str(xy_sorted[i][0]) + """ {
            clear: both;
            left: """ + str(xy_sorted[i][1][0] - left) + """px;
            top: """ + str(xy_sorted[i][1][1] - top) + """px;
            width: """ + str(xy_sorted[i][1][2]) + """px;
            height: """ + str(xy_sorted[i][1][3]) + """px;
        }
        """
    # If two rectangles do not belong to the same outer rectangle. #
    else:
        flag = i
        left = xy[xy_sorted[i][1][7] - 1][1][0]
        top = xy[xy_sorted[i][1][7] - 1][1][1]
        div_css = div_css + """.div""" + str(xy_sorted[i][0]) + """ {
            clear: both;
            left: """ + str(xy_sorted[i][1][0] - left) + """px;
            top: """ + str(xy_sorted[i][1][1] - top) + """px;
            width: """ + str(xy_sorted[i][1][2]) + """px;
            height: """ + str(xy_sorted[i][1][3]) + """px;
        }
        """

# Convert to XML #
tree = ET.ElementTree(div[0])
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

GET_HTML = "full.html"
f = open(GET_HTML, 'w')
f.write(index_page)
f.close()

webbrowser.open("full.html")
