import sys
sys.path.append('./venv/Lib/site-packages')
import xml.etree.ElementTree as ET
from io import BytesIO
import webbrowser
import json
from jsonpath import jsonpath
from collections import defaultdict
from ocr_functions import ocr_recognition
import cv2

#####################################################################
# Please enter command line to start:                               #
# Headers: python OCR.py val_json/via_export_json_raw_data_100.json #
# Forms: python OCR.py val_json/via_export_jsonn_08072020.json      #
# Footers: python OCR.py val_json/via_export_json.json              #
#####################################################################

# with open('val_json/via_export_jsonn_08072020.json') as json_file:
with open(sys.argv[1]) as json_file:
    json = json.load(json_file)

keys = list(json.keys())
div_css = ""
xml_tree = ""
form = ET.Element("body")


def sort(value_dict):
    # Sort in left-top Y first, then sort in left-top X. #
    xy = sorted(value_dict.items(), key=lambda k: (k[1][1], k[1][0]))
    for x in range(len(xy)):
        xy[x][1][6] = 0
        xy[x][1][7] = 0
    for e in range(len(xy) - 1):
        for f in range(e + 1, len(xy)):
            if xy[e][1][0] == xy[f][1][0] and xy[e][1][1] == xy[f][1][1]:
                if (xy[f][1][4] > xy[e][1][4] and xy[f][1][5] >= xy[e][1][5]) \
                        or (xy[f][1][4] >= xy[e][1][4]
                            and xy[f][1][5] > xy[e][1][5]):
                    tempa = xy[f]
                    xy[f] = xy[e]
                    xy[e] = tempa

    xy_column = {}  # All outer rectangles
    for i in range(len(xy) - 1):
        for n in range(i + 1, len(xy)):
            # if it is an outer rectangle. #
            if (xy[i][1][0] <= xy[n][1][0]
                    <= xy[n][1][4] <= xy[i][1][4]
                    and xy[i][1][1] <= xy[n][1][1]
                    <= xy[n][1][5] <= xy[i][1][5]):
                xy_column[i] = xy[i]
                for k in range(len(xy)):
                    # Check all inner rectangles of each outer rectangle. #
                    if k is not i:
                        if (xy_column[i][1][0] <= xy[k][1][0]
                            <= xy[k][1][4] <= xy_column[i][1][4]
                            and xy_column[i][1][1] <= xy[k][1][1]
                            <= xy[k][1][5] <= xy_column[i][1][5]) \
                                and not (xy_column[i][1][0] == xy[k][1][0]
                                         and xy[k][1][4] == xy_column[i][1][4]
                                         and xy_column[i][1][1] == xy[k][1][1]
                                         and xy[k][1][5]
                                         == xy_column[i][1][5]):
                            if xy[k][1][7] != 0:
                                if xy[xy[k][1][7] - 1][1][0] \
                                        <= xy_column[i][1][0] \
                                        <= xy_column[i][1][4] \
                                        <= xy[xy[k][1][7] - 1][1][4] \
                                        and xy[xy[k][1][7] - 1][1][1] \
                                        <= xy_column[i][1][1] \
                                        <= xy_column[i][1][5] \
                                        <= xy[xy[k][1][7] - 1][1][5] \
                                        and not (xy[xy[k][1][7] - 1][1][0]
                                                 == xy_column[i][1][0]
                                                 and xy_column[i][1][4]
                                                 == xy[xy[k][1][7] - 1][1][4]
                                                 and xy[xy[k][1][7] - 1][1][1]
                                                 == xy_column[i][1][1]
                                                 and xy_column[i][1][5]
                                                 == xy[xy[k][1][7] - 1][1][5]):
                                    xy[k][1][6] = xy_column[i][0]
                                    xy[k][1][7] = i + 1
                                elif (xy[xy[k][1][7] - 1][1][0]
                                      == xy_column[i][1][0]
                                      and xy_column[i][1][4]
                                      == xy[xy[k][1][7] - 1][1][4]
                                      and xy[xy[k][1][7] - 1][1][1]
                                      == xy_column[i][1][1]
                                      and xy_column[i][1][5]
                                      == xy[xy[k][1][7] - 1][1][5]):
                                    if i >= xy[k][1][7] - 1:
                                        xy[k][1][6] = xy_column[i][0]
                                        xy[k][1][7] = i + 1
                            else:
                                xy[k][1][6] = xy_column[i][0]
                                xy[k][1][7] = i + 1
                        elif (xy_column[i][1][0] == xy[k][1][0]
                              and xy[k][1][4] == xy_column[i][1][4]
                              and xy_column[i][1][1] == xy[k][1][1]
                              and xy[k][1][5] == xy_column[i][1][5]):
                            if k > i:
                                xy[k][1][6] = xy_column[i][0]
                                xy[k][1][7] = i + 1

    # Sort in outer rectangle number first, then sort in left-top Y. #
    xy_sorted = sorted(xy, key=lambda k: (k[1][7], k[1][0]))
    return xy_sorted, xy, xy_column


def group(value, xy_sorted):
    num = len(value)
    nn = 0
    li = []
    fl = 0
    for a in range(len(xy_sorted)):
        lf = a
        rt = a
        tp = a
        bt = a
        if xy_sorted[a][0] not in li:
            for b in range(len(xy_sorted)):
                if b is not a:
                    if xy_sorted[b][1][7] == xy_sorted[a][1][7]:
                        if (xy_sorted[b][1][0] >= xy_sorted[a][1][4]
                            or xy_sorted[b][1][4] <= xy_sorted[a][1][0]) \
                                and (xy_sorted[b][1][1] < xy_sorted[a][1][5]
                                     <= xy_sorted[b][1][5]
                                     or xy_sorted[b][1][1]
                                     <= xy_sorted[a][1][1]
                                     < xy_sorted[b][1][5]):
                            for c in range(len(xy_sorted)):
                                if xy_sorted[c][0] not in li:
                                    if c not in (a, b):
                                        if xy_sorted[c][1][7] \
                                                == xy_sorted[b][1][7]:
                                            if (xy_sorted[b][1][0]
                                                >= xy_sorted[c][1][4]
                                                or xy_sorted[b][1][4]
                                                <= xy_sorted[c][1][0]) \
                                                    and xy_sorted[c][1][0] \
                                                    <= xy_sorted[rt][1][4] \
                                                    and xy_sorted[c][1][4] \
                                                    >= xy_sorted[lf][1][0] \
                                                    and xy_sorted[tp][1][1] \
                                                    <= xy_sorted[c][1][1] \
                                                    < xy_sorted[b][1][5]:
                                                fl += 1
                                                li.append(xy_sorted[a][0])
                                                li.append(xy_sorted[c][0])
                                                if xy_sorted[c][1][5] \
                                                        > xy_sorted[bt][1][5]:
                                                    bt = c
                                                if xy_sorted[c][1][4] \
                                                        > xy_sorted[rt][1][4]:
                                                    rt = c
                                                if xy_sorted[c][1][1] \
                                                        < xy_sorted[tp][1][1]:
                                                    tp = c
                                                if xy_sorted[c][1][0] \
                                                        < xy_sorted[lf][1][0]:
                                                    lf = c
                                                if xy_sorted[c][1][5] \
                                                        >= xy_sorted[b][1][5] \
                                                        > xy_sorted[c][1][1]:
                                                    for d in range(len(xy_sorted)):
                                                        if xy_sorted[d][0] not in li:
                                                            if d not in (a, b, c):
                                                                if xy_sorted[d][1][7] \
                                                                        == xy_sorted[c][1][7]:
                                                                    if xy_sorted[b][1][5] \
                                                                            <= xy_sorted[d][1][1] \
                                                                            <= xy_sorted[bt][1][5] \
                                                                            and xy_sorted[d][1][5] >= \
                                                                            xy_sorted[tp][1][1] \
                                                                            and xy_sorted[d][1][0] <= \
                                                                            xy_sorted[rt][1][4] \
                                                                            and xy_sorted[d][1][4] > \
                                                                            xy_sorted[lf][1][0] \
                                                                            and (xy_sorted[b][1][0]
                                                                                 >= xy_sorted[d][1][4]
                                                                                 or xy_sorted[b][1][4]
                                                                                 <= xy_sorted[d][1][0]):
                                                                        li.append(xy_sorted[d][0])
                                                                        if xy_sorted[d][1][5] \
                                                                                > xy_sorted[bt][1][5]:
                                                                            bt = d
                                                                        if xy_sorted[d][1][4] \
                                                                                > xy_sorted[rt][1][4]:
                                                                            rt = d
                                                                        if xy_sorted[d][1][1] \
                                                                                < xy_sorted[tp][1][1]:
                                                                            tp = d
                                                                        if xy_sorted[d][1][0] \
                                                                                < xy_sorted[lf][1][0]:
                                                                            lf = d
        if (xy_sorted[a][1][0] is not xy_sorted[lf][1][0]) \
                or (xy_sorted[a][1][1] is not xy_sorted[tp][1][1]) \
                or (xy_sorted[a][1][4] is not xy_sorted[rt][1][4]) \
                or (xy_sorted[a][1][5] is not xy_sorted[bt][1][5]):
            nn += 1
            value[num + nn].append(xy_sorted[lf][1][0])
            value[num + nn].append(xy_sorted[tp][1][1])
            value[num + nn].append(xy_sorted[rt][1][4] - xy_sorted[lf][1][0])
            value[num + nn].append(xy_sorted[bt][1][5] - xy_sorted[tp][1][1])
            value[num + nn].append(xy_sorted[rt][1][4])
            value[num + nn].append(xy_sorted[bt][1][5])
            value[num + nn].append(0)
            value[num + nn].append(0)
            value[num + nn].append("rect")
            value[num + nn].append("group")
    return value, fl


def recur(value, xy_sorted):
    data1 = group(value, xy_sorted)
    value = data1[0]
    fl = data1[1]
    data2 = sort(value)
    xy_sorted = data2[0]
    xy = data2[1]
    xy_column = data2[2]
    if fl != 0:
        recur(value, xy_sorted)
    else:
        return xy_sorted, xy, xy_column, value


def final(xy_sorted, count):
    flg = 0
    count += 1
    # Finally adjust xy_sorted, sort in Left-top X if in the same row. #
    for i in range(len(xy_sorted) - 1):
        for n in range(i + 1, len(xy_sorted)):
            if xy_sorted[i][1][7] == xy_sorted[n][1][7]:
                if xy_sorted[i][1][1] >= xy_sorted[n][1][5]:
                    flg += 1
                    temp = xy_sorted[i]
                    xy_sorted[i] = xy_sorted[n]
                    xy_sorted[n] = temp
    for i in range(len(xy_sorted) - 1):
        for n in range(i + 1, len(xy_sorted)):
            if xy_sorted[i][1][7] == xy_sorted[n][1][7]:
                if (xy_sorted[i][1][5] > xy_sorted[n][1][1]
                    >= xy_sorted[i][1][1]
                    or xy_sorted[n][1][5] > xy_sorted[i][1][1]
                    >= xy_sorted[n][1][1]) \
                        or xy_sorted[n][1][5] > xy_sorted[i][1][5] \
                        > xy_sorted[i][1][1] > xy_sorted[n][1][1] \
                        or xy_sorted[i][1][5] > xy_sorted[n][1][5] \
                        > xy_sorted[n][1][1] > xy_sorted[i][1][1]:
                    if xy_sorted[i][1][0] > xy_sorted[n][1][0]:
                        flg += 1
                        temp = xy_sorted[i]
                        xy_sorted[i] = xy_sorted[n]
                        xy_sorted[n] = temp
    if flg != 0 and count <= 3:
        final(xy_sorted, count)
    return xy_sorted


for z in range(len(keys)):
    print(z)
    via_file = json[keys[z]]
    # Extract element content from JSON #
    filename_value = jsonpath(via_file, "$..filename")
    size_value = jsonpath(via_file, "$..size")
    name_shape_value = jsonpath(via_file, "$..shape_attributes.name")
    x_value = jsonpath(via_file, "$..shape_attributes.x")
    y_value = jsonpath(via_file, "$..shape_attributes.y")
    width_value = jsonpath(via_file, "$..shape_attributes.width")
    height_value = jsonpath(via_file, "$..shape_attributes.height")
    element_region_value = \
        jsonpath(via_file, "$..region_attributes.HTML element")

    x2_value = {}  # All the rectangle's right-bottom X coordinate
    y2_value = {}  # All the rectangle's right-bottom Y coordinate
    for i in range(len(x_value)):
        x2_value[i] = x_value[i] + width_value[i]
        y2_value[i] = y_value[i] + height_value[i]

    # Add data to value. #
    # [0]:Left-top X [1]:Left-top Y [2]:Width
    # [3]:Height [4]:Right-bottom X [5]:Right-bottom Y
    # [6]:The number of outer rectangle in the JSON file(as div number)
    # [7]:The number of outer rectangle in xy{}
    # [8]:Shape name [9]:HTML element
    value = defaultdict(list)
    for i in range(len(y_value)):
        value[i + 1].append(x_value[i])
        value[i + 1].append(y_value[i])
        value[i + 1].append(width_value[i])
        value[i + 1].append(height_value[i])
        value[i + 1].append(x2_value[i])
        value[i + 1].append(y2_value[i])
        value[i + 1].append(0)
        value[i + 1].append(0)
        value[i + 1].append(name_shape_value[i])
        value[i + 1].append(element_region_value[i])

    xy_sorted = sort(value)[0]

    xy_data = recur(value, xy_sorted)
    xy_sorted = recur(value, xy_sorted)[0]
    xy = recur(value, xy_sorted)[1]
    xy_column = recur(value, xy_sorted)[2]
    value = recur(value, xy_sorted)[3]

    xy_sorted = final(xy_sorted, 0)

    # Get the height and width of the image. #
    file_path = 'val_img/' + filename_value[0].strip(".\\")
    img = cv2.imread(file_path)
    h = len(img)
    w = len(img[0])

    # div_css records all the DIVs' style. #
    div_css = div_css + """.container_""" + str(z) + """ {
                clear: both;
                float: left;
                display: block;
                margin-bottom: 100px;
                position: relative;
                background: url(""" + str(file_path) + """) no-repeat center;
                height: """ + str(h) + """px;
                min-width: """ + str(w) + """px;
                border: 5px solid black;
            }
            .div""" + str(z) + """ {
                position: relative;
                text-align: left;
                display: block;
                color: red;
                float: left;
                background-color: transparent;
                outline: 3px solid yellow;
            }
            .div_group""" + str(z) + """ {
                position: relative;
                text-align: left;
                display: block;
                color: red;
                float: left;
                background-color: transparent;
                outline: 3px solid red;
            }
            """

    # Build ElementTree #
    top = 0  # Height needs to be subtracted
    left = 0  # Width needs to be subtracted
    flag_top = 0
    flag_right = 0
    div = {}
    div[0] = ET.SubElement(form, "div")
    div[0].set('class', 'container_' + str(z))
    # div[0].text = str(z)
    for i in range(len(xy_sorted)):
        # Create all divs #
        div[xy_sorted[i][0]] = ET.SubElement(div[xy_sorted[i][1][6]], "div")
        if xy_sorted[i][1][9] == "group":
            div[xy_sorted[i][0]].set(
                'class', 'div_group' + str(z) +
                         ' div' + str(z) + '_' + str(xy_sorted[i][0]))
        else:
            div[xy_sorted[i][0]].set(
                'class', 'div' + str(z) +
                         ' div' + str(z) + '_' + str(xy_sorted[i][0]))
        # div[xy_sorted[i][0]].text = str(xy_sorted[i][0])
        # div[xy_sorted[i][0]].text = " "

        # Use Tesseract to recognize the text and display inside DIVs. #
        if xy_sorted[i] not in xy_column.values():
            if xy_sorted[i][1][2] == 0 \
                    or xy_sorted[i][1][3] == 0 \
                    or xy_sorted[i][1][4] < 0 \
                    or xy_sorted[i][1][5] < 0 \
                    or xy_sorted[i][1][0] > w \
                    or xy_sorted[i][1][1] > h:
                div[xy_sorted[i][0]].text = " "
            else:
                if xy_sorted[i][1][0] < 0:
                    left_x = 0
                else:
                    left_x = xy_sorted[i][1][0]

                if xy_sorted[i][1][1] < 0:
                    left_y = 0
                else:
                    left_y = xy_sorted[i][1][1]

                if xy_sorted[i][1][4] + 1 > w:
                    right_x = w
                else:
                    right_x = xy_sorted[i][1][4] + 1

                if xy_sorted[i][1][5] + 1 > h:
                    right_y = h
                else:
                    right_y = xy_sorted[i][1][5] + 1

                img_crop = img[
                           int(left_y): int(right_y),
                           int(left_x): int(right_x)
                           ]
                data = ocr_recognition(img_crop)
                if data[1]:
                    div[xy_sorted[i][0]].text = str(data[1])
                    div_css = div_css + """.div""" + str(z) + """_""" + str(xy_sorted[i][0]) + """ {
                        font-size: """ + str(data[0]) + """px;
                    }
                    """
                else:
                    div[xy_sorted[i][0]].text = " "
        else:
            div[xy_sorted[i][0]].text = " "

        # If it is the first rectangle in xy_sorted, establish it directly. #
        if i == 0:
            div_css = div_css + """.div""" + str(z) + """_""" + str(xy_sorted[i][0]) + """ {
                margin-left: """ + str(xy_sorted[i][1][0]) + """px;
                margin-top: """ + str(xy_sorted[i][1][1]) + """px;
                width: """ + str(xy_sorted[i][1][2]) + """px;
                height: """ + str(xy_sorted[i][1][3]) + """px;
            }
            """
        # If two rectangles belong to the same outer rectangle. #
        elif xy_sorted[i][1][7] == xy_sorted[i - 1][1][7]:
            # Check if the two rectangles are in the same row:
            # The first rectangle is higher than the second rectangle
            # OR the second rectangle is higher than the first rectangle
            if (xy_sorted[i - 1][1][5] > xy_sorted[i][1][1]
                >= xy_sorted[i - 1][1][1]
                or xy_sorted[i][1][5] > xy_sorted[i - 1][1][1]
                >= xy_sorted[i][1][1]) \
                    or xy_sorted[i - 1][1][5] > xy_sorted[i][1][5] \
                    > xy_sorted[i][1][1] > xy_sorted[i - 1][1][1] \
                    or xy_sorted[i][1][5] > xy_sorted[i - 1][1][5] \
                    > xy_sorted[i - 1][1][1] > xy_sorted[i][1][1]:
                left = xy_sorted[flag_right][1][4]
                div_css = div_css + """.div""" + str(z) + """_""" + str(xy_sorted[i][0]) + """ {
                    margin-left: """ + str(xy_sorted[i][1][0] - left) + """px;
                    margin-top: """ + str(xy_sorted[i][1][1] - top) + """px;
                    width: """ + str(xy_sorted[i][1][2]) + """px;
                    height: """ + str(xy_sorted[i][1][3]) + """px;
                }
                """
                # Check which rectangle's is lower. #
                if xy_sorted[i][1][5] > xy_sorted[flag_top][1][5]:
                    flag_top = i
                # Check which rectangle's is longer. #
                if xy_sorted[i][1][4] > xy_sorted[flag_right][1][4]:
                    flag_right = i
            # if the two rectangles are not in the same row. #
            else:
                if xy_sorted[i][1][7] == 0:
                    left = 0
                else:
                    left = xy[xy_sorted[i][1][7] - 1][1][0]
                top = xy_sorted[flag_top][1][5]
                flag_top = i
                flag_right = i
                div_css = div_css + """.div""" + str(z) + """_""" + str(xy_sorted[i][0]) + """ {
                    clear: both;
                    margin-left: """ + str(xy_sorted[i][1][0] - left) + """px;
                    margin-top: """ + str(xy_sorted[i][1][1] - top) + """px;
                    width: """ + str(xy_sorted[i][1][2]) + """px;
                    height: """ + str(xy_sorted[i][1][3]) + """px;
                }
                """
        # If two rectangles do not belong to the same outer rectangle. #
        else:
            flag_top = i
            flag_right = i
            left = xy[xy_sorted[i][1][7] - 1][1][0]
            top = xy[xy_sorted[i][1][7] - 1][1][1]
            div_css = div_css + """.div""" + str(z) + """_""" + str(xy_sorted[i][0]) + """ {
                clear: both;
                margin-left: """ + str(xy_sorted[i][1][0] - left) + """px;
                margin-top: """ + str(xy_sorted[i][1][1] - top) + """px;
                width: """ + str(xy_sorted[i][1][2]) + """px;
                height: """ + str(xy_sorted[i][1][3]) + """px;
            }
            """

# Convert to XML #
tree = ET.ElementTree(form)
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
""" + str(xml) + """
</html>
"""

GET_HTML = "OCR.html"
f = open(GET_HTML, 'w')
f.write(index_page)
f.close()

webbrowser.open("OCR.html")
