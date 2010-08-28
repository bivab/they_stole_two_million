import pygame
from pygame.locals import *

import pyknic

from pyknic.collision import AABBCollisionStrategy
from pyknic.entity import Entity
from pyknic.entity import Spr
from pyknic.geometry import Vec3

from random import randint
class InteractiveDelegate(object):
    image_files = {}

    def __init__(self, properties, rect, entity, game_state):
        self.properties = properties
        self.rect = rect
        self.color = (255, 100, 0)
        self.timer = None
        self.entity = entity
        self.game_state = game_state
        self.smash_cost = 5
        self.rotation = 0
        self.setup()
        self.load_images()
        if not hasattr(self, 'state'):
            self.state = 'default'

    def load_images(self):
        self.images = dict([(k,pygame.transform.rotate(
                            pygame.image.load(v).convert_alpha(),
                            self.rotation)) for k,v in self.image_files.iteritems()])

    def setup(self):
        if 'rotation' in self.properties:
            try:
                self.rotation = int(self.properties['rotation'])
            except ValueError, e:
                pass

    def label(self):
        return 'A Thing'

    def make_action(self, callback, timer):
        if self.timer:
            return lambda *args:()
        def func(player):
            self.timer = True
            def f(*args):
                self.timer = None
                callback(player)
                player.unfreeze()
            self.game_state.game_time.schedule(timer, f, player)
            player.freeze()
        return func

    def update(self, *args, **kwargs):
        pass

    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        f = self.images.get(self.state, self.images['default'])
        image = pygame.transform.scale(f, (self.rect.width, self.rect.height))
        screen_surf.blit(image, (self.rect.x - offset.x, self.rect.y - offset.y))

class Door(InteractiveDelegate):
    image_files = {
            "default" : 'data/images/door_opened.png',
            "closed" : 'data/images/door_closed.png',
            "locked" : 'data/images/door_closed.png'}

    def __init__(self, *args):
        InteractiveDelegate.__init__(self, *args)
        self.lockpick_time = 6
        self.open_time = 1
        self.close_time = 1
        self.smash_time = 3
        if self.state == 'default':
            self.state = "locked"

    def label(self):
        return 'Door'

    def setup(self):
        InteractiveDelegate.setup(self)
        if 'locked' in self.properties:
            if not self.properties['locked'] == 'true':
                self.state = 'closed'
        else:
            if 'closed' in self.properties and \
                    self.properties['closed'] == 'true':
                self.state = 'closed'
            else:
                self.state = 'locked'

    def get_actions(self, player):
        actions = []
        if self.state == 'smashed':
            return actions

        if self.state == 'locked':
            actions.append(('Lockpick (%ss)' % self.lockpick_time,
                                    self.make_action(self.lockpick, self.lockpick_time)))
        elif self.state == 'closed':
            actions.append(('Open (%ss)' % self.open_time, self.make_action(self.open, self.open_time)))
        elif self.state == 'opened':
            actions.append(('Close (%ss)' % self.close_time,
                                    self.make_action(self.close, self.close_time)))
        if self.state != 'smashed' and player.energy >= self.smash_cost:
            actions.append(('Smash (%ss)' % (self.smash_time),
                                    self.make_action(self.smash, self.smash_time)))
        return actions

    def open(self, player):
        if self.state != 'locked':
            self.entity.make_passable()
            self.state = "opened"

    def lockpick(self, player):
        self.state = 'closed'

    def smash(self, player):
        self.state = 'smashed'
        player.energy -= self.smash_cost
        self.entity.make_passable()

    def close(self, player):
        self.entity.make_impassable()
        self.state = "closed"

class Desk(InteractiveDelegate):
    image_files = {"robbed" : 'data/images/desk01.png',"default" : 'data/images/desk01_money.png'}
    states = ['closed', 'opened', 'smashed', 'locked']

    def __init__(self, properties, rect, *args):
        InteractiveDelegate.__init__(self, properties, rect, *args)
        if self.state not in self.states:
            self.state = "locked"
        self.lockpick_time = 10
        self.smash_time = 1
        self.open_time = 1
        self.close_time = 3
        self.rob_time = 5


    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        image.fill(self.color)
        if self.value > 0:
            f = self.images['default']
        else:
            f = self.images['robbed']
        img = pygame.transform.scale(f, image.get_size())
        image.blit(img, (0,0))
        screen_surf.blit(image, (self.rect.x - offset.x, self.rect.y - offset.y))

    def label(self):
        return 'Desk'

    def setup(self):
        InteractiveDelegate.setup(self)
        for key, value in self.properties.items():
            if key == 'rob':
                self.value = int(value)
            elif key == 'locked':
                if value == 'false':
                    self.state = 'closed'
                else:
                    self.state = 'locked'
            elif key == 'lockpick_time':
                self.unlock_time = int(value)
            elif key == 'smash_time':
                self.smash_time = int(value)
            else:
                pass

    def get_actions(self, player):
        actions = []
        if self.state != 'smashed':
            if player.energy >= self.smash_cost:
                actions.append(('Smash (%ss)' % self.smash_time,
                                            self.make_action(self.smash, self.smash_time)))
            if self.state == 'locked':
                actions.append(('Lockpick (%ss)' % self.lockpick_time,
                                            self.make_action(self.lockpick, self.lockpick_time)))
            if self.state == 'closed':
                actions.append(('Open (%ss)' % self.open_time,
                                            self.make_action(self.open, self.open_time)))
            if self.state == 'opened':
                actions.append(('Close (%ss)' % self.close_time,
                                            self.make_action(self.close, self.close_time)))
        if self.value > 0 and self.state in ['smashed', 'opened']:
            actions.append(('Rob (%ss)' % self.rob_time,
                                            self.make_action(self.rob, self.rob_time)))
        return actions

    def open(self, player):
        self.state = 'opened'
        self.color = (0, 255, 0)

    def close(self, player):
        self.state = 'closed'
        self.color = (255, 100, 0)

    def lockpick(self, player):
        self.state = 'closed'
        self.color = (123,0, 122)

    def smash(self, player):
        if self.state == 'smashed':
            print 'It is already smashed'
            return
        self.state = 'smashed'
        player.energy -= self.smash_cost
        self.color = (0, 55, 100)

    def rob(self, player):
        assert self.state in ['smashed', 'opened']
        player.add_money(self.value)
        self.value = 0
        self.color = (255, 100, 0)

class Car(InteractiveDelegate):
    image_files = {'default':'data/images/car.png'}

    def __init__(self, *args):
        InteractiveDelegate.__init__(self, *args)
        self.escape_time = 5

    def get_actions(self, player):
        return [('Escape (%ss)' % self.escape_time,
                                self.make_action(self.escape, self.escape_time))]

    def escape(self, player):
        self.entity.state.game_won()

    def label(self):
        return 'Car'

class Safe(InteractiveDelegate):
    image_files = { "default" : 'data/images/safe_closed.png',
                    "opened_money":'data/images/safe_opened_money.png',
                    "opened":'data/images/safe_opened.png',
                    }
    states = ['closed', 'opened', 'smashed', 'locked']

    def __init__(self, properties, rect, *args):
        self.lockpick_time = 15
        self.smash_time = 10
        self.open_time = 5
        self.close_time = 5
        self.rob_time = 5
        self.value = 1000
        InteractiveDelegate.__init__(self, properties, rect, *args)
        self.state = "locked"


    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        if self.state == 'opened':
            if self.value <= 0:
                f = self.images['opened']
            else:
                f = self.images['opened_money']
        else:
            f = self.images['default']
        img = pygame.transform.scale(f, image.get_size())
        image.blit(img, (0,0))
        screen_surf.blit(image, (self.rect.x - offset.x, self.rect.y - offset.y))

    def label(self):
        return 'Safe'

    def setup(self):
        InteractiveDelegate.setup(self)
        for key, value in self.properties.items():
            if key == 'rob':
                self.value = int(value)
            elif key == 'locked':
                if value == 'false':
                    self.state = 'closed'
                else:
                    self.state = 'locked'
            elif key == 'lockpick_time':
                self.unlock_time = int(value)
            elif key == 'smash_time':
                self.smash_time = int(value)
            else:
                pass

    def get_actions(self, player):
        actions = []
        if self.state != 'smashed':
            if player.energy >= self.smash_cost:
                actions.append(('Smash (%ss)' % self.smash_time,
                                            self.make_action(self.smash, self.smash_time)))
            if self.state == 'locked':
                actions.append(('Lockpick (%ss)' % self.lockpick_time,
                                            self.make_action(self.lockpick, self.lockpick_time)))
            if self.state == 'closed':
                actions.append(('Open (%ss)' % self.open_time,
                                            self.make_action(self.open, self.open_time)))
            if self.state == 'opened':
                actions.append(('Close (%ss)' % self.close_time,
                                            self.make_action(self.close, self.close_time)))
        if self.value > 0 and self.state in ['smashed', 'opened']:
            actions.append(('Rob (%ss)' % self.rob_time, self.make_action(self.rob, self.rob_time)))
        return actions

    def open(self, player):
        self.state = 'opened'

    def close(self, player):
        self.state = 'closed'

    def lockpick(self, player):
        self.state = 'closed'

    def smash(self, player):
        if self.state == 'smashed':
            print 'It is already smashed'
            return
        self.state = 'smashed'
        player.energy -= self.smash_cost

    def rob(self, player):
        assert self.state in ['smashed', 'opened']
        player.add_money(self.value)
        self.value = 0

class Showcase(InteractiveDelegate):
    image_files = {"smashed" : 'data/images/showcase_smashed.png',"default" :
    'data/images/showcase.png'}
    states = ['closed', 'smashed']

    def __init__(self, properties, rect, *args):
        self.state = "closed"
        self.smash_time = 3
        self.rob_time = 2
        self.value = 100
        InteractiveDelegate.__init__(self, properties, rect, *args)

    def setup(self):
        InteractiveDelegate.setup(self)
        if 'rob' in self.properties:
            self.value = int(self.properties['rob'])

    def get_actions(self, player):
        actions = []
        if self.state != 'smashed':
            actions.append(('Smash (%ss)' % self.smash_time,
                                    self.make_action(self.smash, self.smash_time)))
        else:
            if self.value > 0:
                actions.append(('Rob (%ss)' % self.rob_time,
                                    self.make_action(self.rob, self.rob_time)))
        return actions

    def label(self):
        return 'Showcase'

    def smash(self, player):
        self.state = 'smashed'
        player.energy -= self.smash_cost

    def rob(self, player):
        assert state == 'smashed'
        player.add_money(self.value)
        self.value = 0

class Dispenser(InteractiveDelegate):
    image_files = {'default': 'data/images/water_dispender01.png'}

    def __init__(self, properties, rect, *args):
        self.state = 'filled'
        self.smash_time = 5
        self.drink_time = 2
        self.fill = 20
        self.cost = 1
        self.cup_size = 10

        InteractiveDelegate.__init__(self, properties, rect, *args)


    def label(self):
        return 'Dispenser'

    def setup(self):
        if 'fill' in self.properties:
            self.fill = int(self.properties['fill'])
        if 'cost' in self.properties:
            self.fill = int(self.properties['cost'])

    def get_actions(self, player):
        actions = []
        if self.state == 'smashed':
            return actions

        if self.state == 'filled' and self.fill >= self.cup_size and player.money >= self.cost:
            actions.append(('Drink (%ss)' % self.drink_time, self.make_action(self.drink, self.drink_time)))
        actions.append(('Smash (%ss)' % self.smash_time, self.make_action(self.smash, self.smash_time)))
        return actions

    def drink(self, player):
        self.fill -= self.cup_size
        player.money -= self.cost
        player.energy += self.cup_size

    def smash(self, player):
        self.state = 'smashed'
        player.energy -= self.smash_cost

class Window(Door):
    image_files = {
            "default" : 'data/images/window1.png',
            "opened" : 'data/images/window1_open.png',
            "smashed" : 'data/images/window1_open.png'}

    def label(self):
        return 'Window'
