import os
from PIL import Image, ImageEnhance


def get_products():
    with open("products.txt", "r") as file:
        products = file.read().splitlines()
    return products


class ImageResizer:
    WATERMARK_IMAGE = os.path.join(os.getcwd(), "watermark.png")
    WATERMARK_TRANSPARENCY = 50

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def resize_image(self, image_path):
        # Open the image using PIL
        with Image.open(image_path) as image:
            # Resize the image
            resized_image = image.resize((self.width, self.height))
            # Return the resized image
            return resized_image

    def add_watermark(self, image):
        with Image.open(self.WATERMARK_IMAGE) as watermark:
            # Set the coordinates for the paste location
            x = image.size[0] - watermark.size[0] + 250
            y = image.size[1] - watermark.size[1] + 250


            if watermark.mode!='RGBA':
                alpha = Image.new('L', watermark.size, 255)
                watermark.putalpha(alpha)
            # else:
            #     watermark.convert('RGBA')
            #     alpha = Image.new('L', watermark.size, 255)
            #     watermark.putalpha(alpha)
            # Create an enhancer object for the image
            # enhancer = ImageEnhance.Brightness(watermark)
            # image_with_transparency = enhancer.enhance(self.WATERMARK_TRANSPARENCY)

            # Resize the watermark
            # image_with_transparency = watermark.resize((180, 180))

            # Add the watermark to the image
            # image.paste(image_with_transparency, (y, x))
            watermark = watermark.resize((180, 180))

            paste_mask = watermark.split()[3].point(lambda i: i * self.WATERMARK_TRANSPARENCY / 100.)
            image.paste(watermark, (x, y), mask=paste_mask)

            # Return the image with the watermark
            return image

    def resize_all(self, dir_path):
        # Get all the images in the directory
        images = os.listdir(dir_path)
        # Loop through the images
        for image in images:
            # check if its a file not a directory
            if not os.path.isfile(os.path.join(dir_path, image)):
                continue

            if image.startswith("."):
                continue

            # Get the image path
            image_path = os.path.join(dir_path, image)
            # Resize the image
            resized_image = self.resize_image(image_path)
            final_image = self.add_watermark(resized_image)

            # Save the image
            final_image.save(image_path)
