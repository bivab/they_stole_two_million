import pygame
from pygame.locals import *

import pyknic

from pyknic.collision import AABBCollisionStrategy
from pyknic.entity import Entity
from pyknic.entity import Spr
from pyknic.geometry import Vec3
from pyknic.geometry import Vec3

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
