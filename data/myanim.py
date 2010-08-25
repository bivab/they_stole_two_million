version   = ['animation', '0.0.1', 'pyknic']    # [type, version, vendor]
dt        = 0.2           # 1/fps [s]
offset    = [16,16]      # (opt) anchor point
pixelspeed= 10            # (opt) how many pixels/s it should be moved to match animation speed
imagefile = 'images/rob01_sprite.png'    # rectsfile has to refere also to this imagefile
rectsfile = 'myrects'     # other module to load
#colorkey  =  [255,0,255]    # might be None
#blendmode = 'BLEND_RGB_ADD'             # same as in pygame: BLEND_ADD, ..., see pygame documentation

up   = [{'rects': 3},
        {'rects': 4}]

down  = [{'rects': 9},
        {'rects': 8}]

left  = [{'rects': 13},
        {'rects': 14}]

right  = [{'rects': 18},
        {'rects': 19}]
