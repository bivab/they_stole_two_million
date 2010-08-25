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
        self.moving = Vec3(0,0)
        super(Player, self).__init__(spr, position, velocity, acceleration, coll_rect)
        self.rect.size = img.get_size()

    def update(self, gdt, gt, dt, t, *args, **kwargs):
        if self.target:
            self.position = self.target.position
            self.rect.center = self.position.as_xy_tuple()

    def update_x(self, gdt, gt, dt, t, *args, **kwargs):
        dt = gdt * self.t_speed
        self.velocity.x += self.t_speed * dt * self.acceleration.x
        self.position.x += self.t_speed * dt * self.velocity.x
        self.moving.x = self.velocity.x
        self.moving.y = 0
        self.rect.center = self.position.as_xy_tuple()

    def update_y(self, gdt, gt, dt, t, *args, **kwargs):
        dt = gdt * self.t_speed
        self.velocity.y += self.t_speed * dt * self.acceleration.y
        self.position.y += self.t_speed * dt * self.velocity.y
        self.moving.x = 0
        self.moving.y = self.velocity.y
        self.rect.center = self.position.as_xy_tuple()

    def collision_response(self, other):
        if not self.rect.colliderect(other.rect):
            return

        # smashing into wall from left
        if self.moving.x > 0 and self.rect.right > other.rect.left:
            self.rect.right = other.rect.left

        # smashing into wall from right
        if self.moving.x < 0 and self.rect.left < other.rect.right:
            self.rect.left = other.rect.right

        # smashing into wall from above
        if self.moving.y > 0 and self.rect.bottom > other.rect.top:
            self.rect.bottom = other.rect.top

        # smashing into wall from below
        if self.moving.y < 0 and self.rect.top < other.rect.bottom:
            self.rect.top = other.rect.bottom

        self.moving = Vec3(0,0)
        self.position = Vec3(*self.rect.center)

    def on_key_down(self, key, mod, unicode):
        speed = 50
        if key == K_UP:
            self.velocity.y = -speed
        if key == K_DOWN:
            self.velocity.y = speed
        if key == K_LEFT:
            self.velocity.x = -speed
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
