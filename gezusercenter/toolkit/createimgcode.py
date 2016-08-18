# -- encoding: utf-8 --
__author__ = 'PD-002'

import os
import string
import random
import StringIO
import base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class CreateImgCode:
    """
        生产验证码图片
    """
    fontPath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resource/fonts/simkai.ttf')
    img_width = 200
    img_height = 50
    ft = "png"

    # 获得随机四个字母
    @staticmethod
    def get_random_char():
        return [random.choice(string.letters + '23456789') for _ in range(4)]

    # 获取随机颜色
    @staticmethod
    def get_random_color():
        return (random.randint(30, 100), random.randint(30, 100), random.randint(30, 100))

    # 获得验证码图片
    @classmethod
    def get_code_picture(cls):
        image = Image.new('RGB', (cls.img_width, cls.img_height), (180, 180, 180))
        font = ImageFont.truetype(cls.fontPath, 50)
        draw = ImageDraw.Draw(image)
        code = cls.get_random_char()
        for t in range(4):
            draw.text((50 * t + 10, 0), code[t], font=font, fill=cls.get_random_color())
        for _ in range(random.randint(1500, 3000)):
            draw.point((random.randint(0, cls.img_width), random.randint(0, cls.img_height)), fill=cls.get_random_color())
        image = image.filter(ImageFilter.BLUR)
        # 保存到文件
        # image.save("".join(code) + '.jpg', 'jpeg')
        # 保存为字符流
        out = StringIO.StringIO()
        image.save(out, CreateImgCode.ft)
        content = base64.b64encode(out.getvalue())
        return "".join(code), content

if __name__ == "__main__":
    data = CreateImgCode.get_code_picture()
    fd = open("aa.png", "wb+")
    fd.write(data)
    fd.close()