from statistics import median_low

import cv2
import lorem
from google.cloud import vision
from pytesseract import pytesseract, Output


config_tesseract = "-l eng --oem 1 --psm 3"

# A text detection with google cloud vision
def detect_text_gcv(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    # with io.open(path, 'rb') as image_file:
    #     content = image_file.read()
    # image = types.Image(content=cv2.imencode('.jpg', img)[1].tostring())

    image = vision.Image(content=cv2.imencode(".jpg", path)[1].tostring())

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    if texts:
        return texts[0].description
    else:
        return ""


def ocr_recognition(elem_image, ocr_engine="tesseract"):
    font_size_value = 14
    alltext_width = 0
    leftmin = 0
    maxright = 0
    text_elem_ocr = ""

    # Detect the font-size with tesseract for some element start
    if ocr_engine == "tesseract":
        # Convert to the grey colour
        elem_image_gray = cv2.cvtColor(elem_image, cv2.COLOR_BGR2GRAY)
        elem_image_gray = cv2.resize(elem_image_gray, None, fx=4, fy=4)
        result = pytesseract.image_to_boxes(elem_image_gray)

        lines = result.strip().split("\n")
        font_size = []

        # Calculate the number of letters recognized in lines:
        length_lines = len(lines)
        if length_lines > 7:
            # Calculate the average x-size for the long lines
            for line in lines:
                chars = line.split(" ")
                try:
                    font_size.append(float(chars[4]) - float(chars[2]))
                except Exception:
                    pass

        # Calculate the average x-size for the short lines
        else:
            for line in lines:
                chars = line.split(" ")
                xsize_chars = {
                    "v",
                    "w",
                    "z",
                    "a",
                    "c",
                    "e",
                    "m",
                    "n",
                    "o",
                    "r",
                    "s",
                    "u",
                }
                if chars[0] in xsize_chars:
                    # print(chars[0])
                    try:
                        font_size.append(float(chars[4]) - float(chars[2]))
                    except Exception:
                        pass

        try:
            # Filter out errors of recognition with median_low.
            # Probably should switch to quantiles with next statistics Python versions
            font_size_value = median_low(font_size)[0] * 1.9 / 4.0
        except Exception:
            font_size_value = 14.0
        finally:
            pass

        font_size_value = int(font_size_value)

        # Read a string with tesseract
        text_elem_tesseract = pytesseract.image_to_string(
            elem_image_gray, config=config_tesseract
        )
        # Show tesseract results only when font is larger than 14
        if font_size_value < 14:
            text_elem_tesseract = ""

        text_elem_ocr = text_elem_tesseract
    # Detect the font-size with tesseract for some element end

    # Detect the font-size with tesseract for some element start, with lorem text
    if ocr_engine == "lorem":
        # Convert to the grey colour
        elem_image_gray = cv2.cvtColor(elem_image, cv2.COLOR_BGR2GRAY)
        elem_image_gray = cv2.resize(elem_image_gray, None, fx=4, fy=4)
        result = pytesseract.image_to_boxes(elem_image_gray)

        lines = result.strip().split("\n")
        font_size = []

        # Calculate the number of letters recognized in lines:
        length_lines = len(lines)
        if length_lines > 7:
            # Calculate the average x-size for the long lines
            for line in lines:
                chars = line.split(" ")
                try:
                    font_size.append(float(chars[4]) - float(chars[2]))
                except Exception:
                    pass

        # Calculate the average x-size for the short lines
        else:
            for line in lines:
                chars = line.split(" ")
                xsize_chars = {
                    "v",
                    "w",
                    "z",
                    "a",
                    "c",
                    "e",
                    "m",
                    "n",
                    "o",
                    "r",
                    "s",
                    "u",
                }
                if chars[0] in xsize_chars:
                    # print(chars[0])
                    try:
                        font_size.append(float(chars[4]) - float(chars[2]))
                    except Exception:
                        pass

        try:
            # Filter out errors of recognition with median_low.
            # Probably should switch to quantiles with next statistics Python versions
            font_size_value = median_low(font_size)[0] * 1.9 / 4.0
        except Exception:
            font_size_value = 14.0
        finally:
            pass

        font_size_value = int(font_size_value)

        # Read a string with tesseract
        text_elem_lorem = lorem.get_word(count=2)
        # Show tesseract results only when font is larger than 14
        # if font_size_value < 14:
        #     text_elem_tesseract = ""

        text_elem_ocr = text_elem_lorem
        # Detect the font-size with tesseract for some element end, with lorem text

    # Detect the font-size with tesseract for some element, with gcv text start
    if ocr_engine == "googlecloud":
        # Convert to the grey colour
        elem_image_gray = cv2.cvtColor(elem_image, cv2.COLOR_BGR2GRAY)
        elem_image_gray = cv2.resize(elem_image_gray, None, fx=4, fy=4)
        result = pytesseract.image_to_boxes(elem_image_gray)
        d = pytesseract.image_to_data(elem_image_gray, output_type=Output.DICT)

        n_boxes = len(d["level"])
        # print(n_boxes, d)

        if n_boxes > 1:
            for i in range(n_boxes):
                if d["text"][i]:  # Choose only the text detected rows
                    # Initialization from the first array object containing the text
                    (left_min, top_min, width, height) = (
                        d["left"][i],
                        d["top"][i],
                        d["width"][i],
                        d["height"][i],
                    )
                    max_right = left_min + width
                    max_bottom = top_min + height

            for i in range(n_boxes):
                if d["text"][i]:  # Choose only the text detected rows
                    # print("i=", i)
                    (x, y, w, h) = (
                        d["left"][i],
                        d["top"][i],
                        d["width"][i],
                        d["height"][i],
                    )
                    right = x + w
                    bottom = y + h

                    if x < left_min:
                        left_min = x

                    if y < top_min:
                        top_min = y

                    if right > max_right:
                        max_right = right

                    if bottom > max_bottom:
                        max_bottom = bottom

                    # Detect width and height for the complete sentence or paragraph
                    # 4 is the correction number, because the image was scaled before for this number
                    alltext_width = int((max_right - left_min) / 4.0)
                    # print("alltext_width=", alltext_width)
                    alltext_height = int((max_bottom - top_min) / 4.0)
                    leftmin = int((left_min) / 4.0)
                    maxright = int((max_right) / 4.0)

                    # cv2.rectangle(elem_image_gray, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    """
                    # print(left_min, top_min, max_right, max_bottom, d['text'][i])
                    cv2.rectangle(elem_image_gray, (left_min, top_min), (max_right, max_bottom), (0, 255, 0), 2)
                    cv2.imshow('img', elem_image_gray)
                    cv2.waitKey(0)
                    """

        lines = result.strip().split("\n")
        font_size = []

        # Calculate the number of letters recognized in lines:
        length_lines = len(lines)
        if length_lines > 7:
            # Calculate the average x-size for the long lines
            for line in lines:
                chars = line.split(" ")
                try:
                    font_size.append(float(chars[4]) - float(chars[2]))
                except Exception:
                    pass

        # Calculate the average x-size for the short lines
        else:
            for line in lines:
                chars = line.split(" ")
                xsize_chars = {
                    "v",
                    "w",
                    "z",
                    "a",
                    "c",
                    "e",
                    "m",
                    "n",
                    "o",
                    "r",
                    "s",
                    "u",
                }
                if chars[0] in xsize_chars:
                    # print(chars[0])
                    try:
                        font_size.append(float(chars[4]) - float(chars[2]))
                    except Exception:
                        pass

        try:
            # Filter out errors of recognition with median_low.
            # Probably should switch to quantiles with next statistics Python versions
            font_size_value = median_low(font_size)[0] * 1.9 / 4.0
        except Exception:
            font_size_value = 14.0
        finally:
            pass

        font_size_value = int(font_size_value)

        # Read a string with gcv
        text_elem_gcv = detect_text_gcv(elem_image_gray)
        # Show tesseract results only when font is larger than 14
        # if font_size_value < 14:
        #     text_elem_tesseract = ""

        text_elem_ocr = text_elem_gcv
        # Detect the font-size with tesseract for some element, with gcv text end

    return font_size_value, text_elem_ocr, alltext_width, leftmin, maxright
