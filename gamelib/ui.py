import pyknic, pygame
from pyknic.geometry import Vec3
from pyknic.utilities import SortedList
from pyknic.timing import GameTime
from pyknic.resources.tiledtmxloader import TileMapParser, ImageLoaderPygame

class SimpleRenderer(pyknic.renderer.IRenderer):

    def __init__(self, state, cam_rect, player):
        # cam_rect = resolution, world_rect = visible, world
        super(SimpleRenderer, self).__init__(cam_rect)
        self.player = player
        self.state = state

    def render(self, screen_surf, offset=None):
        if self._world:
            # place word relatively to the players position
            offset = Vec3(self.player.position.x-screen_surf.get_width()/2, self.player.position.y-screen_surf.get_height()/2)
            clipped_surf = screen_surf.subsurface(self.rect)
            # also change the display rect
            search_rect = pygame.Rect(offset.x, offset.y, screen_surf.get_width(), screen_surf.get_height())
            ents = SortedList(self._world.get_entities_in_region(search_rect), lambda e: -e.position.z + e.layer)
            #ents = SortedList(self._world._entities, lambda e: -e.position.z + e.layer)
            for entity in ents:
                entity.render(clipped_surf, offset, self.screen_pos)

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

