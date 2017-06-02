from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtOpenGL import *
from GUI import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

if __name__ =='__main__':
    app = QApplication(sys.argv)

    gui = MyGui()
    gui.init_gui()
    gui.show()

    sys.exit(app.exec())