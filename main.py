import os

from ptig.generators import PersianGenerator

if __name__ == '__main__':
    # Example Use
    img_generator = PersianGenerator(os.path.join(os.getcwd(), 'test_txt.dat'), 'windows-1256')
    img_generator.generate()
