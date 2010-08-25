import pygame
from pygame.locals import *

import pyknic

from pyknic.collision import AABBCollisionStrategy
from pyknic.entity import Entity
from pyknic.entity import Spr
from pyknic.geometry import Vec3
from pyknic.geometry import Vec3

class InteractiveThing(pyknic.entity.Entity):
    def __init__(self, x, y, width, height, properties, thing_type, impassables):
        Entity.__init__(self, None, Vec3(x, y))
        self.rect.size = (width, height)
        self.layer =  1
        self.properties = properties
        self.thing = None
        self.layer = 100
        self.thing_type = thing_type
        self.impassables = impassables

    def get_actions(self, player):
        t = self.get_thing()
        return t.get_actions(player)

    def get_thing(self):
        if not self.thing:
            if self.thing_type == 'Desk':
                self.thing = Desk(self.properties, self.rect)
            elif self.thing_type == 'Door':
                self.thing = Door(self.properties, self.rect, self)

        # if not self.thing:
        # self.thing = globals()[self.thing_type](self.properties, self.rect)
        return self.thing

    def blow_up(self):
        t = InteractiveThing(self.rect.x-15, self.rect.y-15, \
                            self.rect.width+30, self.rect.height+30, \
                            self.properties, self.thing_type, self.impassables)
        t.thing = self
        return t


    def update(self, *args, **kwargs):
        self.thing.update(args, kwargs)

    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        t = self.get_thing()
        t.render(screen_surf, offset, screen_offset)

    def make_impassable(self):
        self.impassables.append(self)

    def make_passable(self):
        if self in self.impassables:
            self.impassables.remove(self)


class InteractiveDelegate(object):
    def __init__(self, properties, rect, entity = None):
        self.properties = properties
        self.rect = rect
        self.color = (255, 100, 0)
        self.timer = None
        self.entity = entity
        self.smashed = False
        self.setup()

    def setup(self):
        xxx

    def make_action(self, callback, timer):
        def func(player):
            self.timer = [timer, callback, [player]]
        return func

    def update(self, *args, **kwargs):
        if self.timer:
            if self.timer[0] == 0 :
                self.timer[1](*self.timer[2])
                self.timer = None
            else:
                self.timer[0] -= 1

    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        image = pygame.Surface((self.rect.width, self.rect.height))
        image.fill(self.color)

        screen_surf.blit(image, (self.rect.x, self.rect.y))

class Door(InteractiveDelegate):
    def __init__(self, properties, rect, entity):
        InteractiveDelegate.__init__(self, properties, rect, entity)
        self.lockpick_time = 50
        self.smashed = False
        self.default_color = (123,123,123)
        self.color = self.default_color

    def setup(self):
        if 'locked' in self.properties:
            self.locked = self.properties['locked'] == True
            self.closed = True
        else:
            self.locked = True
            if 'closed' in self.properties:
                self.closed = self.properties['closed'] == True
            else:
                self.closed = True

    def get_actions(self, player):
        actions = []
        if self.smashed:
            return actions

        if self.locked:
            actions.append(('Lockpick', self.make_action(self.lockpick, self.lockpick_time)))
        elif self.closed:
            actions.append(('Open', self.make_action(self.open, 1)))
        elif not self.closed:
            actions.append(('Close', self.make_action(self.close, 1)))
        if not self.smashed:
            actions.append(('Smash', self.make_action(self.smash, 10)))
        return actions

    def open(self, player):
        if not self.locked:
            self.color = (0,0,0,255)
            self.closed = False
            self.entity.make_passable()

    def lockpick(self, player):
        self.locked = False

    def smash(self, player):
        self.color = (1,1,1, 255)
        self.locked = False
        self.closed = False
        self.smashed = True
        self.entity.make_passable()

    def close(self, player):
        self.color = self.default_color
        self.closed = True
        self.entity.make_impassable()

class Desk(InteractiveDelegate):
    def __init__(self, properties, rect):
        InteractiveDelegate.__init__(self, properties, rect)
        self.lockpick_time = 1
        self.smash_time = 0
        self.closed = True

    def setup(self):
        for key, value in self.properties.items():
            if key == 'rob':
                self.value = int(value)
            elif key == 'locked' and value == 'true':
                self.locked = True
            elif key == 'lockpick_time':
                self.unlock_time = int(value)
            elif key == 'smash_time':
                self.smash_time = int(value)
            else:
                print 'Unknown key %s, %s' % (key, value)

    def get_actions(self, player):
        actions = []
        if not self.smashed:
            actions.append(('Smash', self.make_action(self.smash, self.smash_time)))
            if self.locked:
                actions.append(('Lockpick', self.make_action(self.lockpick, self.lockpick_time)))
            if self.closed and not self.locked:
                actions.append(('Open', self.make_action(self.open, 1)))
            if not self.closed:
                actions.append(('Close', self.make_action(self.close, 1)))
        if not self.closed and self.value:
            actions.append(('Rob', self.make_action(self.rob, 1)))
        return actions

    def open(self, player):
        self.closed = False
        self.color = (0, 255, 0)

    def close(self, player):
        self.closed = True
        self.color = (255, 100, 0)


    def lockpick(self, player):
        self.locked = False
        self.color = (123,0, 122)

    def smash(self, player):
        self.locked = False
        self.closed = False
        self.smashed = True
        self.color = (0, 55, 100)

    def rob(self, player):
        player.add_money(self.value)
        self.value = 0
        self.color = (255, 100, 0)


class Player(pyknic.entity.Entity):
    def __init__(self, spr=None, position=None, velocity=None, acceleration=None, coll_rect=None):
        img = pygame.Surface((16, 16))
        img.fill((255, 0, 0))
        spr = Spr(img, offset=Vec3(8,8))
        self.layer = 10000
        self.moving = Vec3(0,0)
        super(Player, self).__init__(spr, position, velocity, acceleration, coll_rect)
        self.rect.size = img.get_size()
        self.money = 0

    def add_money(self, amount):
        self.money += amount
        print 'Wuhooo, I\'m rich %d' % self.money
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
