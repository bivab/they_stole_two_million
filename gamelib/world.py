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
        world_map = TileMapParser().parse_decode_load("data/testtile.tmx", ImageLoaderPygame())
        assert world_map.orientation == "orthogonal"
        impassables = []
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
                print layer.x, layer.y
                print layer.name, layer.opacity
                print layer.properties
                layer_img.set_alpha(int(255. * float(abs(layer.opacity))))
                spr = Spr()
                spr.image = layer_img.convert_alpha()
                ent = Entity(spr, Vec3(0, 0))
                ent.rect.size = spr.image.get_size()
                ent.layer = layernum * 10
                try:
                    if layer.properties['passable'] == 'false':
                        impassables.append(ent)
                        print impassables
                except KeyError:
                    pass
                self.world.add_entity(ent)
                self.game_time.event_update += ent.update


        cam_rect = pygame.display.get_surface().get_rect()
        self.renderer1 = SimpleRenderer(self, cam_rect)
        self.world.add_renderer(self.renderer1)
        self.game_time.event_update += self.renderer1.update

        player = Player(self)
        player.position.x = 20
        player.position.y = 20
        player.layer = 10000
        self.world.add_entity(player)
        self.game_time.event_update += player.update

        self.coll_detector = pyknic.collision.CollisionDetector()
        self.coll_detector.register_once('player', 'walls', [player], [impassables], \
                    PlayerWallCollisionStrategy(), (Player, Entity), self.coll_player_wall)



#        self.game_time.event_update += self.update
        self.game_time.event_update += self.render


    def render(self, gdt, gt, dt, t, get_surface=pygame.display.get_surface, flip=pygame.display.flip):
        screen_surf = get_surface()
        screen_surf.fill((0, 0, 0))
        self.world.render(screen_surf)
        flip()

    def coll_player_wall(self, player, wall, depth):
        print player, wall

class PlayerWallCollisionStrategy(object):
    def check_broad(self, name1, name2, coll_groups):
        print name1, name2, coll_groups
        return pyknic.collision.brute_force_rect(coll_groups[name1], coll_groups[name2])

    def check_narrow(self, pairs_list, coll_funcs):
            # check for collision
            print pairs_list
            for player, wall in pairs_list:
                d = player.position - wall.position
                n = d.project_onto(wall.normal)
                n_len = n.length
                # check length of wall also
                if n_len <= player.bounding_radius and n.dot(wall.normal)>0:
                    # collision response
                    coll_funcs[(ball.__class__, wall.__class__)](player, wall, player.bounding_radius - n_len)



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
            #offset = self.position - self.vec_center
            offset = Vec3(0,0)
            clipped_surf = screen_surf.subsurface(self.rect)
            #[entity.render(clipped_surf, offset, self.screen_pos) for entity in self._world.get_entities_in_region(self.world_rect)]
            ents = SortedList(self._world.get_entities_in_region(self.world_rect), lambda e: -e.position.z + e.layer)
            for entity in ents:
                entity.render(clipped_surf, offset, self.screen_pos)
#                if entity.position.z > -900:
#                    scale = 1000. / (entity.position.z + 1000.)
#                    if scale == 1.0:


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


class MyEntity(pyknic.entity.Entity):

    def __init__(self, state):
        super(MyEntity, self).__init__()
        self.state = state
        spr = Spr()
        spr.image = pygame.Surface((16, 16))
        spr.image.fill((255, 0, 0))
        super(MyEntity, self).__init__(spr, Vec3(random.randint(0, 255), random.randint(0, 255)))
        self.rect.w = 16
        self.rect.h = 16
        self._off = Vec3(0, 0)

    def update(self, gdt, gt, dt, t):
        super(MyEntity, self).update(gdt, gt, dt, t)
        if self.target:
            self.position = self.target.position + self._off
            self.rect.center = self.position.as_xy_tuple()

    def elapsed(self):
        self.position += Vec3(10, 10)


class Player(MyEntity):
    pass
    #def __init__(self, state):
    #    super(Player, self).__init__(state)
    #    #anims = pyknic.animation.load_animation(state.game_time, 'data/myanim')
    #    #self.sprites = {}
    #    #self.sprites[pyknic.utilities.utilities.Direction.N] = anims['up']
    #    #self.sprites[pyknic.utilities.utilities.Direction.S] = anims['down']
    #    #self.sprites[pyknic.utilities.utilities.Direction.E] = anims['right']
    #    #self.sprites[pyknic.utilities.utilities.Direction.W] = anims['left']
    #    #self.spr = self.sprites[pyknic.utilities.utilities.Direction.S]

    def update(self, gdt, gt, dt, t):
        super(Player, self).update(gdt, gt, dt, t)
        self.position.x += 3
        self.position.y += 3
    #    if self.velocity.lengthSQ:
    #        #self.spr.play()
    #        #dir = pyknic.utilities.utilities.get_4dir(self.velocity.angle)
    #        #self.spr = self.sprites[dir]
    #        pass
    #    else:
    #        #self.spr.pause()
    #        pass
    def collision_response(self, other):
        print other
