import pygame
from pygame.locals import *

import pyknic

from pyknic.collision import AABBCollisionStrategy
from pyknic.entity import Entity
from pyknic.entity import Spr
from pyknic.geometry import Vec3
from pyknic.geometry import Vec3

class InteractiveThing(pyknic.entity.Entity):
    def __init__(self, x, y, width, height, properties):
        Entity.__init__(self, None, Vec3(x, y))
        self.rect.size = (width, height)
        self.layer =  1
        self.properties = properties
        self.thing = None#Desk(properties)
        self.layer = 100

    def get_actions(self, player):
        if not self.thing:
            self.thing = Desk(self.properties, self.rect)
        return self.thing.get_actions(player)

    def blow_up(self):
        t = InteractiveThing(self.rect.x-15, self.rect.y-15, \
                            self.rect.width+30, self.rect.height+30, self.properties)
        t.thing = self
        return t


    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        if not self.thing:
            self.thing = Desk(self.properties, self.rect)
        self.thing.render(screen_surf, offset, screen_offset)


class Desk(object):
    def __init__(self, properties, rect):
        self.properties = properties
        self.rect = rect
        self.color = (255, 100, 0)
        self.actions = []
        self.setup()

    def setup(self):
        for key, value in self.properties.items():
            if key == 'rob':
                self.value = int(value)
            if key == 'locked' and value == 'true':
                self.locked = True

    def get_actions(self, player):
        actions = []
        if self.locked:
            actions.append(('Lockpick', self.lockpick))
            actions.append(('Smash', self.smash))
        elif self.value:
            actions.append(('Rob', self.rob))
        return actions

    def open(self, player):
        self.locked = False
        self.color = (0, 255, 0)

    def lockpick(self, player):
        self.open(player)

    def smash(self, player):
        self.open(player)
        self.color = (0,0, 255)

    def rob(self, player):
        player.add_money(self.value)
        self.value = 0
        self.color = (255, 100, 0)

    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        image = pygame.Surface((self.rect.width, self.rect.height))
        image.fill(self.color)

        screen_surf.blit(image, (self.rect.x, self.rect.y))

class Player(pyknic.entity.Entity):
    def __init__(self, spr=None, position=None, velocity=None, acceleration=None, coll_rect=None):
        img = pygame.Surface((16, 16))
        img.fill((255, 0, 0))
        spr = Spr(img, offset=Vec3(8,8))
        self.layer = 10000
        super(Player, self).__init__(spr, position, velocity, acceleration, coll_rect)
        self.rect.size = img.get_size()
        self.money = 0

    def add_money(self, amount):
        self.money += amount
        print 'Wuhooo, I\'m rich %d' % self.money

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
        self.items = []

    def on_key_down(self, key, mod, code):
        if code != 'a':
            if not self.visible:
                return
            try:
                value = int(code) - 1
                if value in xrange(len(self.items)):
                    self.items[value][1](self.player)
            except ValueError:
                pass
        else:
            self.visible = not self.visible
            self.update_items()

    def update_items(self):
        if self.visible == True:
            self.items = []
            # update menu
            self.actionable_detector.check()
        if not self.items:
            self.visible = False


    def coll_player_stuff(self, player, thing):
        print 'ouch'
        self.items.extend(thing.get_actions(player))

    def update(self, gdt, gt, dt, t, *args, **kwargs):
        self.update_items()

    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        if not self.visible:
            return
        # align to player
        self.position = Vec3(self.player.position.x+10, self.player.position.y +10)

        # setup sprite for menu
        self.spr.image = pygame.Surface((100, 100))
        self.spr.image.fill((255, 0,0))

        # draw menu title
        font = pygame.font.Font(None,25)
        text = font.render("Actions",1,(255,255,255,0))
        self.spr.image.blit(text,(0,0))

        # draw menu items
        font = pygame.font.Font(None,20)
        y = 15
        for item, _ in self.items:
            text = font.render(item,1,(255,255,255,0))
            self.spr.image.blit(text,(0,y))
            y += 10

        # actually render
        Entity.render(self, screen_surf)
