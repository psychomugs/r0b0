#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

EVENTS = ['draw_image']

class EInk(Gadget):
    def __init__(self, config, **kwargs):
        Gadget.__init__(self,config,**kwargs)
        self.handle_events(EVENTS)
        self.epd = epd2in7.EPD()
        self.epd.init()
        self.epd.Clear(0xFF)

    @decode_msg
    def draw_image_event(self, data):
        Himage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 255: clear the frame

        image_stream = io.BytesIO(data['image'])
        image = Image.open(image_stream)
        draw = ImageDraw.Draw(image)

        self.epd.display(self.epd.getbuffer(image))

    
        pass