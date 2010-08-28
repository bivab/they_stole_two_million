import pyknic, pygame
import math
from pygame.locals import *
from pyknic.geometry import Vec3
from pyknic.utilities import SortedList
from pyknic.timing import GameTime
from pyknic.resources.tiledtmxloader import TileMapParser, ImageLoaderPygame

class SimpleRenderer(pyknic.renderer.IRenderer):

    def __init__(self, state, cam_rect):
        super(SimpleRenderer, self).__init__(cam_rect)
        self.state = state
        self.target = self.state.player

    def render(self, screen_surf, offset=None):
        self.position = self.target.position

        if self._world:
            clipped_surf = screen_surf.subsurface(self.rect)
            offset = (self.position - self.vec_center)

            #search_rect = self.rect.move(offset.as_xy_tuple())
            #ents = SortedList(self._world.get_entities_in_region(search_rect), lambda e: -e.position.z + e.layer)

            layers = [self.state.lighting] + self._world._entities

            for layer in SortedList(layers, lambda e: -e.position.z + e.layer):
                layer.render(clipped_surf, offset)



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

class StatusBar(pyknic.renderer.IRenderer):
    def __init__(self, state, cam_rect):
        super(StatusBar, self).__init__(cam_rect)
        self.state = state
        self.player = self.state.player

    def render(self, screen_surf, offset=None):
        clipped_surf = screen_surf.subsurface(self.rect)
        clipped_surf.fill((255,255,0))

        line_offset = 1
        font = pygame.font.Font(None,25)

        values = {'money':self.player.money, 'energy':self.player.energy}
        s = '$$$: %(money)d | Energy: %(energy)d' % values
        text = font.render(s,1,(255,0,0))
        clipped_surf.blit(text, (1, line_offset))

        line_offset += text.get_height()




