import io

from PIL import Image

import app
import unittest


class FlaskrTestCase(unittest.TestCase):
    urls = [
        "https://assets.allegrostatic.com/opbox/allegro.pl/homepage/MainP%20-%20Graphics%20Content/7PwTVOCJNsFOAhookAa3Rg-w132-h132.png",
        "https://assets.allegrostatic.com/display-pl/2019/13392/MKT_1648_960x252.jpg",
        "https://assets.allegrostatic.com/opbox/allegro.pl/homepage/Main%20Page/6tge6nQMDg4o4Vcvxvnxvw-w224-h364.jpg",
        "https://assets.allegrostatic.com/opbox/allegro.pl/homepage/MainP%20-%20Graphics%20Content/7PwTVOCJNsFOAhookAa3Rg-w132-h132.png",
        "https://assets.allegrostatic.com/display-pl/2019/13392/MKT_1648_960x252.jpg",
        "https://assets.allegrostatic.com/opbox/allegro.pl/homepage/Main%20Page/6tge6nQMDg4o4Vcvxvnxvw-w224-h364.jpg",
        "https://assets.allegrostatic.com/opbox/allegro.pl/homepage/MainP%20-%20Graphics%20Content/7PwTVOCJNsFOAhookAa3Rg-w132-h132.png",
        "https://assets.allegrostatic.com/display-pl/2019/13392/MKT_1648_960x252.jpg",
        "https://assets.allegrostatic.com/opbox/allegro.pl/homepage/Main%20Page/6tge6nQMDg4o4Vcvxvnxvw-w224-h364.jpg"]

    def setUp(self):
        app.testing = True
        self.app = app.app.test_client()

    def test_no_images(self):
        response = self.app.get("/mozaika")
        assert response.status_code == 400

    def test_default_resolution(self):
        response = self.app.get("/mozaika?zdjecia={0}".format(self.urls[0]))
        image_file = io.BytesIO(response.get_data())
        image = Image.open(image_file)
        width, height = image.size
        assert width == 2048
        assert height == 2048

    def test_custom_resolution(self):
        resolution = "300x300"
        response = self.app.get("/mozaika?rozdzielczosc={0}&zdjecia={1}".format(resolution, self.urls[0]))
        image_file = io.BytesIO(response.get_data())
        image = Image.open(image_file)
        width, height = image.size
        assert width == 300
        assert height == 300

    def test_image_unavailable(self):
        response = self.app.get("/mozaika?zdjecia={0}".format(self.urls[1]+"ughsoubdo"))
        assert response.status_code == 400

    def test_resolution_format_wrong_separator(self):
        resolution = "300,300"
        response = self.app.get("/mozaika?rozdzielczosc={0}&zdjecia={1}".format(resolution, self.urls[2]))
        assert response.status_code == 400

    def test_resolution_format_wrong_dimension(self):
        resolution = "-5x-10"
        response = self.app.get("/mozaika?rozdzielczosc={0}&zdjecia={1}".format(resolution, self.urls[5]))
        assert response.status_code == 400

    def test_multiple_images_same_order(self):
        response1 = self.app.get("/mozaika?zdjecia={0}".format(",".join(self.urls[0:3])))
        response2 = self.app.get("/mozaika?zdjecia={0}".format(",".join(self.urls[0:3])))
        assert response1.get_data() == response2.get_data()

    def test_multiple_images_random(self):
        response1 = self.app.get("/mozaika?losowo=1&zdjecia={0}".format(",".join(self.urls[0:3])))
        response2 = self.app.get("/mozaika?losowo=1&zdjecia={0}".format(",".join(self.urls[0:3])))
        assert response1.get_data() != response2.get_data()

    def test_multiple_images_random_wrong_format(self):
        response1 = self.app.get("/mozaika?losowo=tak&zdjecia={0}".format(",".join(self.urls[0:3])))
        response2 = self.app.get("/mozaika?losowo=nie&zdjecia={0}".format(",".join(self.urls[0:3])))
        assert response1.get_data() == response2.get_data()

    def test_too_many_images(self):
        response = self.app.get("/mozaika?zdjecia={0}".format(",".join(self.urls)))
        assert response.status_code == 400


if __name__ == '__main__':
    unittest.main()
