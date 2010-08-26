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
            if self.thing_type == 'Desk':
                self.thing = Desk(self.properties, self.rect)
            elif self.thing_type == 'Door':
                self.thing = Door(self.properties, self.rect, self)

        # if not self.thing:
        # self.thing = globals()[self.thing_type](self.properties, self.rect)
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

    def label(self):
        return 'A Thing'

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

        screen_surf.blit(image, (self.rect.x - offset.x, self.rect.y - offset.y))

class Door(InteractiveDelegate):
    def __init__(self, properties, rect, entity):
        InteractiveDelegate.__init__(self, properties, rect, entity)
        self.lockpick_time = 50
        self.smashed = False
        self.default_color = (123,123,123)
        self.color = self.default_color

    def label(self):
        return 'Door'

    def setup(self):
        if 'locked' in self.properties:
            self.locked = self.properties['locked'] == 'true'
            self.closed = True
        else:
            self.locked = True
            if 'closed' in self.properties:
                self.closed = self.properties['closed'] == 'true'
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

    def label(self):
        return 'Desk'
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


class Player(Enlightened):
    def __init__(self, position, state):
        super(Player, self).__init__(position, state)
        self.money = 0

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

        self.state.fog.add(self, True, (300,300))

        action_menu = ActionMenu(self.state.the_app.screen, self, self.state.actionables)
        self.state.game_time.event_update += action_menu.update
        self.state.events.key_down += action_menu.on_key_down
        self.state.world.add_entity(action_menu)

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
        speed = 90
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
        if not self.visible:
            return
        # align to player
        self.position = Vec3(self.player.position.x+10, self.player.position.y +10)

        # setup sprite for menu
        self.spr.image = pygame.Surface((200, 100))
        self.spr.image.fill((255, 0,0))

        # draw menu title
        font = pygame.font.Font(None,25)
        text = font.render("Actions",1,(255,255,255,0))
        self.spr.image.blit(text,(0,0))

        # draw menu items
        fonta = pygame.font.Font(None,20)
        fontb = pygame.font.Font(None,15)
        y = 15
        label_text = ''
        for i in range(len(self.items)):
            item, _ = self.items[i]
            if self.names[i] != label_text:
                label_text = self.names[i]
                label = fonta.render(label_text, 1, (255,255,255))
                self.spr.image.blit(label,(0,y))
                y +=15
            text = fontb.render("%d: %s" % (i+1, item),1,(255,255,255,0))
            self.spr.image.blit(text,(0,y))
            y += 10

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
        self.state.fog.add(self, True, (100,100))

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

class Fog(pyknic.entity.Entity):
    def __init__(self):
        self.light_objects = {}

        # black surface filling the whole screen
        self.black = pygame.Surface((1024,768), pygame.SRCALPHA)
        self.black.fill((0,0,0,150))

        self.layer = 99999
        self.rect = pygame.Rect(0,0,0,0)
        self.rect.size = self.black.get_size()
        self.position = Vec3(0,0)

        # surface of the spotlight
        self.spot = pygame.Surface((200,200), pygame.SRCALPHA)
        self.spot.fill((0,0,0,255))

        # image for the spotlight
        spot_png = pygame.image.load("data/images/player_light.png")
        self.spot.blit(spot_png, (0,0), None, pygame.BLEND_RGBA_SUB)

    def add(self, object, state, size):
        # object = entity, state = boolean, size = (widht, height)
        self.light_objects[object] = (state, size)

    def remove(self, object):
        self.light_objects.pop(object)

    def set_state(self, object, state):
        self.light_objects[object][0] = state

    def render(self, screen_surf, offset=Vec3(0,0), screen_offset=Vec3(0,0)):
        fog = self.black.copy()
        for obj in self.light_objects.keys():

            if self.light_objects[obj][0] is True:
                # resize spotlight
                resized_spot = pygame.transform.scale(self.spot, self.light_objects[obj][1])

                # calculate position
                spot_x = obj.position.x - resized_spot.get_width()/2
                spot_y = obj.position.y - resized_spot.get_height()/2

                # place lights dependant on the world offset
                fog.blit(resized_spot, (spot_x - offset.x ,spot_y - offset.y), None, pygame.BLEND_RGBA_MIN)
        
        # when all lights are added, draw fog
        screen_surf.blit(fog, (self.rect.x, self.rect.y)) # the black surface is always drawn in (0,0)

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

        self.state.fog.add(self, True, (100,100))

    def update(self, gdt, gt, dt, t, *args, **kwargs):
        super(LurkingGuard, self).update(gdt, gt, dt, t, *args, **kwargs)
        
        self.steps_made = self.steps_made + 1
        if self.steps_made == [64, 128][self.random_move]:
            self.find_direction()
            self.steps_made = 0

        if self.velocity.lengthSQ:
            self.spr.play()
            dir = pyknic.utilities.utilities.get_4dir(self.velocity.angle)
            self.spr = self.sprites[dir]
        else:
            self.spr.pause()

    def find_direction(self):
        max_speed = 50.0
        pos_x = self.position.x
        pos_y = self.position.y
        lurk_rect = pygame.Rect((64,64), (pos_x-32, pos_y-32))
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
        self.velocity.x = 0
        self.velocity.y = 0
        font = pygame.font.SysFont("Dejavu Sans", 32)
        title = font.render("GAME OVER", True, (255, 0, 0))
        s = pygame.display.get_surface()
        r = s.blit(title, (0,0))
        pygame.display.flip()
