import pygame

import pyknic
from pyknic.collision import AABBCollisionStrategy
from pyknic.entity import Entity
from pyknic.entity import Spr
from pyknic.geometry import Vec3
from pyknic.resources.tiledtmxloader import TileMapParser, ImageLoaderPygame

from entities import InteractiveThing, Player, ActionMenu
from ui import SimpleRenderer
from world import TheWorld

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
                    thing = InteractiveThing(obj.x, obj.y, obj.width, obj.height, obj.properties)
                    actionables.append(thing.blow_up())
                    impassables.append(thing)
                    self.world.add_entity(thing)

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

        self.setup_update_events()

    def setup_update_events(self):
        self.game_time.event_update += self.action_menu.update
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
