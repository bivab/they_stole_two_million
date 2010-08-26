import pyknic
from pyknic.geometry import Vec3
from pyknic.utilities import SortedList
from pyknic.timing import GameTime
from pyknic.resources.tiledtmxloader import TileMapParser, ImageLoaderPygame

class SimpleRenderer(pyknic.renderer.IRenderer):

    def __init__(self, state, cam_rect):
        super(SimpleRenderer, self).__init__(cam_rect)
        self.state = state

    def render(self, screen_surf, offset=None):
        if self._world:
            offset = Vec3(0,0)
            clipped_surf = screen_surf.subsurface(self.rect)
            ents = SortedList(self._world.get_entities_in_region(self.rect), lambda e: -e.position.z + e.layer)
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

