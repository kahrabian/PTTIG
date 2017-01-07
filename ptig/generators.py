# -*- coding: utf-8 -*-

import os
import math

from bidi.algorithm import get_display
from PIL import ImageFont, Image, ImageDraw

from ptig.arabic_reshaper import reshape


# TODO: Add Config Class


class PersianGenerator(object):
    PERSIAN_NUMBERS = list(reshape(u'۱۲۳۴۵۶۷۸۹۰'))
    ENGLISH_NUMBERS = list(u'1234567890')
    
    DIR_NAME = 'data_set'

    lexical = dict()
    mapping = dict()

    def __init__(self, data_path, data_encoding='utf-8', **kwargs):
        # Data Properties
        self.data_path = data_path
        self.data_encoding = data_encoding

        # Font Properties
        self.font_paths = kwargs.get('font_paths', ['PNazanin.TTF'])
        self.font_sizes = kwargs.get('font_sizes', [12, 14])

        # Image Properties
        self.image_width = kwargs.get('image_width', 600)
        self.image_margin_width = kwargs.get('image_margin_width', 20)
        self.background_color = kwargs.get('background_color', (255, 255, 255))
        self.text_color = kwargs.get('text_color', (0, 0, 0))

        # TODO: Make this customizable
        self.data_sets_names = kwargs.get('data_sets_names', ['train', 'dev', 'val', 'lm'])

    @staticmethod
    def create_directory(dir_name):
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)

    @staticmethod
    def create_and_cd_directory(dir_name):
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        os.chdir(dir_name)

    def create_sub_directories(self):
        for font_path in self.font_paths:
            self.create_and_cd_directory(font_path.split('/')[-1].split('.')[0])
            for font_size in self.font_sizes:
                self.create_directory(str(font_size))
            os.chdir('..')

    def create_directories(self):
        self.create_and_cd_directory(self.DIR_NAME)
        for data_set_name in self.data_sets_names:
            self.create_and_cd_directory(data_set_name)
            self.create_sub_directories()
            os.chdir('..')

    def _reshape_data(self):
        with open(self.data_path, 'r', encoding=self.data_encoding) as f:
            data = '\n'.join([' '.join(data_line.split()[::-1]) for data_line in f.read().split('\n')]).replace('#', '')

            for index, english_digit in enumerate(self.ENGLISH_NUMBERS, 0):
                data.replace(english_digit, self.PERSIAN_NUMBERS[index])

            return get_display(reshape(data)).split()

    def _create_lines(self, font):
        words_list = self._reshape_data()
        max_text_height = 0

        lines = list()
        cur = words_list[0]
        for word in words_list[1:]:
            tmp = u'{word} {cur}'.format(word=word, cur=cur)

            text_width, text_height = font.getsize(tmp)
            max_text_height = max(max_text_height, text_height)

            if text_width > self.image_width - self.image_margin_width:
                lines.append(cur)
                cur = word
            else:
                cur = tmp

        lines.append(cur)
        return lines, max_text_height

    @staticmethod
    def _create_txt(name, text):
        with open('{name}.dat'.format(name=name), 'wb') as out:
            out.write(
                ' '.join([word[::-1] if word.isdigit() else word for word in text.split()])[::-1].encode('utf-8')
            )

    def _map(self, word):
        mapped_word = list()
        for letter in list(word):
            if letter.encode('utf-8') not in self.mapping:
                self.mapping[letter.encode('utf-8')] = chr(200 + len(self.mapping))
            mapped_word.append(self.mapping[letter.encode('utf-8')])

        self.lexical[word] = u''.join(mapped_word)

        return u''.join(mapped_word)

    def _create_mapped_txt(self, name, text):
        text = u' '.join([word[::-1] if word.isdigit() else word for word in text.split()])[::-1]
        with open('{name}.dat2'.format(name=name), 'wb') as out:
            out.write(u' '.join([self._map(word) for word in text.split()]).encode('utf-8'))

    def _create_img(self, font, name, text, max_text_height):
        text_width, text_height = font.getsize(text)
        img = Image.new('RGB', (self.image_width, max_text_height), self.background_color)
        draw = ImageDraw.Draw(img)
        draw.text(
            ((self.image_width - text_width) / 2, (max_text_height - text_height) / 2),
            text.replace('(', '\)').replace(')', '(').replace('\(', ')'), self.text_color, font=font
        )
        img.save('{name}.png'.format(name=name))
        del draw

    def _generate_data_set(self, path, lines, font, max_text_height):
        os.chdir(path)
        for index, line in enumerate(lines, 1):
            self._create_txt(index, line)
            self._create_mapped_txt(index, line)
            self._create_img(font, index, line, max_text_height)
        os.chdir('../../..')

    @staticmethod
    def _generate_language_model(path, lines):
        os.chdir(path)
        flag = 0
        for line in lines:
            with open('language_model.dat', 'ab') as out:
                if flag == 1:
                    out.write(' '.encode('utf-8'))
                out.write(
                    ' '.join([word[::-1] if word.isdigit() else word for word in line.split()])[::-1].encode('utf-8')
                )
            flag = 1
        os.chdir('../../..')

    def _generate_lexical(self):
        with open('lexical.dat', 'wb') as out:
            out.write(u'\n'.join(
                [u'{value} {key}'.format(key=key, value=value) for key, value in self.lexical.items()]
            ).encode('utf-8'))

    def _generate_data_sets(self, font, sub_path):
        lines, max_text_height = self._create_lines(font)
        line_len_1_on_4 = math.ceil(len(lines) / 4)
        line_len_1_on_40 = math.ceil(len(lines) / 40)

        self._generate_data_set(
            os.path.join('train', sub_path),
            lines[:line_len_1_on_4],
            font,
            max_text_height
        )

        self._generate_data_set(
            os.path.join('dev', sub_path),
            lines[line_len_1_on_4:line_len_1_on_4 + line_len_1_on_40],
            font,
            max_text_height
        )

        self._generate_data_set(
            os.path.join('val', sub_path),
            lines[line_len_1_on_4 + line_len_1_on_40:line_len_1_on_4 + 2 * line_len_1_on_40],
            font,
            max_text_height
        )

        self._generate_language_model(
            os.path.join('lm', sub_path),
            lines[line_len_1_on_4 + 2 * line_len_1_on_40:]
        )

        self._generate_lexical()

    def generate(self):
        self.create_directories()

        for font_path in self.font_paths:
            for font_size in self.font_sizes:
                sub_path = os.path.join(font_path.split('/')[-1].split('.')[0], str(font_size))
                self._generate_data_sets(ImageFont.truetype(font_path, font_size), sub_path)
