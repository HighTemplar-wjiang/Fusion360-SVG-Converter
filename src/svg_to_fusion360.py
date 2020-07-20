# Convert Inkscape (standard) svg files to Fusion 360 importable svg files.
# Note: Fusion 360's svg import function is incomplete, with a slightly different format.

from lxml import etree
import numpy as np

class SVGTransformer:

    # Deal with SVG transforms

    def __init__(self, x, y):
        self.coord = np.array([[x], [y], [1]])

    def translate(self, tx, ty):
        self.coord = np.dot([[1, 0, tx], [0, 1, ty], [0, 0, 0]], self.coord)

    def scale(self, sx, sy):
        self.coord = np.dot([[sx, 0, 0], [0, sy, 0], [0, 0, 1]], self.coord)

    def rotate(self, a, cx=0., cy=0.):
        a_rad = np.deg2rad(a)
        self.coord = np.dot([
            [np.cos(a_rad), -np.sin(a_rad), -cx * np.cos(a_rad) + cy * np.sin(a_rad) + cx], 
            [np.sin(a_rad),  np.cos(a_rad), -cx * np.sin(a_rad) - cy * np.cos(a_rad) + cy], 
            [0, 0, 1]], self.coord)

    def parse_transform(self, transform: str):

        # Sanity check.
        if (transform is None) or (len(transform) == 0):
            return 

        # Clearning.
        transform = transform.replace(",", " ")
        transform = transform.replace("  ", " ")

        # Processing in order.
        transform_list = transform.split(" ")
        local_context = {k: getattr(self, k) for k in dir(self)}
        for transform_item in transform_list:
            eval(transform_item, globals(), local_context)


class SVGConverter:

    def __init__(self):
        pass

    def convert(self, source_file_path, destination_file_path):
        with open(source_file_path, "r") as f:
            svg = etree.parse(f)

        # Find all texts.
        text_list = svg.xpath("//svg:text", namespaces={"svg": "http://www.w3.org/2000/svg"})
        for text in text_list:

            # print(etree.tostring(text))

            if text is not None:
                # Get attributes.
                x = float(text.get("x"))
                y = float(text.get("y"))
                transform = text.get("transform")

                # Transform.
                svg_transformer = SVGTransformer(x, y)
                svg_transformer.parse_transform(transform)

                # Set new coordinates.
                x_, y_, _ = svg_transformer.coord.flatten()
                text.set("x", "{:8f}".format(x_))
                text.set("y", "{:8f}".format(y_))

                # Remove intermediate nodes. 
                content = text.xpath(".//text()")[0]
                for e in list(text):
                    text.remove(e)
                text.text = content

        svg.write(destination_file_path)

        return text_list

if __name__ == "__main__":
    svg = SVGTransformer(176.86084, 2.8143532)
    svg.parse_transform("rotate(-96.620796)")
    print(svg.coord)

    converter = SVGConverter()
    text_list = converter.convert("./texts.svg", "./converted.svg")

