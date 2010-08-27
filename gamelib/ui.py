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
        if self._world:
            clipped_surf = screen_surf.subsurface(self.rect)
            offset = (self.position - self.vec_center)

            #search_rect = self.rect.move(offset.as_xy_tuple())
            #ents = SortedList(self._world.get_entities_in_region(search_rect), lambda e: -e.position.z + e.layer)

            ents = SortedList(self._world._entities, lambda e: -e.position.z + e.layer)
            font = pygame.font.Font(None,25)

            for i, entity in enumerate(ents):
                entity.render(clipped_surf, offset)

            self.state.lighting.render(clipped_surf, offset)

            #pygame.draw.rect(clipped_surf, (255,0,0), self.rect, 1)

            #center_rect = Rect(0,0,8,8)
            #center_rect.center = self.vec_center.as_xy_tuple()
            #pygame.draw.rect(clipped_surf, (255,0,0), center_rect, 1)

            #s = 'player %(pos)s' % {'pos':str(self.target.position.as_xy_tuple())}
            #text = font.render(s,1,(255,0,0))
            #clipped_surf.blit(text, (1, clipped_surf.get_rect().bottom-25))

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

