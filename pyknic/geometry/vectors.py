#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Vector calsses.

:Variables:
    PI_DIV_180 : float
        Just pi/-180.0 used for converting  between degrees and radians
        (negavite because of the rotation direction)

:Note:
    Make sure to know the difference between::
        
        u = Vec2()
        v = Vec2()
        w = Vec2()
        
        # only values are copied
        u = w.values
        # reference, v is actually lost and points now to w
        v = w
    
    When using ``v = w`` any change to w will also change w and vice versa 
    since both point to the same `Vec2` instance.

:Todo: investigate why PI_DIV_180 has to be negative?
"""

__version__ = '$Id: vectors.py 315 2009-08-30 05:24:49Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

import math
from math import hypot
from math import radians
from math import sin
from math import cos
from math import pi
from math import atan2
from math import sqrt

PI_DIV_180 = pi / -180.0



def sign(value):
    u"""
    Signum function. Computes the sign of a value.
    
    :Parameters:
        value : numerical
            Any number.
    
    :rtype: numerical
    
    :Returns:
        -1 if value was negative, 
        1 if value was positive, 
        0 if value was equal zero
    """
    assert isinstance(value, int) or isinstance(value, float)
    if 0 < value:
        return 1
    elif 0 > value:
        return -1
    else:
        return 0

#------------------------------------------------------------------------------

class Vec2(object):
    u"""
    See `vectors`
    
    2D vector class.
    
    :Ivariables:
        x : int, float
            x value
        y : int, float
            y value
    
    """

    __slots__ = tuple('xy')

    def __init__(self, x, y):
        u"""
        Constructor.
        
        :Parameters:
            x : int, float
                x value
            y : int, float
                y value
        """
        if __debug__:
            import decimal
            assert isinstance(x, (int, long, complex, float, decimal.Decimal))
            assert isinstance(y, (int, long, complex, float, decimal.Decimal))
        self.x = x
        self.y = y

    #-- properties --#
    def _set_values(self, other):
        assert isinstance(other, self.__class__)
        # TODO: should tuples and lists also be allowed?
        self.x = other.x
        self.y = other.y
    values = property(None, _set_values, doc=u'set only, value assignemt')

    def _set_from_iterable(self, other):
        oiter = iter(other)
        try:
            self.x = oiter.next()
            self.y = oiter.next()
        except StopIteration:
            pass
    from_iter = property(None, _set_from_iterable, 
                         doc=u'''
                                set only, vlaue assignment from iterable, 
                                if iterable is too short, old values will be 
                                left in place, e.g. iterable is [1] then only x 
                                will be set and y is unmodified''')

    def _length(self):
        return hypot(self.x, self.y)
    length = property(_length, doc=u"""returns length""")

    def _lengthSQ(self):
        return self.x * self.x + self.y * self.y
    lengthSQ = property(_lengthSQ, doc=u"""returns length squared""")

    def _normalized(self):
        leng = self.length
        if leng:
            return self.__class__(self.x / leng, self.y / leng)
        else:
            return self.__class__(0, 0)
    normalized = property(_normalized, doc=u"""returns new vector with unit length""")

    def _normal_L(self):
        """returns the right normal (perpendicular), not unit length"""
        return self.__class__(self.y, -self.x)
    normal_L = property(_normal_L)

    def _normal_R(self):
        """returns the left normal (perpendicular), not unit length"""
        return self.__class__(-self.y, self.x)
    normal_R = property(_normal_R)

    def _get_angle(self):
        angle = atan2(self.y, self.x) / PI_DIV_180
        if angle < 0:
            return - angle # add because angle is negative already
        return 360 - angle
    angle = property(_get_angle, doc=u"read only, returns angle, 0 is at 3 o'clock")

    #-- repr methods --#
    def __str__(self):
        return u"<%s(%s, %s) at %s>" %(self.__class__.__name__, self.x, self.y, hex(id(self)))

#    def __str__(self):
#        return u"<%s(%s, %s)>" %(self.__class__.__name__, self.x, self.y)

    #-- math --#
    def __add__(self, other):
        u"""+ operation"""
        assert isinstance(other, self.__class__)
        return self.__class__(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        u"""+= operation"""
        assert isinstance(other, self.__class__)
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        u"""- operation"""
        assert isinstance(other, self.__class__)
        return self.__class__(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        u"""-= operation"""
        assert isinstance(other, self.__class__)
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, scalar):
        u"""* operator, only scalar multiplication, for other use the methods"""
        return self.__class__(self.x * scalar,  self.y * scalar)
    __rmul__ = __mul__

    def __imul__(self, scalar):
        u""" \*= multiplication, scalar only"""
        self.x *= scalar
        self.y *= scalar
        return self

    def __len__(self):
        u"""returns always 2"""
        return 2

    def __div__(self, scalar):
        u"""/ operator, only scalar"""
        return self.__class__(self.x / scalar, self.y / scalar)

    def __idiv__(self, scalar):
        u"""/= operator, only scalar"""
        self.x /= scalar
        self.y /= scalar
        return self

    def __neg__(self):
        u"""- operator, same as -1 * v"""
        return self.__class__(-self.x, -self.y)

    def __pos__(self):
        u"""+ operator"""
        return self.__class__(abs(self.x), abs(self.y))

    #-- comparison --#
    def __eq__(self, other):
        u""" == operator, vectors are equal when components are equal, might not 
        make much sense since using a tolerance would be better"""
        # TODO: allow compares with tuples / lists of same dim ??
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        return False

    def __neq__(self, other):
        u"""same as 'not __eq__'"""
        return not self.__eq__(other)

    #-- items access --#
    def __getitem__(self, key):
        u"""[] operator, slow"""
        return (self.x, self.y)[key]

    def __iter__(self):
        u"""iterator, slow"""
        return iter((self.x, self.y))

    #-- additional methods --#
    def as_tuple(self):
        u"""
        Returns a tuple containing the vector values.
        
        :rtype: tuple
        :Returns: (x, y)
        
        """
        return self.x, self.y

    as_xy_tuple = as_tuple

    def round(self, n_digits=3):
        u"""
        Round values to n_digits.
        
        :Parameters:
            n_digits : int
                Number of digits after the point.
        """
        self.x = round(self.x, n_digits)
        self.y = round(self.y, n_digits)

    def rounded(self, n_digits=3):
        u"""
        Get a rounded vector.
        
        :Parameters:
            n_digits : int
                Number of digits after the point.
                
        :rtype: `Vec2`
        :Returns: `Vec2` rounded to n_digits
        """
        return self.__class__(round(self.x, n_digits), round(self.y, n_digits))

    def normalize(self):
        u"""
        Make the vector unit length.
        """
        leng = self.length
        self.x /= leng
        self.y /= leng

    def clone(self):
        u"""
        Clone the vector.
        
        :rtype: `Vec2`
        :Returns: a copy of itself.
        """
        return self.__class__(self.x, self.y)

    def dot(self, other):
        u"""
        Dot product.
        """
        assert isinstance(other, self.__class__)
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        u"""
        Cross product.
        
        :Parameters:
            other : `Vec2`
                The second vector for the cross product.
        
        :rtype: float
        :Returns: z value of the cross product (since x and y would be 0).
        :Note: a.cross(b) == - b.cross(a)
        """
        assert isinstance(other, self.__class__)
        return self.x * other.y - self.y * other.x

    def project_onto(self, other):
        u"""
        Project this vector onto another one.
        
        :Parameters:
            other : `Vec2`
                The other vector to project onto.
                
        :rtype: `Vec2`
        :Returns: The projected vector.
        """
        assert isinstance(other, self.__class__)
        return self.dot(other) / other.lengthSQ * other

    def reflect(self, normal):
        u"""normal should be normalized unitlength"""
        assert isinstance(normal, self.__class__)
        return self - 2 * self.dot(normal) * normal

    def reflect_tangent(self, tangent):
        u"""tangent should be normalized, unitlength"""
        assert isinstance(tangent, self.__class__)
        return 2 * tangent.dot(self) * tangent - self

    def rotate(self, degrees):
        u"""Rotates the vector bout the angle (degrees), + clockwise, - ccw"""
        rad = degrees * PI_DIV_180
        s = sin(rad)
        c = cos(rad)
        x = self.x
        self.x = c * x + s * self.y
        self.y = -s * x + c * self.y

    def rotated(self, degrees):
        u"""
        Returns a new vector, rotated about angle (degrees), + clockwise, - ccw
        """
        rad = degrees * PI_DIV_180
        s = sin(rad)
        c = cos(rad)
        return self.__class__(c * self.x + s * self.y, -s * self.x + c * self.y)

    def rotate_to(self, angle_degrees):
        u"""rotates the vector to the given angle (degrees)."""
        self.rotate(angle_degrees - self.angle)

    def get_angle_between(self, other):
        u"""Returns the angle between the vectors."""
        assert isinstance(other, self.__class__)
        return  self.dot(other)/ (PI_DIV_180 * self.length * other.length)

#------------------------------------------------------------------------------

class Vec3(object):
    u"""
    See `vectors`
    
    3D Vector.
    
    
    :Ivariables:
        x : int, float
            x, value
        y : int, float
            y, value
        z : int, float
            z, value
    """

    __slots__ = tuple('xyz')

    def __init__(self, x, y, z=0):
        u"""
        Constructor.
        
        :Parameters:
            x : int, float
                x value
            y : int, float
                y value
            z : int, float
                z value, defaults to 0
        """
        if __debug__:
            import decimal
            assert isinstance(x, (int, long, complex, float, decimal.Decimal))
            assert isinstance(y, (int, long, complex, float, decimal.Decimal))
            assert isinstance(z, (int, long, complex, float, decimal.Decimal))
        self.x = x
        self.y = y
        self.z = z

    #-- properties --#
    def _set_values(self, other):
        assert isinstance(other, self.__class__)
        # TODO: should tuples and lists also be allowed?
        self.x = other.x
        self.y = other.y
        self.z = other.z
    values = property(None, _set_values, doc=u'set only,value assignemt')

    def _set_from_iterable(self, other):
        oiter = iter(other)
        try:
            self.x = oiter.next()
            self.y = oiter.next()
            self.z = oiter.next()
        except StopIteration:
            pass
    from_iter = property(None, _set_from_iterable, 
                         doc=u'''
                                set only, vlaue assignment from iterable, 
                                if iterable is too short, old values will be 
                                left in place, e.g. iterable is [1,2] then 
                                only x and y will be set and z remains 
                                unmodified''')

    def _length(self):
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    length = property(_length, doc=u"""returns length of vector""")

    def _lengthSQ(self):
        return self.x * self.x + self.y * self.y + self.z * self.z
    lengthSQ = property(_lengthSQ, doc=u"""returns length squared of vector""")

    def _normalized(self):
        leng = self.length
        if leng:
            return self.__class__(self.x / leng, self.y / leng,  self.z / leng)
        else:
            return self.__class__(0, 0, 0)
    normalized = property(_normalized, doc=u"""returns new `Vec3` with unit length""")

    def _normal_L(self):
        """ not unit length, z is set to 0"""
        return self.__class__(self.y, -self.x)
    normal_L = property(_normal_L, doc=u"""returns the right normal, not unitlength""")

    def _normal_R(self):
        """ not unit length, z is set to 0"""
        return self.__class__(-self.y, self.x)
    normal_R = property(_normal_R, doc=u"""returns left normal, not unit length""")

    def _get_angle(self):
        u"""returns the angle for the x and y component"""
        angle = atan2(self.y, self.x) / PI_DIV_180
        if angle < 0:
            return - angle # add because angle is negative already
        return 360 - angle
    angle = property(_get_angle, doc=u"read only, returns angle of vector, 0 is at 3 o'clock")

    #-- repr methods --#
    def __str__(self):
        return u"<%s(%s, %s,%s) at %s>" %(self.__class__.__name__, self.x, self.y, self.z, hex(id(self)))

#    def __str__(self):
#        return u"<%s(%s, %s, %s)>" %(self.__class__.__name__, self.x, self.y, self.z)

    #-- math --#
    def __add__(self, other):
        u"""+ opertaor"""
        assert isinstance(other, self.__class__)
        return self.__class__(self.x + other.x, self.y + other.y, self.z + other.z)

    def __iadd__(self, other):
        u"""+= opertaor"""
        assert isinstance(other, self.__class__)
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __sub__(self, other):
        u"""- opertaor"""
        assert isinstance(other, self.__class__)
        return self.__class__(self.x - other.x, self.y - other.y,  self.z - other.z)

    def __isub__(self, other):
        u"""-= opertaor"""
        assert isinstance(other, self.__class__)
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __mul__(self, scalar):
        u"""\* opertaor with scalar only, for `dot` or `cross` see corresponding methods"""
        return self.__class__(self.x * scalar,  self.y * scalar, self.z * scalar)
    __rmul__ = __mul__

    def __imul__(self, scalar):
        u"""\*= opertaor with scalara only"""
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar
        return self

    def __len__(self):
        u"""always 3"""
        return 3

    def __div__(self, scalar):
        u"""/ opertaor, scalar only"""
        return self.__class__(self.x / scalar, self.y / scalar, self.z / scalar)

    def __idiv__(self, scalar):
        u"""/= opertaor, scalar only"""
        self.x /= scalar
        self.y /= scalar
        self.z /= scalar
        return self

    def __neg__(self):
        u"""- opertaor, same as -1 \* vec"""
        return self.__class__(-self.x, -self.y, -self.z)

    def __pos__(self):
        return self.__class__(abs(self.x), abs(self.y), abs(self.z))

    #-- comparison --#
    def __eq__(self, other):
        u""" == operator, vectors are equal when components are equal, might not 
        make much sense since using a tolerance would be better"""
        # TODO: allow compares with tuples / lists of same dim ??
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y and self.z == other.z
        return False

    def __neq__(self, other):
        u"""same as not __eq__"""
        return not self.__eq__(other)

    #-- items access --#
    def __getitem__(self, key):
        u"""[] operator, slow"""
        return (self.x, self.y, self.z)[key]

    def __iter__(self):
        u"""returns an iterator"""
        return iter((self.x, self.y, self.z))

    #-- additional methods --#
    def as_tuple(self):
        u"""returns a tuple, (x, y, z)"""
        return self.x, self.y, self.z

    def as_xy_tuple(self):
        u"""returns tuple (x, y), z is supressed"""
        return self.x, self.y

    def round(self, n_digits=3):
        u"""
        Round values to n_digits.
        
        :Parameters:
            n_digits : int
                Number of digits after the point.
        """
        self.x = round(self.x, n_digits)
        self.y = round(self.y, n_digits)
        self.z = round(self.z, n_digits)

    def rounded(self, n_digits=3):
        u"""
        Get a rounded vector.
        
        :Parameters:
            n_digits : int
                Number of digits after the point.
                
        :rtype: `Vec3`
        :Returns: `Vec3` rounded to n_digits
        """
        return self.__class__(round(self.x, n_digits), round(self.y, n_digits), round(self.z, n_digits))

    def normalize(self):
        u"""
        Make the vector unit length. May raise a ZeroDivisionError if length is 0.
        """
        leng = self.length
        self.x /= leng
        self.y /= leng
        self.z /= leng

    def clone(self):
        u"""
        Clone the vector.
        
        :rtype: `Vec3`
        :Returns: a copy of itself.
        """
        return self.__class__(self.x, self.y, self.z)

    def dot(self, other):
        u"""
        Dot product.
        
        :Parameters:
            other : `Vec3`
                Other vector.
        
        :rtype: float
        
        :Returns:
            self.dot(other)
        """
        assert isinstance(other, self.__class__)
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        u"""
        Cross product.
        
        :Parameters:
            other : `Vec3`
                The second vector for the cross product.
        
        :rtype: `Vec3`
        :Returns: vector resulting from the cross product.
        :Note: a.cross(b) == - b.cross(a)
        """
        assert isinstance(other, self.__class__)
        return self.__class__(self.y * other.z - self.z * other.y,
                              self.z * other.x - self.x * other.z,
                              self.x * other.y - self.y * other.x)

    def project_onto(self, other):
        u"""
        Project this vector onto another one.
        
        :Parameters:
            other : `Vec3`
                The other vector to project onto.
                
        :rtype: `Vec3`
        :Returns: The projected vector.
        """
        assert isinstance(other, self.__class__)
        return self.dot(other) / other.lengthSQ * other

    def reflect(self, normal):
        u"""
        Reflects this vector at a normal.
        
        :Parameters:
            normal : `Vec3`
                normal should be normalized unitlength
        
        :rtype: `Vec3`
        
        :Returns:
            Reflected vector.
        
        """
        assert isinstance(normal, self.__class__)
        return self - 2 * self.dot(normal) * normal

    def reflect_tangent(self, tangent):
        u"""
        Reflects vector at a tangent.
        
        :Parameters:
            tangent : `Vec3`
                tangent should be normalized, unitlength
        
        :rtype: `Vec3`
        
        :Returns:
            Reflected vector.
        """
        assert isinstance(tangent, self.__class__)
        return 2 * tangent.dot(self) * tangent - self

    def rotate(self, degrees, axis_vec3):
        u"""
        Rotates the vector around given axis.
        
        :Parameters:
            degrees : float
                angle in degrees
            axis_vec3 : `Vec3`
                axis to rotate around
        
        :rtype: `Vec3`
        
        :Returns: Rotated vector.
        
        :Note: see: http://www.cprogramming.com/tutorial/3d/rotation.html
        
        """
        assert isinstance(axis_vec3, self.__class__)
        #// http://www.cprogramming.com/tutorial/3d/rotation.html
        #  
        #//tXX + c  tXY + sZ  tXZ - sY  0
        #//tXY-sZ   tYY + c   tYZ + sX  0
        #//tXY + sY tYZ - sX  tZZ + c   0
        #//0        0         0         1
        #
        #//Where c = cos (theta), s = sin (theta), t = 1-cos (theta), and <X,Y,Z> is the unit vector representing the arbitary axis

        theta = degrees * PI_DIV_180
        c = cos(theta)
        s = sin(theta)
        t = 1 - c
        x, y, z = axis_vec3.normalized.as_tuple()
        xy = x * y
        yz = y * z
        sx = s * x
        sy = s * y
        sz = s * z
        
        _x = self.x
        _y = self.y
        _z = self.z
        
        return self.__class__((t * x * x + c) * _x + (t * xy + sz)   * _y + (t * x * z - sy) * _z,
                              (t * xy - sz)   * _x + (t * y * y + c) * _y + (t * yz + sx)   *  _z,
                              (t * xy + sy)   * _x + (t * yz - sx)   * _y + (t * z * z + c) *  _z)

    def get_angle_between(self, other):
        u"""
        Get angle between this and other vector.
        
        :Parameters:
            other : `Vec3`
                other vector
        
        :rtype: float
        
        :Returns:
            Angle in degrees.
        """
        assert isinstance(other, self.__class__)
        return  self.dot(other)/ (PI_DIV_180 * self.length * other.length)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    #-- 2D --#
    Vec = Vec2
    v = Vec(2, 2)
    w = Vec(3, 5)
    assert v == Vec(2, 2), u'equal failed'
    assert v + w == Vec(5, 7), u'add failed'
    assert w - v == Vec(1, 3), u'sub failed'
    assert 2 * v == Vec(4, 4), u'rmul failed'
    assert v * 3 == Vec(6, 6), u'mul failed'
    assert v.dot(w) == 16, u'dot failed'
    z = v.clone()
    z *= 4
    assert z == Vec(8, 8) , u'imul failed'
    assert z / 2 == Vec(4, 4), u'div failed'
    z /= 2
    assert z == Vec(4, 4), u'idiv failed'
    assert Vec(3, 4).length == 5, u'length failed'
    assert Vec(5, 2).lengthSQ == 29, u'lengsq failed'
    v += w
    assert v == Vec(5, 7), u'iadd failed'
    v -= w
    assert v == Vec(2, 2), u'isub failed'
    assert v.normal_L == Vec(-2, 2), u'normal_L failed'
    assert v.normal_R == Vec(2, -2), u'normal_R failed'
    assert v.normalized == v / v.length, u'normalized failed'
    n = v.normalized
    v.normalize()
    assert v == n, u'normalize failed'
    v = Vec(1, 0)
    n = Vec(1, -1).normalized
    r = v.rotated(-45).normalized
    assert round(r.x, 5) == round(n.x, 5) and round(r.y, 5) == round(n.y, 5), u'rotated failed'
    r = Vec(1, 0)
    r.rotate(-45)
    assert round(r.x, 5) == round(n.x, 5) and round(r.y, 5) == round(n.y, 5), u'rotate failed'
    assert Vec(1, 1).project_onto(Vec(1, 0)) == Vec(1, 0), u'project_onto failed'
    assert Vec(-1, 1).project_onto(Vec(0, 1)) == Vec(0, 1), u'project_onto failed'
    assert Vec(1, -1).reflect(Vec(0, 1)) == Vec(1, 1), u'reflect failed'
    assert Vec(1, -1).reflect_tangent(Vec(1, 0)) == Vec(1, 1), u'reflect_tangent failed'
    v = Vec(1, 1)
    w = Vec(3, 3)
    v.values = w
    w.x = 100
    w.y = 100
    assert v.x == 3, u'value for x failed'
    assert v.y == 3, u'value for y failed'
    v = Vec(2, 2)
    w = Vec(0, 2)
    assert v.cross(w) == 4
    assert w.cross(v) == -4
    v = Vec(1, 0)
    v.rotate(90)
    v.round(4)
    assert v == Vec(0.0, 1.0), u'rotate angle is wrong'
    v = Vec(1, 0)
    v.rotate(-90)
    v.round(5)
    assert v == Vec(0, -1), u'rotate -angle is wrong'
    assert Vec(1, 0).rotated(90).rounded(5) == Vec(0, 1), u'rotated angele is wrong'
    assert Vec(1, 0).rotated(-90).rounded(5) == Vec(0, -1), u'rotated -angele is wrong'
    assert Vec(1, 0).rotated(90).angle == 90, u'wrong angle'
    assert Vec(1, 0).rotated(-90).angle == 270, u'wrong -angle'
    v = Vec(1, 0)
    v.rotate_to(90)
    v.round(5)
    assert v == Vec(0, 1), u'wrong rotate_to angle'
    #-- 3D --#
    Vec = Vec3
    v = Vec(2, 2, 2)
    w = Vec(3, 5, 7)
    assert v == Vec(2, 2, 2), u'equal failed'
    assert v + w == Vec(5, 7, 9), u'add failed'
    assert w - v == Vec(1, 3, 5), u'sub failed'
    assert 2 * v == Vec(4, 4, 4), u'rmul failed'
    assert v * 3 == Vec(6, 6, 6), u'mul failed'
    assert v.dot(w) == 30, u'dot failed'
    z = v.clone()
    z *= 4
    assert z == Vec(8, 8, 8) , u'imul failed'
    assert z / 2 == Vec(4, 4, 4), u'div failed'
    z /= 2
    assert z == Vec(4, 4, 4), u'idiv failed'
    assert Vec(1, 1, 1).length == sqrt(3), u'length failed'
    assert Vec(1, 1, 1).lengthSQ == 3, u'lengsq failed'
    v += w
    assert v == Vec(5, 7, 9), u'iadd failed'
    v -= w
    assert v == Vec(2, 2, 2), u'isub failed'
    assert v.normalized == v / v.length, u'normalized failed'
    n = v.normalized
    v.normalize()
    assert v == n, u'normalize failed'
    assert Vec(1, 1, 0).project_onto(Vec(1, 0, 0)) == Vec(1, 0, 0), u'project_onto failed'
    assert Vec(-1, 1, 0).project_onto(Vec(0, 1, 0)) == Vec(0, 1, 0), u'project_onto failed'
    assert Vec(1, -1, 1).reflect(Vec(0, 1, 0)) == Vec(1, 1, 1), u'reflect failed'
    assert Vec(1, -1, 1).reflect_tangent(Vec(1, 0, 0)) == Vec(1, 1, -1), u'reflect_tangent failed'
    v = Vec(1, 1, 1)
    w = Vec(3, 3, 3)
    v.values = w
    w.x = 100
    w.y = 100
    assert v.x == 3, u'value for x failed'
    assert v.y == 3, u'value for y failed'
    assert v.z == 3, u'value for z failed'
    v = Vec(2, 2, 2)
    w = Vec(0, 2, 1)
    assert v.cross(w) == Vec(-2, -2, 4)
    assert w.cross(v) == -1 * Vec(-2, -2, 4)
    v = Vec(1, 0, 0)
#    for i in range(0, 300, 30):
#        print v.rotate(i, Vec(1, 1, 1)).rounded(5)
    assert v.rotate(90, Vec(0, 0, 1)).rounded(5) == Vec(0, 1, 0)
    assert v.rotate(90, Vec(0, 1, 0)).rounded(5) == Vec(0, 0, -1)
    assert v.rotate(240, Vec(1, 1, 1)).rounded(5) == Vec(0, 0, 1)
    assert v.rotate(-120, Vec(1, 1, 1)).rounded(5) == Vec(0, 0, 1)
    
#    v = Vec2(1, 1)
#    w = Vec3(1, 1, 1)
#    print v + w
#    print w + v
    
    raw_input(u'press any key to continue...')


if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))

