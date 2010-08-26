# -*- coding: utf-8 -*-
import pygame

import pyknic
from pyknic.entity import Entity, Spr
from pyknic.geometry import Vec3
from pyknic.resources.tiledtmxloader import TileMapParser, ImageLoaderPygame
from pyknic.collision import AABBCollisionStrategy


from world import TheWorld
from entities import InteractiveThing, Player, ActionMenu, Guard, Fog

from ui import SimpleRenderer

import pygame

class StartState(pyknic.State):
    def __init__(self,  *args, **kwargs):
        super(StartState, self).__init__(*args, **kwargs)
        self.levels = ['testtile', 'level1', 'Level2']
        self.selected_level = 0
    
    def on_init(self, app):
        self.draw_menu(0)
    
    def on_resume(self):
        self.draw_menu(self.selected_level)

    def on_key_down(self, key, mod, unicode):
        u"""Default event handler for key presses.
         - escape: pops this state
         - F3: take a screenshot
        
        """
        if pygame.K_ESCAPE == key:
            self.on_quit()
        elif pygame.K_F3 == key:
            pyknic.utilities.take_screenshot(self.the_app.config['paths']['screenshots'])
        elif key == pygame.K_UP:
            if self.selected_level > 0:
                self.draw_menu(self.selected_level-1)
        elif key == pygame.K_DOWN:
            if self.selected_level+1 < len(self.levels):
                self.draw_menu(self.selected_level+1)
        elif key == pygame.K_RETURN:
            self.start_level(self.selected_level)

    def draw_menu(self, selected_level=None):
        self.selected_level = selected_level
        
        font = pygame.font.SysFont("Dejavu Sans", 18)
        title = font.render(self.the_app.config['display']['caption'], True, (0, 255, 0))
        s = pygame.display.get_surface()
        s.fill((0,0,0))
        r = s.blit(title, (0,0))

        for i, level in enumerate(self.levels):
            if i == selected_level:
                color = (255,0,0)
            else:
                color = (0,255,0)
            levelfont = font.render(level, True, color)
            r = s.blit(levelfont, (0, r.bottom))

        pygame.display.flip()

    def start_level(self, level):
        l = self.levels[level]
        print "Starting %s" % l
        self.the_app.push_state(PlayState(l))

class PlayState(pyknic.State):
    def __init__(self, level = 'testtile', *args, **kwargs):
        super(PlayState, self).__init__(*args, **kwargs)
        self.world = TheWorld()
        self.game_time = pyknic.timing.GameTime()
        self.level = level


    def on_init(self, app):
        world_map = TileMapParser().parse_decode_load("data/%s.tmx" % self.level, ImageLoaderPygame())
        assert world_map.orientation == "orthogonal"
        impassables = []
        actionables = []

       ## test spotlight
       #black_surface = pygame.Surface((1024,768), pygame.SRCALPHA)
       #black_surface.fill((0,0,0,150))
       ##black_surface.set_alpha(100)
       ##black_surface.set_colorkey((255,255,255))
       #black_layer = Spr()
       #black_layer.image = black_surface
       #black_ent = Entity(black_layer, Vec3(0, 0))
       #black_ent.rect.size = black_layer.image.get_size()
       #black_ent.layer = 10000
        
       #spot_surface = pygame.Surface((100,100), pygame.SRCALPHA)
       #spot_surface.fill((0,0,0,255))
       ##spot_surface.set_alpha(100)
       #pygame.draw.circle(spot_surface, (255,255,255,0), (50,50), 50)
       #black_surface.blit(spot_surface,(10,10), None, pygame.BLEND_RGBA_MIN)

       #self.world.add_entity(black_ent)

        for layernum, layer in enumerate(world_map.layers[:]):
            if layer.visible:
                layer_img = pygame.Surface((layer.pixel_width, layer.pixel_height), pygame.SRCALPHA)
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
                    thing = InteractiveThing(obj.x, obj.y, obj.width, \
                                obj.height, obj.properties, obj.type, \
                                impassables)
                    actionables.append(thing.blow_up())
                    impassables.append(thing)
                    self.world.add_entity(thing)
                    self.game_time.event_update += thing.update

        cam_rect = pygame.display.get_surface().get_rect()
        self.renderer1 = SimpleRenderer(self, cam_rect)
        self.world.add_renderer(self.renderer1)

        self.player = Player(None, Vec3(64, 64), None, None, None,self)
        self.world.add_entity(self.player)

        self.guard = Guard(None, Vec3(320, 32), None, None, None, self)
        self.world.add_entity(self.guard)

        self.action_menu = ActionMenu(self.the_app.screen, self.player, actionables)
        self.world.add_entity(self.action_menu)

        self.fog = Fog(self.player)
        self.world.add_entity(self.fog)

        self.events.key_down += self.player.on_key_down
        self.events.key_down += self.action_menu.on_key_down
        self.events.key_up += self.player.on_key_up

        self.coll_detector = pyknic.collision.CollisionDetector()
        self.coll_detector.register_once('player', 'walls', [self.player], impassables, \
                    AABBCollisionStrategy(), (Player, Entity), self.coll_player_wall)
        self.enemy_coll_detector = pyknic.collision.CollisionDetector()
        self.enemy_coll_detector.register_once('guard', 'walls', [self.guard], [self.player]+impassables, \
                    AABBCollisionStrategy(), (Guard, Entity), self.guard.collidate_wall)
        self.setup_update_events()

    def setup_update_events(self):
        self.game_time.event_update += self.action_menu.update
        self.game_time.event_update += self.update
        self.game_time.event_update += self.render
        self.game_time.event_update += self.renderer1.update
        self.game_time.event_update += self.player.update
        self.game_time.event_update += self.guard.update
        #self.game_time.event_update += self.guard.update

    def render(self, gdt, gt, dt, t, get_surface=pygame.display.get_surface, flip=pygame.display.flip):
        screen_surf = get_surface()
        screen_surf.fill((0, 0, 0))
        self.world.render(screen_surf)
        flip()

    def coll_player_wall(self, player, wall, dummy = 0):
        player.collision_response(wall)

    def update(self, gdt, gt, dt, t, *args):
        pass
