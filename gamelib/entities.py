# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *

import pyknic

from pyknic.collision import AABBCollisionStrategy
from pyknic.entity import Entity
from pyknic.entity import Spr
from pyknic.geometry import Vec3

from random import randint

class InteractiveThing(pyknic.entity.Entity):
    @staticmethod
    def build_from_object(obj, state):
        thing = InteractiveThing(Rect(obj.x, obj.y, obj.width, obj.height), state)
        thing.properties = obj.properties
        thing.thing_type = obj.type
        state.actionables.append(thing.blow_up())
        state.impassables.append(thing)
        state.game_time.event_update += thing.update
        return thing

    def __init__(self, rect, state):
        Entity.__init__(self, None, Vec3(rect.x, rect.y))
        self.rect.size = (rect.w, rect.h)
        self.properties = {}
        self.thing = None
        self.layer = 100
        self.thing_type = None
        self.state = state
        self.impassables = state.impassables

    def get_actions(self, player):
        t = self.get_thing()
        return t.get_actions(player)

    def get_thing(self):
        if not self.thing:
            try:
                import gamelib
                klass = getattr(gamelib.entities, self.thing_type)
                self.thing = klass(self.properties, self.rect, self)
            except Exception, e:
               print 'Unknown type %s' % self.thing_type

        return self.thing

    def label(self):
        return self.thing.label()

    def blow_up(self):
        rect = Rect(self.rect.x-15, self.rect.y-15,self.rect.width+30, self.rect.height+30)
        t = InteractiveThing(rect, self.state)
        t.properties = self.properties
        t.thing_type = self.thing_type
        t.thing = self
        return t

    def update(self, *args, **kwargs):
        t = self.get_thing()
        t.update(args, kwargs)

    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        t = self.get_thing()
        t.render(screen_surf, offset, screen_offset)

    def make_impassable(self):
        self.impassables.append(self)

    def make_passable(self):
        if self in self.impassables:
            self.impassables.remove(self)


class InteractiveDelegate(object):
    image_files = {}

    def __init__(self, properties, rect, entity = None):
        self.properties = properties
        self.rect = rect
        self.color = (255, 100, 0)
        self.timer = None
        self.entity = entity
        self.smash_cost = 10
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
            self.timer = [timer, callback, player]
            player.freeze()
        return func

    def update(self, *args, **kwargs):
        if self.timer:
            if self.timer[0] == 0 :
                self.timer[1](self.timer[2])
                self.timer[2].unfreeze()
                self.timer = None
            else:
                self.timer[0] -= 1

    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        f = self.images.get(self.state, self.images['default'])
        image = pygame.transform.scale(f, f.get_size())
        screen_surf.blit(image, (self.rect.x - offset.x, self.rect.y - offset.y))

class Door(InteractiveDelegate):
    image_files = {
            "default" : 'data/images/door_opened.png',
            "closed" : 'data/images/door_closed.png',
            "locked" : 'data/images/door_closed.png'}

    def __init__(self, properties, rect, entity):
        InteractiveDelegate.__init__(self, properties, rect, entity)
        self.lockpick_time = 50
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
            actions.append(('Lockpick', self.make_action(self.lockpick, self.lockpick_time)))
        elif self.state == 'closed':
            actions.append(('Open', self.make_action(self.open, 1)))
        elif self.state == 'opened':
            actions.append(('Close', self.make_action(self.close, 1)))
        if self.state != 'smased' and player.energy >= self.smash_cost:
            actions.append(('Smash', self.make_action(self.smash, 10)))
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
        InteractiveDelegate.__init__(self, properties, rect)
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
                print 'Unknown key %s, %s' % (key, value)

    def get_actions(self, player):
        actions = []
        if self.state != 'smashed':
            if player.energy >= self.smash_cost:
                actions.append(('Smash', self.make_action(self.smash, self.smash_time)))
            if self.state == 'locked':
                actions.append(('Lockpick', self.make_action(self.lockpick, self.lockpick_time)))
            if self.state == 'closed':
                actions.append(('Open', self.make_action(self.open, self.open_time)))
            if self.state == 'opened':
                actions.append(('Close', self.make_action(self.close, self.close_time)))
        if self.value > 0 and self.state in ['smashed', 'opened']:
            actions.append(('Rob', self.make_action(self.rob, self.rob_time)))
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

    def get_actions(self, player):
        return [('Escape', self.make_action(self.escape, 5))]

    def escape(self, player):
        self.entity.state.game_won()


class Enlightened(pyknic.entity.Entity):
    def __init__(self, position, state):
        super(Enlightened, self).__init__(None, position)
        self.state = state
        self.layer = 10000
        self.moving = Vec3(0,0)
        self.coll_detector = pyknic.collision.CollisionDetector()
        self.state.game_time.event_update += self.update

    def update(self, gdt, gt, dt, t, *args, **kwargs):
        if self.target:
            self.position = self.target.position
            self.rect.center = self.position.as_xy_tuple()
        else:
            self.update_x(gdt, gt, dt, t, *args)
            self.coll_detector.check()
            self.update_y(gdt, gt, dt, t, *args)
            self.coll_detector.check()

    def collides_with(self, other_name, others, callback, other_class=Entity):
        my_name = self.__class__.__name__.lower()

        self.coll_detector.register_once(my_name, other_name, [self], others, \
                    AABBCollisionStrategy(), (self.__class__, other_class), callback)

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

    @staticmethod
    def factory(objekt, state):
        pos = Vec3(objekt.x, objekt.y)

        if objekt.type == 'Player':
            return Player(pos, state)
        elif objekt.type == 'Guard':
            return Guard(pos, state)
        elif objekt.type == 'LurkingGuard':
            return LurkingGuard(pos, state)
        elif objekt.type == 'PatrollingGuard':
            direction = objekt.properties['direction']
            return PatrollingGuard(pos, state, direction)


class Player(Enlightened):
    def __init__(self, position, state):
        super(Player, self).__init__(position, state)
        self.money = 0
        self.energy = 50

        anims = pyknic.animation.load_animation(self.state.game_time, 'data/myanim')

        self.sprites = {}
        self.sprites[pyknic.utilities.utilities.Direction.N] = anims['up']
        self.sprites[pyknic.utilities.utilities.Direction.S] = anims['down']
        self.sprites[pyknic.utilities.utilities.Direction.E] = anims['right']
        self.sprites[pyknic.utilities.utilities.Direction.W] = anims['left']
        self.spr = self.sprites[pyknic.utilities.utilities.Direction.N]
        self.rect.size = self.spr.image.get_size()

        self.collides_with('walls', self.state.impassables, self.coll_player_wall)

        self.state.events.key_down += self.on_key_down
        self.state.events.key_up += self.on_key_up

        self.light = self.state.lighting.create_light(self, False, (300,300))

        action_menu = ActionMenu(self.state.the_app.screen, self, self.state.actionables)
        self.state.game_time.event_update += action_menu.update
        self.state.events.key_down += action_menu.on_key_down
        self.state.world.add_entity(action_menu)
        self.frozen = False

    def freeze(self):
        self.frozen = True

    def unfreeze(self):
        self.frozen = False

    def coll_player_wall(self, player, wall):
        assert player is self
        player.collision_response(wall)

    def add_money(self, amount):
        self.money += amount
        print 'Wuhooo, I\'m rich %d' % self.money

    def update(self, gdt, gt, dt, t, *args, **kwargs):
        super(Player, self).update(gdt, gt, dt, t, *args, **kwargs)

        if self.velocity.lengthSQ:
            self.spr.play()
            dir = pyknic.utilities.utilities.get_4dir(self.velocity.angle)
            self.spr = self.sprites[dir]
        else:
            self.spr.pause()

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
        if self.frozen:
            self.velocity = Vec3(0,0)
            return

        speed = 180

        if key == K_UP:
            self.velocity.y = -speed
            #self.state.fog.set_offset(self, Vec3(0,-75))
        if key == K_DOWN:
            self.velocity.y = speed
            #self.state.fog.set_offset(self, Vec3(0,75))
        if key == K_LEFT:
            self.velocity.x = -speed
            #self.state.fog.set_offset(self, Vec3(-75,0))
        if key == K_RIGHT:
            self.velocity.x = speed
            #self.state.fog.set_offset(self, Vec3(75,0))
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
        self.names = []

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
            self.names = []
            # update menu
            self.actionable_detector.check()
        if not self.items:
            self.visible = False


    def coll_player_stuff(self, player, thing):
        a = thing.get_actions(player)
        self.names.extend([thing.label()] * len(a))
        self.items.extend(a)

    def update(self, gdt, gt, dt, t, *args, **kwargs):
        self.update_items()

    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        item_height = 10
        name_height = 15
        min_width = 90
        if not self.visible:
            return
        # align to player
        self.position = Vec3(self.player.position.x+10, self.player.position.y +10)

        # setup sprite for menu
        height = 50 + len(self.items) * item_height + \
                len(set(self.names)) * name_height
        i_width = 20 + reduce(max, [len(i) for i in self.items]) * item_height
        n_width = 20 + reduce(max, [len(i) for i in self.names])  * name_height
        width = max(i_width, n_width, min_width)

        self.spr.image = pygame.Surface((width, height))
        self.spr.image.set_alpha(200)
        self.spr.image.fill((255, 0,0))

        # draw menu title
        font = pygame.font.Font(None,25)
        text = font.render("Actions",1,(255,255,255,0))
        self.spr.image.blit(text,(10,10))

        # draw menu items
        fonta = pygame.font.Font(None,20)
        fontb = pygame.font.Font(None,15)
        y = 35
        label_text = ''
        for i in range(len(self.items)):
            item, _ = self.items[i]
            if self.names[i] != label_text:
                label_text = self.names[i]
                label = fonta.render(label_text, 1, (255,255,255))
                self.spr.image.blit(label,(10,y))
                y += name_height
            text = fontb.render("%d: %s" % (i+1, item),1,(255,255,255,0))
            self.spr.image.blit(text,(10,y))
            y += item_height

        # actually render
        Entity.render(self, screen_surf, offset)

class Guard(Enlightened):
    def __init__(self, position, state):
        super(Guard, self).__init__(position, state)

        anims = pyknic.animation.load_animation(self.state.game_time, 'data/copanim')

        self.sprites = {}
        self.sprites[pyknic.utilities.utilities.Direction.N] = anims['up']
        self.sprites[pyknic.utilities.utilities.Direction.S] = anims['down']
        self.sprites[pyknic.utilities.utilities.Direction.E] = anims['right']
        self.sprites[pyknic.utilities.utilities.Direction.W] = anims['left']
        self.spr = self.sprites[pyknic.utilities.utilities.Direction.N]
        self.rect.size = self.spr.image.get_size()

        self.switch_random_direction()
        self.steps_made = 0

        self.collides_with('walls', [self.state.player]+self.state.impassables, self.collidate_wall)
        self.light = self.state.lighting.create_light(self, True, (100,100))

    def switch_random_direction(self, wrong_direction=0):
        import random
        direction = int(random.random()*4)
        if direction==0:
            self.velocity.x = 40
        elif direction==1:
            self.velocity.x = -40
        elif direction==2:
            self.velocity.y = 40
        elif direction==3:
            self.velocity.y = -40
        # if the chosen direction was the old one
        # move back
        if wrong_direction == direction:
            self.velocity.y *= -1
            self.velocity.x *= -1

    def collision_response(self, other):
        if not self.rect.colliderect(other.rect):
            return

        # smashing into wall from left
        if self.moving.x > 0 and self.rect.right > other.rect.left:
            self.rect.right = other.rect.left
            self.switch_random_direction(0)

        # smashing into wall from right
        if self.moving.x < 0 and self.rect.left < other.rect.right:
            self.rect.left = other.rect.right
            self.switch_random_direction(1)

        # smashing into wall from above
        if self.moving.y > 0 and self.rect.bottom > other.rect.top:
            self.rect.bottom = other.rect.top
            self.switch_random_direction(2)

        # smashing into wall from below
        if self.moving.y < 0 and self.rect.top < other.rect.bottom:
            self.rect.top = other.rect.bottom
            self.switch_random_direction(3)

        self.moving = Vec3(0,0)
        self.position = Vec3(*self.rect.center)

    def collidate_wall(self, player, wall, dummy = 0):
        self.collision_response(wall)

    def update(self, gdt, gt, dt, t, *args, **kwargs):
        super(Guard, self).update(gdt, gt, dt, t, *args, **kwargs)

        self.steps_made = self.steps_made + 1
        if self.steps_made == 40:
            self.switch_random_direction()
            self.steps_made = 0

        if self.velocity.lengthSQ:
            self.spr.play()
            dir = pyknic.utilities.utilities.get_4dir(self.velocity.angle)
            self.spr = self.sprites[dir]
        else:
            self.spr.pause()

class Lighting(object):
    def __init__(self):
        self._lights = []
        self.layer = 999999
        self.position =Vec3(0,0,0)

    def create_light(self, obj, enabled, size, offset=Vec3(0,0)):
        light = Light(obj)
        light.enabled = enabled
        light.size = size
        light.offset = offset

        self._lights.append(light)
        return light


    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        fog = pygame.Surface(screen_surf.get_rect().size, pygame.SRCALPHA)
        fog.fill((0,0,0,150))

        for light in self._lights:
            light.render(fog, offset)

        screen_surf.blit(fog, (0,0))

class Light(object):
    def __init__(self, entity = None):
        self.attached = entity
        self.enabled = True
        self.size = (200,200)
        self.offset = Vec3(0,0)
        self._light_image = pygame.image.load("data/images/player_light.png").convert_alpha()

    def img(self):
        return pygame.transform.scale(self._light_image, self.size)

    def sprite_offset(self):
        return Vec3((self.size[0]/2), (self.size[1]/2))

    def position(self):
        return self.attached.position - self.sprite_offset() + self.offset

    def render(self, surface, offset):
        surface.blit(self.img(), (self.position() - offset).as_xy_tuple(), None, pygame.BLEND_RGBA_SUB)

class LurkingGuard(Enlightened):
    def __init__(self, position, state):
        super(LurkingGuard, self).__init__(position, state)

        anims = pyknic.animation.load_animation(self.state.game_time, 'data/copanim')

        self.sprites = {}
        self.sprites[pyknic.utilities.utilities.Direction.N] = anims['up']
        self.sprites[pyknic.utilities.utilities.Direction.S] = anims['down']
        self.sprites[pyknic.utilities.utilities.Direction.E] = anims['right']
        self.sprites[pyknic.utilities.utilities.Direction.W] = anims['left']
        self.spr = self.sprites[pyknic.utilities.utilities.Direction.N]
        self.rect.size = self.spr.image.get_size()

        self.world = self.state.world
        self.impassables = self.state.impassables
        self.steps_made = 0
        self.random_move = False
        self.find_direction()

        self.collides_with('walls', self.state.impassables, self.collidate_wall)
        self.collides_with('player', [self.state.player], self.collidate_player, Player)

        self.light = self.state.lighting.create_light(self, True, (150,150))

    def update(self, gdt, gt, dt, t, *args, **kwargs):
        self.steps_made = self.steps_made + 1
        if self.steps_made == [64, 128][self.random_move]:
            self.find_direction()
            self.steps_made = 0

        super(LurkingGuard, self).update(gdt, gt, dt, t, *args, **kwargs)

    def find_direction(self):
        max_speed = 50.0
        pos_x = self.position.x
        pos_y = self.position.y
        lurk_rect = pygame.Rect(pos_x - 75, pos_y - 75, 150, 150)
        entities = self.world.get_entities_in_region(lurk_rect)
        found_player = None
        for e in entities:
            if isinstance(e, Player):
                found_player = e
        if found_player:
            self.random_move = False
            p_pos_x = found_player.position.x
            p_pos_y = found_player.position.y
            if p_pos_x<pos_x:
                left = p_pos_x
                width = pos_x-p_pos_x
            else:
                left = pos_x
                width = p_pos_x-pos_x
            if p_pos_y<pos_y:
                top = p_pos_y
                height = pos_y-p_pos_y
            else:
                top = pos_y
                height = p_pos_y-pos_y
            check_rect = pygame.Rect(left, top, width, height)
            e_collision=False
            for e in entities:
                if not isinstance(e, (Player, Guard, LurkingGuard)):
                    if check_rect.colliderect(e.rect) and e in self.impassables:
                            e_collision=True
            v_x = p_pos_x-pos_x
            v_y = p_pos_y-pos_y
            if v_x>max_speed or v_y>max_speed:
                if v_x>v_y:
                    scale = v_x/max_speed
                else:
                    scale = v_y/max_speed
                v_x = v_x/scale
                v_y = v_y/scale
            if not e_collision:
                self.velocity.x = v_x
                self.velocity.y = v_y
            else:
                if v_x>v_y:
                    self.velocity.x = v_x
                    self.velocity.y = 0
                else:
                    self.velocity.x = 0
                    self.velocity.y = v_y
        else:
            self.random_move = True
            self.velocity.x = randint(-max_speed,max_speed)
            self.velocity.y = randint(-max_speed,max_speed)

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

        self.find_direction()

    def collidate_wall(self, player, wall, dummy = 0):
        self.collision_response(wall)

    def collidate_player(self, player, wall, dummy = 0):
        self.state.game_over()

class PatrollingGuard(Enlightened):
    def __init__(self, position, state, direction):
        super(PatrollingGuard, self).__init__(position, state)

        # animation
        anims = pyknic.animation.load_animation(self.state.game_time, 'data/copanim')
        self.sprites = {}
        self.sprites[pyknic.utilities.utilities.Direction.N] = anims['up']
        self.sprites[pyknic.utilities.utilities.Direction.S] = anims['down']
        self.sprites[pyknic.utilities.utilities.Direction.E] = anims['right']
        self.sprites[pyknic.utilities.utilities.Direction.W] = anims['left']
        self.spr = self.sprites[pyknic.utilities.utilities.Direction.N]

        self.rect.size = self.spr.image.get_size()

        # some values
        self.world = self.state.world
        self.impassables = self.state.impassables
        self.steps_made = 0
        self.random_move = False
        self.at_home = True                                 # on patrolling route?
        self.speed = 30                                     # speed
        self.start_position = Vec3(position.x, position.y)  # save start vector
        self.direction = direction
        if self.direction == 'horizontal':
            self.normal_velocity = Vec3(self.speed, 0)
        else: # vertical
            self.normal_velocity = Vec3(0, self.speed)
        self.velocity = self.normal_velocity                # initial velocity

        self.collides_with('walls', self.state.impassables, self.collidate_wall)
        self.collides_with('player', [self.state.player], self.collidate_player, Player)

        self.light = self.state.lighting.create_light(self, True, (200,200))

    def update(self, gdt, gt, dt, t, *args, **kwargs):

        ## update fog (depending on direction the guard is looking)
        fog_offset = 50
        fog_width = self.light.size[0]/2 #self.state.fog.get(self)[1][0]/2
        m = max(abs(self.velocity.x), abs(self.velocity.y))
        if m != 0:
            fog_dir = self.velocity / m * fog_offset
            self.light.offset = fog_dir
        else:
            fog_dir = self.position

        # set the view of the guard = the position of the fog
        watch_x = self.position.x + fog_dir.x - fog_width/2 # position + offset - width(needed to get the center)
        watch_y = self.position.y + fog_dir.y - fog_width/2
        watch_rect = pygame.Rect(watch_x, watch_y, fog_width, fog_width)
        entities = self.world.get_entities_in_region(watch_rect)
        found_player = None
        for e in entities:
            if isinstance(e, Player):
                found_player = e

        if found_player:
            # increase speed, follow player
            direction_vec = found_player.position - self.position
            # velocity = normalized(vector_to_player) * speed (double it to make him run a bit faster)
            self.velocity = direction_vec / max(abs(direction_vec.x), abs(direction_vec.y)) * self.speed * 2
            self.at_home = False

        # if you left the patrolling route(horizontal=y-axis, vertical=x-axis), head back for patrolling route
        elif self.direction == 'horizontal' and round(self.position.y) != round(self.start_position.y):
            # decrease speed, go back to patrolling point
            direction_vec = self.start_position - self.position
            self.velocity = direction_vec / max(abs(direction_vec.x), abs(direction_vec.y)) * self.speed

        elif self.direction == 'vertical' and round(self.position.x) != round(self.start_position.x):
            # decrease speed, go back to patrolling point
            direction_vec = self.start_position - self.position
            self.velocity = direction_vec / max(abs(direction_vec.x), abs(direction_vec.y)) * self.speed

        elif not self.at_home:
            self.velocity = self.normal_velocity
            self.at_home = True

        # animate
        if self.velocity.lengthSQ:
            self.spr.play()
            dir = pyknic.utilities.utilities.get_4dir(self.velocity.angle)
            self.spr = self.sprites[dir]
        else:
            self.spr.pause()

        super(PatrollingGuard, self).update(gdt, gt, dt, t, *args, **kwargs)

    def collision_response(self, other):
        if not self.rect.colliderect(other.rect):
            return

        # smashing into wall from left
        if self.moving.x > 0 and self.rect.right > other.rect.left:
            self.rect.right = other.rect.left
            self.velocity = Vec3(-self.speed,0)

        # smashing into wall from right
        if self.moving.x < 0 and self.rect.left < other.rect.right:
            self.rect.left = other.rect.right
            self.velocity = Vec3(self.speed,0)

        # smashing into wall from above
        if self.moving.y > 0 and self.rect.bottom > other.rect.top:
            self.rect.bottom = other.rect.top
            self.velocity = Vec3(0, -self.speed)

        # smashing into wall from below
        if self.moving.y < 0 and self.rect.top < other.rect.bottom:
            self.rect.top = other.rect.bottom
            self.velocity = Vec3(0, self.speed)

        self.moving = Vec3(0,0)
        self.position = Vec3(*self.rect.center)

    def collidate_wall(self, player, wall, dummy = 0):
        self.collision_response(wall)

    def collidate_player(self, player, wall, dummy = 0):
        self.state.game_over()
