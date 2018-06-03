"""
Sorl Thumbnail Engine that accepts background color
---------------------------------------------------

Created on Sunday, February 2012 by Yuji Tomita

Source: https://yuji.wordpress.com/2012/02/26/sorl-thumbnail-convert-png-to-jpeg-with-background-color/
"""
from PIL import Image, ImageColor
from sorl.thumbnail.engines.pil_engine import Engine


class Engine(Engine):
    def create(self, image, geometry, options):
        thumb = super(Engine, self).create(image, geometry, options)
        if options.get('background'):
            try:
                background = Image.new('RGB', thumb.size, ImageColor.getcolor(options.get('background'), 'RGB'))
                background.paste(thumb, mask=thumb.split()[3]) # 3 is the alpha of an RGBA image.
                return background
            except Exception as e:
                return thumb
        return thumb


# NOTE:
# (1) To clear the database of images, run:
# python manage.py thumbnail clear_delete_all
