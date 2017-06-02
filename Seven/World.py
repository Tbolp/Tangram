from PyQt5.QtCore import *
from PyQt5.QtGui import QVector2D
from PyQt5.QtGui import QColor
from OpenGL.GL import *
from OpenGL.GLU import *
import time
import math
import json

QVector2D.list = lambda x : [x.x(), x.y()]
QVector2D.list3 = lambda x : [x.x(), x.y(), 0]
QColor.list = lambda x : [x.redF(), x.greenF(), x.blueF()]

class World(QThread):
    def init_world(self, length, widget):
        self._shapes = []
        self._parallelogram = None
        self._widget = widget
        self._length = length
        self.init_position()

    def init_position(self):
        shape = Shape(QColor('#5AB25B').list(), (0, 0), (-100, 100), (-100, -100))
        self._shapes.append(shape)
        shape = Shape(QColor('#E96556').list(), (0, 0), (-100, -100), (100, -100))
        self._shapes.append(shape)
        shape = Shape(QColor('#46C8F9').list(), (-100, 100), (-50, 50), (0, 100))
        self._shapes.append(shape)
        shape = Shape(QColor('#EAD001').list(), (0, 100), (-50, 50), (0, 0), (50, 50))
        self._shapes.append(shape)
        shape = Shape(QColor('#FD9CBD').list(), (0, 0), (50, -50), (50, 50))
        self._shapes.append(shape)
        shape = ParalleLogram(QColor('#C7458F').list(), (50, 50), (50, -50), (100, -100), (100, 0))
        self._shapes.append(shape)
        shape = Shape(QColor('#D6444F').list(), (0, 100), (100, 0), (100, 100))
        self._shapes.append(shape)
        for i in self._shapes:
            if i.__class__.__name__ == 'ParalleLogram':
                self._parallelogram = i

    def run(self):
        interval = 0
        consume = 0
        timer = 0
        while True:  
            interval = time.clock() - timer
            timer = time.clock()
            self._widget.update()
            consume = time.clock() - timer
            if consume < 0.3:
                time.sleep(0.3)

    def render(self):
        '''call shapes render function'''
        for i in self._shapes:
            i.render()
        glFlush()

    def selection(self, point):
        '''select shape'''
        for i in reversed(self._shapes):
            if i.is_in(QVector2D(point.x() - self._length / 2, self._length / 2 - point.y())):
                i.toggle_selected()
                if i.selected:
                    self._shapes.remove(i)
                    self._shapes.append(i)
                break
        self._widget.update()

    def move_selected(self, detal):
        '''move selected shapes'''
        selected = []
        for i in self._shapes:
            if i.selected:
                selected.append(i)
        for i in selected:
            i.move(QVector2D(detal.x(), -detal.y()))
        self._widget.update()

    def rotate_selected(self, direction):
        '''rotate shape'''
        selected = []
        for i in self._shapes:
            if i.selected:
                selected.append(i)
        for i in selected:
            i.rotate(direction)
        self._widget.update()

    def reset(self):
        self._shapes = []
        self.init_position()
        self._widget.update()

    def resize(self, size):
        self._length = size
        self.clear_selected()

    def clear_selected(self):
        for i in self._shapes:
            if i.selected:
                i.toggle_selected()

    def relect_selected(self):
        if self._parallelogram.selected:
            self._parallelogram.reflect()

    def save_world(self, name):
        data = {}
        for i in range(len(self._shapes)):
            data[i] = []
            shape = self._shapes[i]
            data[i].append(list(shape.color))
            #data[i].append(shape.position.list())
            for j in shape._points:
                data[i].append(j.list())
            if shape.__class__.__name__ == 'ParalleLogram':
                data['s'] = i
        try:
            with open(name+'.seven', 'w') as f:
                json.dump(data, f)
        except:
            return False
        return True

    def open_world(self, path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                if self._creat_world(data):
                    return True
                return False
        except:
            return False

    def _creat_world(self, data):
        s = data['s']
        del data['s']
        shapes = []
        paralle = None
        try:
            for key, value in data.items():
                if key == str(s):
                    p = ParalleLogram(value[0], *value[1:])
                    shapes.append(p)
                    paralle = p
                else:
                    shapes.append(Shape(value[0], *value[1:]))
        except:
            return False
        self._shapes = shapes
        self._parallelogram = paralle
        return True


class Shape(object):
    @property
    def selected(self):
        return self._selected

    @property 
    def color(self):
        return self._color

    @property 
    def position(self):
        return self._position

    @property 
    def points(self):
        return self._points

    def __init__(self, color, *args):
        super().__init__()
        self._points = []
        self._color = color
        for i in args:
            vec = QVector2D(i[0], i[1]) 
            self._points.append(vec)
        sum = QVector2D(0, 0)
        for i in self._points:
            sum = sum + i
        self._position = sum*1.0/len(self._points)
        self._selected = False

    def toggle_selected(self):
        self._selected = not self._selected

    def render(self):
        glColor3f(*self._color)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glPolygonMode(GL_FRONT, GL_FILL)
        glBegin(GL_POLYGON)
        for i in self._points:
            glVertex3f(*i.list3())
        glEnd()
        if self._selected:
            glColor3f(0, 0, 0)
            glPolygonMode(GL_FRONT, GL_LINE)
            glBegin(GL_LINE_LOOP)
            for i in self._points:
                glVertex3f(*i.list3())
            glEnd()
            glBegin(GL_POINTS)
            glVertex3f(*self._position.list3())
            glEnd()

    def is_in(self, point):
        '''judge point is in shape'''
        for i in range(len(self._points)):
            if i == len(self._points)-1:
                j = 0
            else:
                j = i + 1
            res = is_intersection(point.list(), self._position.list(), \
                self._points[i].list(), self._points[j].list())
            if res:
                return False
        return True

    def move(self, detal):
        points = []
        for i in self._points:
            points.append(i + detal)
        self._points = points
        self._position = self._position + detal

    def rotate(self, direction):
        theta = -2.0/360.0
        points = []
        a = QVector2D(math.cos(theta), -math.sin(theta))
        b = QVector2D(math.sin(theta), math.cos(theta))
        c = QVector2D(math.cos(-theta), -math.sin(-theta))
        d = QVector2D(math.sin(-theta), math.cos(-theta))
        if direction:
            for i in self._points:
                 x = QVector2D.dotProduct(i-self._position, a)
                 y = QVector2D.dotProduct(i-self._position, b)
                 points.append(QVector2D(x, y)+self._position)
            self._points = points
        else:
            for i in self._points:
                 x = QVector2D.dotProduct(i-self._position, c)
                 y = QVector2D.dotProduct(i-self._position, d)
                 points.append(QVector2D(x, y)+self._position)
            self._points = points

class ParalleLogram(Shape):
    def reflect(self):
        a = self._points[0] - self._position
        b = self._points[2] - self._position
        c = (a - b).normalized()
        a = self._points[1] - self._position
        b = self._points[3] - self._position
        a = 2*QVector2D.dotProduct(a, c)*c - a
        b = 2*QVector2D.dotProduct(b, c)*c - b
        self._points[1] = a + self._position
        self._points[3] = b + self._position

def is_intersection(p1, p2, p3, p4):
    '''judge line intersection'''
    a1 = p2[1] - p1[1]
    b1 = p1[0] - p2[0]
    c1 = (p2[0] * p1[1]) - (p1[0] * p2[1])
    d1 = a1 * p3[0] + b1 * p3[1] + c1
    d2 = a1 * p4[0] + b1 * p4[1] + c1
    if d1 > 0 and d2 > 0:
        return False
    if d1 < 0 and d2 < 0:
        return False
    a2 = p4[1] - p3[1]
    b2 = p3[0] - p4[0]
    c2 = (p4[0] * p3[1]) - (p3[0] * p4[1])
    d1 = a2 * p1[0] + b2 * p1[1] + c2
    d2 = a2 * p2[0] + b2 * p2[1] + c2
    if d1 > 0 and d2 > 0:
        return False
    if d1 < 0 and d2 < 0:
        return False
    return True
