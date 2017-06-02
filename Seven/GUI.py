from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtOpenGL import *
from OpenGL.GL import *
from OpenGL.GLU import *
import json
import os
from World import *

class MyRender(QOpenGLWidget):
    def init_window(self, world):
        self._world = world

    def paintGL(self):
        super().paintGL()
        self._world.render()

    def initializeGL(self):
        super().initializeGL()
        w = self.width() / 2
        h = self.height() / 2
        glClearColor(1.0, 1.0, 1.0, 1.0) 
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()                    
        glOrtho(-w, w, -h, h, 0.0, -1.0)
        glEnable(GL_POINT_SMOOTH)
        glPointSize(6.0)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        w2 = w / 2
        h2 = h / 2
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()  
        glOrtho(-w2, w2, -h2, h2, 0.0, -1.0)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if Qt.RightButton == event.button():
            self._world.selection(event.pos())
        if Qt.LeftButton == event.button():
            self._start = event.pos()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if event.buttons() == Qt.LeftButton:
            detal = event.pos() - self._start
            self._start = event.pos()
            self._world.move_selected(detal)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Plus:
            self._world.rotate_selected(True)
        elif event.key() == Qt.Key_Minus:
            self._world.rotate_selected(False)
        elif event.key() == Qt.Key_Equal:
            self._world.relect_selected()

class MyGui(QMainWindow):
    def init_gui(self):
        with open('setting.json') as file:
            self._setting = json.load(file)
        with open('language' + os.sep + self._setting['language'] + '.json') as file:
            self._language = json.load(file)
        self.resize(self._setting['size'], self._setting['size'])
        self._world = World()
        self._init_menu()
        self._init_render_widget()    
        self.setWindowTitle(self._getlanguage('title')) 
        self.setWindowIcon(QIcon('icon.jpg'))

    def _init_menu(self):
        setting_menu = QMenu(self._getlanguage('setting'), self)
        self.menuBar().addMenu(setting_menu)
        reset_action = QAction(self._getlanguage('reset'), setting_menu)
        reset_action.triggered.connect(self.reset_world)
        setting_menu.addAction(reset_action)
        resize_action = QAction(self._getlanguage('resize'), setting_menu)
        resize_action.triggered.connect(self.resize_world)
        setting_menu.addAction(resize_action)
        export_action = QAction(self._getlanguage('export'), setting_menu)
        export_action.triggered.connect(self.export_png)
        setting_menu.addAction(export_action)
        setting_menu.addSeparator()
        open_action = QAction(self._getlanguage('open'), setting_menu)
        open_action.triggered.connect(self.open_file)
        setting_menu.addAction(open_action)
        save_action = QAction(self._getlanguage('save'), setting_menu)
        save_action.triggered.connect(self.save_file)
        setting_menu.addAction(save_action)

    def _init_render_widget(self):
        scroll = QScrollArea()
        self.setCentralWidget(scroll)
        '''create render widget'''
        render = MyRender()
        size = self._setting['size']
        render.setFixedSize(size, size)
        render.init_window(self._world)
        self._world.init_world(size, render)
        self._world.start()
        scroll.setWidget(render)
        render.setFocusPolicy(Qt.ClickFocus)
        self._render = render

    def _getlanguage(self, str):
        if str in self._language:
            return self._language[str]
        return "错误字符"

    def reset_world(self):
        self._world.reset()

    def resize_world(self):
        result = QInputDialog.getInt(self, self._getlanguage('ask_size'), self._getlanguage('size'), self._render.width(), 200)
        if result[1]:
            self._render.setFixedSize(result[0], result[0])
            self._world.resize(result[0])

    def export_png(self):
        self._world.clear_selected()
        result = QInputDialog.getText(self, self._getlanguage('ask_name'), self._getlanguage('name'), text = 'image')
        if not result[1]:
            return
        if self._render.grab().save(result[0] + '.png'):
            QMessageBox(QMessageBox.Information, self._getlanguage('info'), \
                self._getlanguage('save_success')).exec()
        else:
            QMessageBox(QMessageBox.Information, self._getlanguage('info'), \
                self._getlanguage('save_failed')).exec()

    def save_file(self):
        result = QInputDialog.getText(self, self._getlanguage('ask_name'), self._getlanguage('name'), text = 'world')
        if not result[1]:
            return
        if self._world.save_world(result[0]):
            QMessageBox(QMessageBox.Information, self._getlanguage('info'), \
                self._getlanguage('save_success')).exec()
        else:
            QMessageBox(QMessageBox.Information, self._getlanguage('info'), \
                self._getlanguage('save_failed')).exec()

    def open_file(self):
        result = QFileDialog.getOpenFileUrl(self, filter='*.seven')
        if not result[1]:
            return
        url = result[0]
        if url.isEmpty():
            return
        if self._world.open_world(url.path()[1:]):
             QMessageBox(QMessageBox.Information, self._getlanguage('info'), \
                self._getlanguage('open_success')).exec()
        else:
            QMessageBox(QMessageBox.Information, self._getlanguage('info'), \
                self._getlanguage('open_failed')).exec()

    def closeEvent(self, event):
        super().closeEvent(event)
        self._setting['size']  = self._render.width()
        with open('setting.json', 'w') as f:
            json.dump(self._setting, f)