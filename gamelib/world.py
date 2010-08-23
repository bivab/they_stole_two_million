# -*- coding: utf-8 -*-
# 
import pyknic
import pyknic.timing
import pyknic.world
import pyknic.utilities
import pyknic.animation

from pyknic.utilities import SortedList
from pyknic.timing import GameTime
from pyknic.geometry import Vec3
from pyknic.entity import Entity
from pyknic.entity import Spr
from pyknic import renderer
from pyknic import gui


import pygame
from pygame.sprite import DirtySprite
from pygame.locals import *

import random

from pyknic.resources.tiledtmxloader import TileMapParser, ImageLoaderPygame



class PlayState(pyknic.State):
    def __init__(self,  *args, **kwargs):
        super(PlayState, self).__init__(*args, **kwargs)
        self.world = TheWorld()
        self.game_time = pyknic.timing.GameTime()

        
    def on_init(self, app):
        world_map = TileMapParser().parse_decode("data/testtile.tmx")
        world_map.load(ImageLoaderPygame())
        assert world_map.orientation == "orthogonal"
        for layernum, layer in enumerate(world_map.layers[:]):
            if layer.visible:
                layer_img = pygame.Surface((layer.pixel_width, layer.pixel_height))
                layer_img.fill((255, 0, 255))
                layer_img.set_colorkey((255, 0, 255))
                idx = 0
                for y in xrange(0, layer.pixel_height, world_map.tileheight):
                    for x in xrange(0, layer.pixel_width, world_map.tilewidth):
                        img_idx = layer.decoded_content[idx]
                        idx += 1
                        if img_idx:
                            offx, offy, screen_img = world_map.indexed_tiles[img_idx]
                            screen_img = screen_img.convert()
                            if layer.opacity > -1:
                                screen_img.set_alpha(None)
                                alpha_value = int(255. * float(layer.opacity))
                                screen_img.set_alpha(alpha_value)
                            layer_img.blit(screen_img.convert(), (x + offx, y + offy))
                print layer.name, layer.opacity
                layer_img.set_alpha(int(255. * float(abs(layer.opacity))))
                spr = Spr()
                spr.image = layer_img.convert_alpha()
                ent = Entity(spr, Vec3(0, 0))
                ent.rect.size = spr.image.get_size()
                ent.layer = layernum * 10
                self.world.add_entity(ent)
                self.game_time.event_update += ent.update


        cam_rect = pygame.display.get_surface().get_rect()
#        cam_rect = pygame.Rect(0, 0, 360, 560)
        self.renderer1 = SimpleRenderer(self, cam_rect)
        self.game_time.event_update += self.renderer1.update
        self.world.add_renderer(self.renderer1)
#        self.game_time.event_update += self.update
        self.game_time.event_update += self.render
                
                
    def render(self, gdt, gt, dt, t, get_surface=pygame.display.get_surface, flip=pygame.display.flip):
        screen_surf = get_surface()
        screen_surf.fill((255, 0, 255))
        self.world.render(screen_surf)
#        self.screen_space.render(screen_surf)
        # draw debug rect for renderers
#        pygame.draw.rect(screen_surf, (255, 0, 0), self.renderer1.rect, 1)
#        pygame.draw.rect(screen_surf, (255, 0, 0), self.renderer2.rect, 1)
#        [ent.render(screen_surf) for ent in self.screen_space]
#        self.screen_mouse.render(screen_surf)
#        print '-------------- render'
        flip()        

        
        
class TheWorld(pyknic.world.IWorld):
    def add_entity(self, entity):
        if entity not in self._entities:
            self._entities.append(entity)

    def remove_entity(self, entity):
        if entity in self._entities:
            self._entities.remove(entity)

    def get_entities_in_region(self, world_rect):
        u"""should return a ordered by layer list of entites to of this region"""
        return [self._entities[i] for i in world_rect.collidelistall(self._entities)]

    def screen_to_world(self, screen_coord):
        r = pygame.Rect(screen_coord, (0, 0))
        idx = r.collidelist(self._renderers)
        if idx > -1:
            return self._renderers[idx].screen_to_world(screen_coord)
        return None

    def get_entites_from_screen_coords(self, screen_coord):
        r = pygame.Rect(screen_coord, (0, 0))
        for idx in r.collidelistall(self._renderers):
            world_rect = pygame.Rect(self._renderers[idx].screen_to_world(screen_coord).as_xy_tuple(), (0, 0))
            entities = self.get_entities_in_region(world_rect)
            if entities:
                return entities
        return None
    

class SimpleRenderer(pyknic.renderer.IRenderer):

    def __init__(self, state, cam_rect):
        super(SimpleRenderer, self).__init__(cam_rect)
        self.state = state

    def render(self, screen_surf, offset=None):
        if self._world:
            self.world_rect.center = self.position.as_xy_tuple()
            offset = self.position - self.vec_center
            clipped_surf = screen_surf.subsurface(self.rect)
            [entity.render(clipped_surf, offset, self.screen_pos) for entity in self._world.get_entities_in_region(self.world_rect)]
    def screen_to_world(self, coord):
        x = self.position.x + coord[0] - self.rect.topleft[0] - self.vec_center.x
        y = self.position.y + coord[1] - self.rect.topleft[1]- self.vec_center.y
        return Vec3(x, y)

    def on_screenmouse_enter(self, world_coord, dragging):
        print 'simple m enter',  world_coord, self
        self.state.screen_mouse.spr.image.fill((255, 0, 0))

    def on_screenmouse_leave(self, world_coord, dragging):
        print 'simple m leave',  world_coord, self
        self.state.screen_mouse.spr.image.fill((255, 255, 255))

    def hit(self, coord):
        return self.rect.collidepoint(coord.as_xy_tuple())
        
        