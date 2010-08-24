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
from pyknic.collision import AABBCollisionStrategy
import pdb

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
        actionables = []
        
        for layernum, layer in enumerate(world_map.layers[:]):
            if layer.visible:
                layer_img = pygame.Surface((layer.pixel_width, layer.pixel_height))
                layer_img.fill((255, 0, 255))
                layer_img.set_colorkey((255, 0, 255))
                idx = 0

                impassable = False
                try:
                    impassable = layer.properties['passable'] == 'false'
                except KeyError:
                    pass

                spr = Spr()
                for y in xrange(0, layer.pixel_height, world_map.tileheight):
                    for x in xrange(0, layer.pixel_width, world_map.tilewidth):
                        img_idx = layer.decoded_content[idx]
                        idx += 1
                        if img_idx:
                            offx, offy, screen_img = world_map.indexed_tiles[img_idx]

                            if impassable:
                                ent = Entity(None, Vec3(x + offx, y + offy))
                                ent.rect.size = screen_img.get_size()
                                ent.layer = layernum * 10
                                impassables.append(ent)

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

                self.world.add_entity(ent)
                self.game_time.event_update += ent.update

                
        # map objects
        for obj_group in world_map.object_groups:
            for obj in obj_group.objects:
                if hasattr(obj, 'type'):
                    thing = InteractiveThing(obj.x, obj.y, obj.width, obj.height)
                    actionables.append(thing)

        cam_rect = pygame.display.get_surface().get_rect()
        self.renderer1 = SimpleRenderer(self, cam_rect)
        self.world.add_renderer(self.renderer1)
        self.game_time.event_update += self.renderer1.update

        self.player = Player(None, Vec3(32, 32))
        self.world.add_entity(self.player)
        self.game_time.event_update += self.player.update
        
        self.action_menu = ActionMenu(self.the_app.screen, self.player, actionables)
        self.world.add_entity(self.action_menu)
        
        self.events.key_down += self.player.on_key_down
        self.events.key_down += self.action_menu.on_key_down
        self.events.key_up += self.player.on_key_up

        self.coll_detector = pyknic.collision.CollisionDetector()
        self.coll_detector.register_once('player', 'walls', [self.player], impassables, \
                    AABBCollisionStrategy(), (Player, Entity), self.coll_player_wall)
        
        self.game_time.event_update += self.update
        self.game_time.event_update += self.render

    def render(self, gdt, gt, dt, t, get_surface=pygame.display.get_surface, flip=pygame.display.flip):
        screen_surf = get_surface()
        screen_surf.fill((0, 0, 0))
        self.world.render(screen_surf)
        flip()

    def coll_player_wall(self, player, wall, dummy = 0):
        player.collision_response(wall) 
        
    def update(self, gdt, gt, dt, t, *args):
        self.coll_detector.check()
                                        
class ActionMenu(pyknic.entity.Entity):
    def __init__(self, screen, player, actionables):
        Entity.__init__(self, spr=Spr(image=pygame.Surface((100, 100)) ))
        self.screen = screen
        self.player = player
        self.visible = False
        self.layer = 1000000
        self.actionable_detector = pyknic.collision.CollisionDetector()
        self.actionable_detector.register_once('player', 'stuff', [self.player], actionables, \
                    AABBCollisionStrategy(), (Player, InteractiveThing), self.coll_player_stuff)
        
    def on_key_down(self, key, mod, code):
        if code != 'a':
            return
        self.visible = not self.visible
        if self.visible == True:
            # update menu
            self.actionable_detector.check()


    def coll_player_stuff(self, player, thing):
        print "fuufuuu@#$@#$"
    
    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        if not self.visible:
            return
        font = pygame.font.Font(None,25)
        text = font.render("YourText",1,(255,255,255,0)) #font.render( Text , antialias , Color(r,g,b,a))
        screen_surf.blit(text,(10,100)) #screen = yoursurface
                
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

class InteractiveThing(pyknic.entity.Entity):
    def __init__(self, x, y, width, height):
        Entity.__init__(self, None, Vec3(x, y))
        self.bounding_radius = 16
        self.rect.size = (width, height)
        self.layer =  1

class Player(pyknic.entity.Entity):
    def __init__(self, spr=None, position=None, velocity=None, acceleration=None, coll_rect=None):
        img = pygame.Surface((16, 16))
        img.fill((255, 0, 0))
        spr = Spr(img, offset=Vec3(8,8))
        self.layer = 10000
        super(Player, self).__init__(spr, position, velocity, acceleration, coll_rect)
        self.rect.size = img.get_size()

    def collision_response(self, other):
        print self.rect, other.rect
        print self.velocity
        import math
        if self.velocity.x > 0 and self.position.x < other.position.x:
            self.position.x -= 1
            self.velocity.x = 0
        if self.velocity.x < 0 and self.position.x > other.position.x:
            self.position.x += 1
            self.velocity.x = 0
        if self.velocity.y > 0 and self.position.y < other.position.y:
            self.position.y -= 1
            self.velocity.y = 0
        if self.velocity.y < 0 and self.position.y > other.position.y:
            self.position.y += 1
            self.velocity.y = 0

    def on_key_down(self, key, mod, unicode):
        speed = 50
        if key == K_UP:
            self.velocity.y = -1 * speed
        if key == K_DOWN:
            self.velocity.y = speed
        if key == K_LEFT:
            self.velocity.x = -1 * speed
        if key == K_RIGHT:
            self.velocity.x = speed
        #print key, mod, unicode

    def on_key_up(self, key, mod):
        if key == K_UP:
            self.velocity.y = 0
        if key == K_DOWN:
            self.velocity.y = 0
        if key == K_LEFT:
            self.velocity.x = 0
        if key == K_RIGHT:
            self.velocity.x = 0
        #print key, mod
