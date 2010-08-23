#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: main.py 239 2009-07-27 20:41:19Z dr0iddr0id $'

# do not use __file__ because it is not set if using py2exe

# put your imports here
from pyknic.resources.tiledtmxloader import TileMapParser, ImageLoaderPygame
import pyknic

def demo_pygame(file_name):
    pygame = __import__('pygame')

    # parser the map
    world_map = TileMapParser().parse_decode(file_name)
    # init pygame and set up a screen
    pygame.init()
    pygame.display.set_caption("tiledtmxloader - " + file_name)
    screen_width = min(1024, world_map.pixel_width)
    screen_height = min(768, world_map.pixel_height)
    screen = pygame.display.set_mode((screen_width, screen_height))

    # load the images using pygame
    world_map.load(ImageLoaderPygame())
    #printer(world_map)

    # an example on how to access the map data and draw an orthoganl map
    # draw the map
    assert world_map.orientation == "orthogonal"

    running = True
    dirty = True
    # cam_offset is for scrolling
    cam_offset_x = 0
    cam_offset_y = 0
    # mainloop
    
    SPEED = 3
    
    pygame.key.set_repeat(50)
    
    while running:
        # eventhandling
        events = [pygame.event.wait()]
    #    print events
        events.extend(pygame.event.get())
        for event in events:
            
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                dirty = True
                if event.key == pygame.K_ESCAPE:
                    running = False

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_DOWN]:    
            cam_offset_y -= SPEED
        
        if pressed_keys[pygame.K_UP]: 
            cam_offset_y += SPEED    
        
        if pressed_keys[pygame.K_LEFT]:    
                cam_offset_x += SPEED

        if pressed_keys[pygame.K_RIGHT]:    
                cam_offset_x -= SPEED
                
        # draw the map
        if dirty:
            dirty = False
            screen.fill((255,255,255))
            for layer in world_map.layers[:]:
                if layer.visible:
                    idx = 0
                    # loop over all tiles
#                    import pdb
#                    pdb.set_trace()
                    for y in xrange(0, layer.pixel_height, world_map.tileheight):
                        for x in xrange(0, layer.pixel_width, world_map.tilewidth):
                            # add offset in number of tiles
                            x += layer.x * world_map.tilewidth
                            y += layer.y * world_map.tileheight
                            # get the gid at this position
                            img_idx = layer.decoded_content[idx]
                            idx += 1
                            if img_idx:
                                # get the actual image and its offset
                                offx, offy, screen_img = world_map.indexed_tiles[img_idx]
                                # only draw the tiles that are relly visible (speed up)
                                if True: #x >= cam_offset_x - 3 * world_map.tilewidth and x + cam_offset_x <= screen_width + world_map.tilewidth\
                                   #and y >= cam_offset_y - 3 * world_map.tileheight and y + cam_offset_y <= screen_height + 3 * world_map.tileheight:
                                    if screen_img.get_alpha():
                                        screen_img = screen_img.convert_alpha()
                                    else:
                                        screen_img = screen_img.convert()
                                        if layer.opacity > -1:
                                            #print 'per surf alpha', layer.opacity
                                            screen_img.set_alpha(None)
                                            alpha_value = int(255. * float(layer.opacity))
                                            screen_img.set_alpha(alpha_value)
                                    screen_img = screen_img.convert_alpha()
                                    # draw image at right position using its offset
                                    screen.blit(screen_img, (x + cam_offset_x + offx, y + cam_offset_y + offy))
        
            r =  pygame.Rect((250, 150), (30,30))
            player =  pygame.draw.rect(screen, (0, 255, 0), r, 1)
        
        
            # map objects
            for obj_group in world_map.object_groups:
                goffx = obj_group.x
                goffy = obj_group.y
                if True: #goffx >= cam_offset_x - 3 * world_map.tilewidth and goffx + cam_offset_x <= screen_width + world_map.tilewidth \
                   #and goffy >= cam_offset_y - 3 * world_map.tileheight and goffy + cam_offset_y <= screen_height + 3 * world_map.tileheight:
                    for map_obj in obj_group.objects:
                        size = (map_obj.width, map_obj.height)
#                        import pdb
#                        pdb.set_trace()
                        
                        if map_obj.image_source:
                            surf = pygame.image.load(map_obj.image_source)
                            surf = pygame.transform.scale(surf, size)
                            screen.blit(surf, (goffx + map_obj.x + cam_offset_x, goffy + map_obj.y + cam_offset_y))
                        else:
                            r = pygame.Rect((goffx + map_obj.x + cam_offset_x, goffy + map_obj.y + cam_offset_y), size)
                            pygame.draw.rect(screen, (255, 255, 0), r, 1)
            # simple pygame
            pygame.display.flip()



def main():
#    demo_pygame("./data/maps/fishingvilla.tmx")
    demo_pygame("./data/testtile.tmx")
    print "foo"


# this is needed in order to work with py2exe
if __name__ == '__main__':
    main()
