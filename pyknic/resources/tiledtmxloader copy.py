#!/usr/bin/python
# -*- coding: utf-8 -*-

u"""
TileMap loader for python for Tiled, a generic tile map editor 
from http://mapeditor.org/ .
It loads the \*.tmx files produced by Tiled.
"""

__version__ = u'$Id: tiledtmxloader.py 293 2009-08-02 18:48:50Z dr0iddr0id $'
__author__ = u'DR0ID_ @ 2009'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

#-------------------------------------------------------------------------------


import sys
from xml.dom import minidom, Node
import base64
import gzip
import StringIO
import os.path
#import codecs

# TODO: ideas: save indexed_tiles as {type:data} so no image loader is needed
# user would have to write its own image loading
# different types would be : {gid : ('img_parts', (margin, spacing, path, tile_w, tile_h, colorkey))}
#                            {gid : ('img_path', ('C:/...', colorkey)}
#                            {gid : ('file_like', (file_like_obj, colorkey))}
#
# maybe use cStringIO instead of StringIO

#-------------------------------------------------------------------------------
class IImageLoader(object):
    u"""
    Interface for image loading. Depending on the framework used the
    images have to be loaded differently.
    """

    def load_image(self, filename, colorkey=None): # -> image
        u"""
        Load a single image.
        
        :Parameters:
            filename : string
                Path to the file to be loaded.
            colorkey : tuple
                The (r, g, b) color that should be used as colorkey (or magic color).
                Default: None
        
        :rtype: image
        
        """
        raise NotImplementedError(u'This should be implemented in a inherited class')

    def load_image_file_like(self, file_like_obj, colorkey=None): # -> image
        u"""
        Load a image from a file like object.
        
        :Parameters:
            file_like_obj : file
                This is the file like object to load the image from.
            colorkey : tuple
                The (r, g, b) color that should be used as colorkey (or magic color).
                Default: None
        
        :rtype: image
        """
        raise NotImplementedError(u'This should be implemented in a inherited class')

    def load_image_parts(self, filename, margin, spacing, tile_width, tile_height, colorkey=None): #-> [images]
        u"""
        Load different tile images from one source image.
        
        :Parameters:
            filename : string
                Path to image to be loaded.
            margin : int
                The margin around the image.
            spacing : int
                The space between the tile images.
            tile_width : int
                The width of a single tile.
            tile_height : int
                The height of a single tile.
            colorkey : tuple
                The (r, g, b) color that should be used as colorkey (or magic color).
                Default: None
            
        Luckily that iteration is so easy in python::
        
            ...
            w, h = image_size
            for y in xrange(margin, h, tile_height + spacing):
                for x in xrange(margin, w, tile_width + spacing):
                    ...
            
        :rtype: a list of images
        """
        raise NotImplementedError(u'This should be implemented in a inherited class')

#-------------------------------------------------------------------------------
class ImageLoaderPygame(IImageLoader):
    u"""
    Pygame image loader.
    
    It uses an internal image cache. The methods return Surface.
    
    :Undocumented:
        pygame
    """


    def __init__(self):
        self.pygame = __import__('pygame')
        self._img_cache = {} # {name: surf}

    def load_image(self, filename, colorkey=None):
        img = self._img_cache.get(filename, None)
        if img is None:
            img = self.pygame.image.load(filename)
            self._img_cache[filename] = img
        if colorkey:
            img.set_colorkey(colorkey)
        return img

    def load_image_part(self, filename, x, y, w, h, colorkey=None):
        source_rect = self.pygame.Rect(x, y, w, h)
        img = self._img_cache.get(filename, None)
        if img is None:
            img = self.pygame.image.load(filename)
            self._img_cache[filename] = img
        img_part = self.pygame.Surface((w, h), 0, img)
        img_part.blit(img, (0, 0), source_rect)
        if colorkey:
            img_part.set_colorkey(colorkey)
        return img_part

    def load_image_parts(self, filename, margin, spacing, tile_width, tile_height, colorkey=None): #-> [images]
        source_img = self._img_cache.get(filename, None)
        if source_img is None:
            source_img = self.pygame.image.load(filename)
            self._img_cache[filename] = source_img
        w, h = source_img.get_size()
        images = []
        for y in xrange(margin, h, tile_height + spacing):
            for x in xrange(margin, w, tile_width + spacing):
                img_part = self.pygame.Surface((tile_width, tile_height), 0, source_img)
                img_part.blit(source_img, (0, 0), self.pygame.Rect(x, y, tile_width, tile_height))
                if colorkey:
                    img_part.set_colorkey(colorkey)
                images.append(img_part)
        return images

    def load_image_file_like(self, file_like_obj, colorkey=None): # -> image
        # pygame.image.load can load from a path and from a file-like object
        # that is why here it is redirected to the other method
        return self.load_image(file_like_obj, colorkey)

#-------------------------------------------------------------------------------
class ImageLoaderPyglet(IImageLoader):
    u"""
    Pyglet image loader.
    
    It uses an internal image cache. The methods return some form of
    AbstractImage. The resource module is not used for loading the images.
    
    Thanks to HydroKirby from #pyglet to contribute the ImageLoaderPyglet and the pyglet demo!
    
    :Undocumented:
        pyglet
    """


    def __init__(self):
        self.pyglet = __import__('pyglet')
        self._img_cache = {} # {name: image}

    def load_image(self, filename, colorkey=None, fileobj=None):
        img = self._img_cache.get(filename, None)
        if img is None:
            if fileobj:
                img = self.pyglet.image.load(filename, fileobj, self.pyglet.image.codecs.get_decoders("*.png")[0])
            else:
                img = self.pyglet.image.load(filename)
            self._img_cache[filename] = img
        return img

    def load_image_part(self, filename, x, y, w, h, colorkey=None):
        img = self._img_cache.get(filename, None)
        if img is None:
            img = self.pyglet.image.load(filename)
            self._img_cache[filename] = img
        img_part = image.get_region(x, y, w, h)
        return img_part

    def load_image_parts(self, filename, margin, spacing, tile_width, tile_height, colorkey=None): #-> [images]
        source_img = self._img_cache.get(filename, None)
        if source_img is None:
            source_img = self.pyglet.image.load(filename)
            self._img_cache[filename] = source_img
        images = []
        # Reverse the map column reading to compensate for pyglet's y-origin.
        for y in xrange(source_img.height - tile_height, margin - tile_height,
            -tile_height - spacing):
            for x in xrange(margin, source_img.width, tile_width + spacing):
                #img_part = source_img.get_region(x, y, tile_width, tile_height)
                img_part = source_img.get_region(x, y - spacing, tile_width, tile_height)
                images.append(img_part)
        return images

    def load_image_file_like(self, file_like_obj, colorkey=None): # -> image
        # pygame.image.load can load from a path and from a file-like object
        # that is why here it is redirected to the other method
        return self.load_image(file_like_obj, colorkey, file_like_obj)

#-------------------------------------------------------------------------------
class TileMap(object):
    u"""

    The TileMap holds all the map data.

    :Ivariables:
        orientation : string
            orthogonal or isometric or hexagonal or shifted
        tilewidth : int
            width of the tiles (for all layers)
        tileheight : int
            height of the tiles (for all layers)
        width : int
            width of the map (number of tiles)
        height : int
            height of the map (number of tiles)
        version : string
            version of the map format
        tile_sets : list
            list of TileSet
        properties : dict
            the propertis set in the editor, name-value pairs, strings
        pixel_width : int
            width of the map in pixels
        pixel_height : int
            height of the map in pixels
        layers : list
            list of TileLayer
        map_file_name : dict
            file name of the map
        object_groups : list
            list of :class:MapObjectGroup
        indexed_tiles : dict
            dict containing {gid : (offsetx, offsety, surface} if load() was called
            when drawing just add the offset values to the draw point
        named_layers : dict of string:TledLayer
            dict containing {name : TileLayer}
        named_tile_sets : dict
            dict containing {name : TileSet}

    """


    def __init__(self):
#        This is the top container for all data. The gid is the global id (for a image).
#        Before calling convert most of the values are strings. Some additional 
#        values are also calculated, see convert() for details. After calling 
#        convert, most values are integers or floats where appropriat.
        u"""
        The TileMap holds all the map data.
        """
        # set through parser
        self.orientation = None
        self.tileheight = 0
        self.tilewidth = 0
        self.width = 0
        self.height = 0
        self.version = 0
        self.tile_sets = [] # TileSet
        self.layers = [] # WorldTileLayer <- what order? back to front (guessed)
        self.indexed_tiles = {} # {gid: (offsetx, offsety, image}
        self.object_groups = []
        self.properties = {} # {name: value}
        # additional info
        self.pixel_width = 0
        self.pixel_height = 0
        self.named_layers = {} # {name: layer}
        self.named_tile_sets = {} # {name: tile_set}
        self.map_file_name = ""
        self._image_loader = None

    def convert(self):
        u"""
        Converts numerical values from strings to numerical values.
        It also calculates or set additional data:
        pixel_width
        pixel_height
        named_layers
        named_tile_sets
        """
        self.tilewidth = int(self.tilewidth)
        self.tileheight = int(self.tileheight)
        self.width = int(self.width)
        self.height = int(self.height)
        self.pixel_width = self.width * self.tilewidth
        self.pixel_height = self.height * self.tileheight
        for layer in self.layers:
            self.named_layers[layer.name] = layer
            layer.opacity = float(layer.opacity)
            layer.x = int(layer.x)
            layer.y = int(layer.y)
            layer.width = int(layer.width)
            layer.height = int(layer.height)
            layer.pixel_width = layer.width * self.tilewidth
            layer.pixel_height = layer.height * self.tileheight
            layer.visible = bool(int(layer.visible))
        for tile_set in self.tile_sets:
            self.named_tile_sets[tile_set.name] = tile_set
            tile_set.spacing = int(tile_set.spacing)
            tile_set.margin = int(tile_set.margin)
            for img in tile_set.images:
                if img.trans:
                    img.trans = (int(img.trans[:2], 16), int(img.trans[2:4], 16), int(img.trans[4:], 16))
        for obj_group in self.object_groups:
            obj_group.x = int(obj_group.x)
            obj_group.y = int(obj_group.y)
            obj_group.width = int(obj_group.width)
            obj_group.height = int(obj_group.height)
            for map_obj in obj_group.objects:
                map_obj.x = int(map_obj.x)
                map_obj.y = int(map_obj.y)
                map_obj.width = int(map_obj.width)
                map_obj.height = int(map_obj.height)

    def load(self, image_loader):
        u"""
        loads all images using a IImageLoadermage implementation and fills up
        the indexed_tiles dictionary. 
        The image may have per pixel alpha or a colorkey set.
        """
        self._image_loader = image_loader
        for tile_set in self.tile_sets:
            # do images first, because tiles could reference it
            for img in tile_set.images:
                if img.source:
                    self._load_image_from_source(tile_set, img)
                else:
                    tile_set.indexed_images[img.id] = self._load_image(img)
            # tiles
            for tile in tile_set.tiles:
                for img in tile.images:
                    if not img.content and not img.source:
                        # only image id set
                        indexed_img = tile_set.indexed_images[img.id]
                        self.indexed_tiles[int(tile_set.firstgid) + int(tile.id)] = (0, 0, indexed_img)
                    else:
                        if img.source:
                            self._load_image_from_source(tile_set, img)
                        else:
                            indexed_img = self._load_image(img)
                            self.indexed_tiles[int(tile_set.firstgid) + int(tile.id)] = (0, 0, indexed_img)

    def _load_image_from_source(self, tile_set, a_tile_image):
        # relative path to file
        img_path = os.path.join(os.path.dirname(self.map_file_name), a_tile_image.source)
        tile_width = int(self.tilewidth)
        tile_height = int(self.tileheight)
        if tile_set.tileheight:
            tile_width = int(tile_set.tilewidth)
        if tile_set.tilewidth:
            tile_height = int(tile_set.tileheight)
        offsetx = 0
        offsety = 0
#        if tile_width > self.tilewidth:
#            offsetx = tile_width
        if tile_height > self.tileheight:
            offsety = tile_height - self.tileheight
        idx = 0
        for image in self._image_loader.load_image_parts(img_path, \
                    tile_set.margin, tile_set.spacing, tile_width, tile_height, a_tile_image.trans):
            self.indexed_tiles[int(tile_set.firstgid) + idx] = (offsetx, -offsety, image)
            idx += 1

    def _load_image(self, a_tile_image):
        img_str = a_tile_image.content
        if a_tile_image.encoding:
            if a_tile_image.encoding == u'base64':
                img_str = decode_base64(a_tile_image.content)
            else:
                raise Exception(u'unknown image encoding %s' % a_tile_image.encoding)
        sio = StringIO.StringIO(img_str)
        new_image = self._image_loader.load_image_file_like(sio, a_tile_image.trans)
        return new_image

    def decode(self):
        u"""
        Decodes the TileLayer encoded_content and saves it in decoded_content.
        """
        for layer in self.layers:
            layer.decode()
#-------------------------------------------------------------------------------

class TileSet(object):
    u"""
    A tileset holds the tiles and its images.
    
    :Ivariables:
        firstgid : int
            the first gid of this tileset
        name : string
            the name of this TileSet
        images : list
            list of TileImages
        tiles : list
            list of Tiles
        indexed_images : dict
            after calling load() it is dict containing id: image
        indexed_tiles : dict
            after calling load() it is a dict containing 
            gid: (offsetx, offsety, image) , the image corresponding to the gid
        spacing : int
            the spacing between tiles
        marging : int
            the marging of the tiles
        properties : dict
            the propertis set in the editor, name-value pairs
        tilewidth : int
            the actual width of the tile, can be different from the tilewidth of the map
        tilehight : int
            the actual hight of th etile, can be different from the tilehight of the  map
    
    """

    def __init__(self):
        self.firstgid = 0
        self.name = None
        self.images = [] # TileImage
        self.tiles = [] # Tile
        self.indexed_images = {} # {id:image}
        self.indexed_tiles = {} # {gid: (offsetx, offsety, image} <- actually in map data
        self.spacing = 0
        self.margin = 0
        self.properties = {}
        self.tileheight = 0
        self.tilewidth = 0

#-------------------------------------------------------------------------------

class TileImage(object):
    u"""
    An image of a tile or just an image.
    
    :Ivariables:
        id : int
            id of this image (has nothing to do with gid)
        format : string
            the format as string, only 'png' at the moment
        source : string
            filename of the image. either this is set or the content
        encoding : string
            encoding of the content
        trans : tuple of (r,g,b)
            the colorkey color, raw as hex, after calling convert just a (r,g,b) tuple
        properties : dict
            the propertis set in the editor, name-value pairs
        image : TileImage
            after calling load the pygame surface
    """

    def __init__(self):
        self.id = 0
        self.format = None
        self.source = None
        self.encoding = None # from <data>...</data>
        self.content = None # from <data>...</data>
        self.image = None
        self.trans = None
        self.properties = {} # {name: value}

#-------------------------------------------------------------------------------

class Tile(object):
    u"""
    A single tile.
    
    :Ivariables:
        id : int
            id of the tile gid = TileSet.firstgid + Tile.id
        images : list of :class:TileImage
            list of TileImage, either its 'id' or 'image data' will be set
        properties : dict of name:value
            the propertis set in the editor, name-value pairs
    """

    def __init__(self):
        self.id = 0
        self.images = [] # uses TileImage but either only id will be set or image data
        self.properties = {} # {name: value}

#-------------------------------------------------------------------------------

class TileLayer(object):
    u"""
    A layer of the world.
    
    :Ivariables:
        x : int
            position of layer in the world in number of tiles (not pixels)
        y : int
            position of layer in the world in number of tiles (not pixels)
        width : int
            layer width in tiles
        height : int
            layer height in tiles
        pixel_width : int
            width of layer in pixels
        pixel_height : int
            height of layer in pixels
        name : string
            name of this layer
        opacity : float
            float from 0 (full transparent) to 1.0 (opaque)
        decod_content : list
            list of gid going through the map::
            
                e.g [1, 1, 1, ]
                where decoded_content[0] is (0,0)
                      decoded_content[1] is (1,0)
                      ...
                      decoded_content[1] is (width,0)
                      decoded_content[1] is (0,1)
                      ...
                      decoded_content[1] is (width,height)
    
    """

    def __init__(self):
        self.width = 0
        self.height = 0
        self.x = 0
        self.y = 0
        self.pixel_width = 0
        self.pixel_height = 0
        self.name = None
        self.opacity = -1
        self.encoding = None
        self.compression = None
        self.encoded_content = None
        self.decoded_content = []
        self.visible = True
        self.properties = {} # {name: value}

    def decode(self):
        u"""
        Converts the contents in a list of integers which are the gid of the used
        tiles. If necessairy it decodes and uncompresses the contents.
        """
        s = self.encoded_content
        if self.encoded_content:
            if self.encoding:
                if self.encoding == u'base64':
                    s = decode_base64(s)
                else:
                    raise Exception(u'unknown data encoding %s' % (self.encoding))
            if self.compression:
                if self.compression == u'gzip':
                    s = decompress_gzip(s)
                else:
                    raise Exception(u'unknown data compression %s' %(self.compression))
        else:
            raise Exception(u'no encoded content to decode')
        self.decoded_content = []
        for idx in xrange(0, len(s), 4):
            val = ord(str(s[idx])) | (ord(str(s[idx + 1])) << 8) | \
                 (ord(str(s[idx + 2])) << 16) | (ord(str(s[idx + 3])) << 24)
            self.decoded_content.append(val)

    def pretty_print(self):
        num = 0
        for y in range(int(self.height)):
            s = u""
            for x in range(int(self.width)):
                s += str(self.decoded_content[num])
                num += 1
            print s
#-------------------------------------------------------------------------------

class MapObjectGroup(object):
    u"""
    Group of objects on the map.
    
    :Ivariables:
        x : int
            the x position
        y : int
            the y position
        width : int
            width of the bounding box (usually 0, so no use)
        height : int
            height of the bounding box (usually 0, so no use)
        name : string
            name of the group
        objects : list
            list of the map objects
    
    """

    def __init__(self):
        self.width = 0
        self.height = 0
        self.name = None
        self.objects = []
        self.x = 0
        self.y = 0
        self.properties = {} # {name: value}

#-------------------------------------------------------------------------------

class MapObject(object):
    u"""
    A single object on the map.
    
    :Ivariables:
        x : int
            x position relative to group x position
        y : int
            y position relative to group y position
        width : int
            width of this object
        height : int
            height of this object
        type : string
            the type of this object
        image_source : string
            source path of the image for this object
        image : :class:TileImage
            after loading this is the pygame surface containing the image
    """
    def __init__(self):
        self.name = None
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.type = None
        self.image_source = None
        self.image = None
        self.properties = {} # {name: value}

#-------------------------------------------------------------------------------
def decode_base64(in_str):
    u"""
    Decodes a base64 string and returns it.

    :Parameters:
        in_str : string
            base64 encoded string

    :returns: decoded string
    """
    return base64.decodestring(in_str)

#-------------------------------------------------------------------------------
def decompress_gzip(in_str):
    u"""
    Uncompresses a gzip string and returns it.

    :Parameters:
        in_str : string
            gzip compressed string

    :returns: uncompressed string
    """
    # gzip can only handle file object therefore using StringIO
    copmressed_stream = StringIO.StringIO(in_str)
    gzipper = gzip.GzipFile(fileobj=copmressed_stream)
    s = gzipper.read()
    gzipper.close()
    return s

#-------------------------------------------------------------------------------
def printer(obj, ident=''):
    u"""
    Helper function, prints a hirarchy of objects.
    """
    import inspect
    print ident + obj.__class__.__name__.upper()
    ident += '    '
    lists = []
    for name in dir(obj):
        elem = getattr(obj, name)
        if isinstance(elem, list) and name != u'decoded_content':
            lists.append(elem)
        elif not inspect.ismethod(elem):
            if not name.startswith('__'):
                if name == u'data' and elem:
                    print ident + u'data = '
                    printer(elem, ident + '    ')
                else:
                    print ident + u'%s\t= %s' % (name, getattr(obj, name))
    for l in lists:
        for i in l:
            printer(i, ident + '    ')

#-------------------------------------------------------------------------------
class TileMapParser(object):
    u"""
    Allows to parse and decode map files for 'Tiled', a open source map editor 
    written in java. It can be found here: http://mapeditor.org/
    """

    def _build_tile_set(self, tile_set_node, world_map):
        tile_set = TileSet()
        self._set_attributes(tile_set_node, tile_set)
        for node in self._get_nodes(tile_set_node.childNodes, u'image'):
            self._build_tile_set_image(node, tile_set)
        for node in self._get_nodes(tile_set_node.childNodes, u'tile'):
            self._build_tile_set_tile(node, tile_set)
        self._set_attributes(tile_set_node, tile_set)
        world_map.tile_sets.append(tile_set)

    def _build_tile_set_image(self, image_node, tile_set):
        image = TileImage()
        self._set_attributes(image_node, image)
        # id of TileImage has to be set!! -> Tile.TileImage will only have id set
        for node in self._get_nodes(image_node.childNodes, u'data'):
            self._set_attributes(node, image)
            image.content = node.childNodes[0].nodeValue
        tile_set.images.append(image)

    def _build_tile_set_tile(self, tile_set_node, tile_set):
        tile = Tile()
        self._set_attributes(tile_set_node, tile)
        for node in self._get_nodes(tile_set_node.childNodes, u'image'):
            self._build_tile_set_tile_image(node, tile)
        tile_set.tiles.append(tile)

    def _build_tile_set_tile_image(self, tile_node, tile):
        tile_image = TileImage()
        self._set_attributes(tile_node, tile_image)
        for node in self._get_nodes(tile_node.childNodes, u'data'):
            self._set_attributes(node, tile_image)
            tile_image.content = node.childNodes[0].nodeValue
        tile.images.append(tile_image)

    def _build_layer(self, layer_node, world_map):
        layer = TileLayer()
        self._set_attributes(layer_node, layer)
        for node in self._get_nodes(layer_node.childNodes, u'data'):
            self._set_attributes(node, layer)
            layer.encoded_content = node.lastChild.nodeValue
        world_map.layers.append(layer)

    def _build_world_map(self, world_node):
        world_map = TileMap()
        self._set_attributes(world_node, world_map)
        if world_map.version != u"1.0":
            raise Exception(u'this parser was made for maps of version 1.0, found version %s' % world_map.version)
        for node in self._get_nodes(world_node.childNodes, u'tileset'):
            self._build_tile_set(node, world_map)
        for node in self._get_nodes(world_node.childNodes, u'layer'):
            self._build_layer(node, world_map)
        for node in self._get_nodes(world_node.childNodes, u'objectgroup'):
            self._build_object_groups(node, world_map)
        return world_map

    def _build_object_groups(self, object_group_node, world_map):
        object_group = MapObjectGroup()
        self._set_attributes(object_group_node,  object_group)
        for node in self._get_nodes(object_group_node.childNodes, u'object'):
            tiled_object = MapObject()
            self._set_attributes(node, tiled_object)
            for img_node in self._get_nodes(node.childNodes, u'image'):
                tiled_object.image_source = img_node.attributes[u'source'].nodeValue
            object_group.objects.append(tiled_object)
        world_map.object_groups.append(object_group)

    #-- helpers --#
    def _get_nodes(self, nodes, name):
        for node in nodes:
            if node.nodeType == Node.ELEMENT_NODE and node.nodeName == name:
                yield node

    def _set_attributes(self, node, obj):
        attrs = node.attributes
        for attr_name in attrs.keys():
            setattr(obj, attr_name, attrs.get(attr_name).nodeValue)
        self._get_properties(node, obj)

    def _get_properties(self, node, obj):
        props = {}
        for properties_node in self._get_nodes(node.childNodes, u'properties'):
            for property_node in self._get_nodes(properties_node.childNodes, u'property'):
                try:
                    props[property_node.attributes[u'name'].nodeValue] = property_node.attributes[u'value'].nodeValue
                except KeyError:
                    props[property_node.attributes[u'name'].nodeValue] = property_node.lastChild.nodeValue
        obj.properties = props


    #-- parsers --#
    def parse(self, file_name):
        u"""
        Parses the given map. Does no decoding nor loading the data.
        :return: instance of TileMap
        """
        #dom = minidom.parseString(codecs.open(file_name, "r", "utf-8").read())
        dom = minidom.parseString(open(file_name, "rb").read())
        for node in self._get_nodes(dom.childNodes, 'map'):
            world_map = self._build_world_map(node)
            break
        world_map.map_file_name = os.path.abspath(file_name)
        world_map.convert()
        return world_map

    def parse_decode(self, file_name):
        u"""
        Parses the map but additionally decodes the data.
        :return: instance of TileMap
        """
        world_map = TileMapParser().parse(file_name)
        world_map.decode()
        return world_map

    def parse_decode_load(self, file_name, image_loader):
        u"""
        Parses the data, decodes them and loads the images as pygame surfaces.
        :return: instance of TileMap
        """
        world_map = self.parse_decode(file_name)
        world_map.load(image_loader)
        return world_map

#-------------------------------------------------------------------------------
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
    while running:
        # eventhandling
        events = [pygame.event.wait()]
        events.extend(pygame.event.get())
        for event in events:
            dirty = True
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_DOWN:
                    cam_offset_y -= world_map.tileheight
                elif event.key == pygame.K_UP:
                    cam_offset_y += world_map.tileheight
                elif event.key == pygame.K_LEFT:
                    cam_offset_x += world_map.tilewidth
                elif event.key == pygame.K_RIGHT:
                    cam_offset_x -= world_map.tilewidth
        
        # draw the map
        if dirty:
            dirty = False
            for layer in world_map.layers[:]:
                if layer.visible:
                    idx = 0
                    # loop over all tiles
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
                                if x >= cam_offset_x - 3 * world_map.tilewidth and x + cam_offset_x <= screen_width + world_map.tilewidth\
                                   and y >= cam_offset_y - 3 * world_map.tileheight and y + cam_offset_y <= screen_height + 3 * world_map.tileheight:
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
            # map objects
            for obj_group in world_map.object_groups:
                goffx = obj_group.x
                goffy = obj_group.y
                if goffx >= cam_offset_x - 3 * world_map.tilewidth and goffx + cam_offset_x <= screen_width + world_map.tilewidth \
                   and goffy >= cam_offset_y - 3 * world_map.tileheight and goffy + cam_offset_y <= screen_height + 3 * world_map.tileheight:
                    for map_obj in obj_group.objects:
                        size = (map_obj.width, map_obj.height)
                        if map_obj.image_source:
                            surf = pygame.image.load(map_obj.image_source)
                            surf = pygame.transform.scale(surf, size)
                            screen.blit(surf, (goffx + map_obj.x + cam_offset_x, goffy + map_obj.y + cam_offset_y))
                        else:
                            r = pygame.Rect((goffx + map_obj.x + cam_offset_x, goffy + map_obj.y + cam_offset_y), size)
                            pygame.draw.rect(screen, (255, 255, 0), r, 1)
            # simple pygame
            pygame.display.flip()

#-------------------------------------------------------------------------------

def demo_pyglet(file_name):
    import pyglet
    from pyglet.gl import glTranslatef, glLoadIdentity


    world_map = TileMapParser().parse_decode(file_name)
    # This is a list because pyglet's scoping is annoying.
    delta = [0.0, 0.0]
    window = pyglet.window.Window()

    @window.event
    def on_draw():
        window.clear()
        glLoadIdentity()
        glTranslatef(delta[0], delta[1], 0.0)
        batch.draw()
    
    keys = pyglet.window.key.KeyStateHandler()
    window.push_handlers(keys)
    world_map.load(ImageLoaderPyglet())

    def update(dt):
        speed = 3.0 + keys[pyglet.window.key.LSHIFT] * 6.0
        if keys[pyglet.window.key.LEFT]:
            delta[0] += speed
        if keys[pyglet.window.key.RIGHT]:
            delta[0] -= speed
        if keys[pyglet.window.key.UP]:
            delta[1] -= speed
        if keys[pyglet.window.key.DOWN]:
            delta[1] += speed

    batch = pyglet.graphics.Batch()
    groups = []
    sprites = []
    for group_num, layer in enumerate(world_map.layers[:]):
        if not layer.visible:
            continue
        groups.append(pyglet.graphics.OrderedGroup(group_num))
        id_index = 0
        # Reversed for pyglet's y-perspective.
        for y in xrange(layer.pixel_height - world_map.tileheight,
            -world_map.tileheight, -world_map.tileheight):
            for x in xrange(0, layer.pixel_width, world_map.tilewidth):
                image_id = layer.decoded_content[id_index]
                id_index += 1
                if image_id:
                    offset_x, offset_y, image_file = \
                        world_map.indexed_tiles[image_id]
                    sprites.append(pyglet.sprite.Sprite(image_file,
                        x, y , batch=batch,
                        group=groups[group_num]))

    pyglet.clock.schedule_interval(update, 1.0 / 60.0)
    pyglet.app.run()

#-------------------------------------------------------------------------------
def main():

    args = sys.argv[1:]
    if len(args) != 2:
        #print 'usage: python test.py mapfile.tmx [pygame|pyglet]'
        print('usage: python %s your_map.tmx [pygame|pyglet]' % \
            os.path.basename(__file__))
        return

    if args[1] == 'pygame':
        demo_pygame(args[0])
    elif args[1] == 'pyglet':
        demo_pyglet(args[0])
    else:
        print 'missing framework, usage: python test.py mapfile.tmx [pygame|pyglet]'
        sys.exit(-1)

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()


if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))



