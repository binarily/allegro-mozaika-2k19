from io import BytesIO

from flask import Flask, request, send_file
from PIL import Image, ImageOps
from random import shuffle

import requests

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/mozaika')
def mozaika():
    # Parse resolution (if provided), check for errors
    resolution_string = request.args.get('rozdzielczosc', default='2048x2048', type=str)
    resolutions_split = resolution_string.split('x')
    if len(resolutions_split) != 2:
        return 'Wrong resolution defined (too many/not enough values)', 400
    try:
        resolution = (int(resolutions_split[0]), int(resolutions_split[1]))
    except ValueError:
        return 'Wrong resolution defined (incorrect values)', 400
    if min(resolution) <= 0:
        return 'Wrong resolution defined (non-positive values)', 400

    # Create final image for mosaic
    final_image = Image.new(mode="RGB", size=resolution)

    # Parse image URLs, check for errors
    images_urls = request.args.get('zdjecia', default='').split(',')
    images_list = list()
    if len(images_urls) < 1 or len(images_urls) > 8:
        return 'Wrong number of image URLs provided', 400

    # Parse randomization option (if provided)
    randomize = True if request.args.get('losowo', default='0', type=str) == '1' else False
    if randomize:
        shuffle(images_urls)

    # Parse images, check for errors
    for url in images_urls:
        try:
            response = requests.get(url)
            images_list.append(Image.open(BytesIO(response.content)))
        except IOError:
            return 'Could not get one of the pictures', 400

    # Determine generic sizes for images in mosaic
    x_is_longer = resolution[0] >= resolution[1]
    if len(images_list) == 1:
        longer_side = resolution[0]
        shorter_side = resolution[1]
        if not x_is_longer:
            (longer_side, shorter_side) = (shorter_side, longer_side)
    else:
        longer_side = max(resolution) // ((len(images_list) + 1) // 2)
        shorter_side = min(resolution) // 2
    if longer_side < shorter_side:
        longer_side, shorter_side = shorter_side, longer_side

    # Keep track of where current image in mosaic should be
    current_position_longer = 0
    current_position_shorter = 0

    for i in range(0, len(images_list)):
        # If image has no pairing - extend its size to fill in remaining space
        if i % 2 == 0 and i == len(images_list) - 1:
            shorter_side *= 2
        # Fit the image to proper size and determine its location in final image
        if x_is_longer:
            image = ImageOps.fit(images_list[i], (longer_side, shorter_side))
            location = (current_position_longer, current_position_shorter, current_position_longer + longer_side,
                        current_position_shorter + shorter_side)
        else:
            image = ImageOps.fit(images_list[i], (shorter_side, longer_side))
            location = (current_position_shorter, current_position_longer, current_position_shorter + shorter_side,
                        current_position_longer + longer_side)
        # Paste created image into mosaic
        final_image.paste(image, location)
        # Move to next position in the mosaic
        current_position_shorter += shorter_side
        current_position_longer = current_position_longer + longer_side \
            if current_position_shorter > 0.9 * min(resolution) \
            else current_position_longer
        current_position_shorter = 0 \
            if current_position_shorter > 0.9 * min(resolution) \
            else current_position_shorter

    return serve_pil_image(final_image)


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


if __name__ == '__main__':
    app.run()
