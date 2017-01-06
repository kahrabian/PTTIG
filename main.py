import os

from image_generator.generator import ImageGenerator

if __name__ == '__main__':
    # Example Use
    img_generator = ImageGenerator(file_path=os.path.join(os.getcwd(), 'test_txt.dat'))
    img_generator.generate()
