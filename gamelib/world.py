# -*- coding: utf-8 -*-
#
import pygame
import pyknic

class TheWorld(pyknic.world.IWorld):
    def add_entity(self, entity):
        if entity not in self._entities:
            self._entities.append(entity)

    def remove_entity(self, entity):
        if entity in self._entities:
            self._entities.remove(entity)

    def get_entities_in_region(self, world_rect):
        u"""should return a ordered by layer list of entites to of this region"""
        return [self._entities[i] for i in world_rect.collidelistall(self._entities)]

    def screen_to_world(self, screen_coord):
        r = pygame.Rect(screen_coord, (0, 0))
        idx = r.collidelist(self._renderers)
        if idx > -1:
            return self._renderers[idx].screen_to_world(screen_coord)
        return None

    def get_entites_from_screen_coords(self, screen_coord):
        r = pygame.Rect(screen_coord, (0, 0))
        for idx in r.collidelistall(self._renderers):
            world_rect = pygame.Rect(self._renderers[idx].screen_to_world(screen_coord).as_xy_tuple(), (0, 0))
            entities = self.get_entities_in_region(world_rect)
            if entities:
                return entities
        return None

