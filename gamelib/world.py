# -*- coding: utf-8 -*-
# 
import pyknic
import pyknic.world
import pygame
from pygame.locals import *

import pyknic.resources.tiledtmxloader


class PlayState(pyknic.State):
    def __init__(self,  *args, **kwargs):
        super(PlayState, self).__init__(*args, **kwargs)
        self.world = TheWorld()

        
    def on_init(self, app):
        pass
        
        
        
class TheWorld(pyknic.world.IWorld):
    pass