# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'InterfaceGUI.ui'
#
# Created: Mon Mar 11 15:56:47 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

try:
	from PyQt4 import QtCore, QtGui
except:
	from PySide import QtCore, QtGui
	
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(240, 200)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 241, 381))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.powerSlider = QtGui.QSlider(self.groupBox)
        self.powerSlider.setGeometry(QtCore.QRect(0, 150, 141, 29))
        self.powerSlider.setMaximum(2400)
        self.powerSlider.setOrientation(QtCore.Qt.Horizontal)
        self.powerSlider.setObjectName(_fromUtf8("powerSlider"))
        self.enable_checkBox = QtGui.QCheckBox(self.groupBox)
        self.enable_checkBox.setGeometry(QtCore.QRect(50, 0, 101, 22))
        self.enable_checkBox.setObjectName(_fromUtf8("enable_checkBox"))
		
        self.power_timer_checkBox = QtGui.QCheckBox(self.groupBox)
        self.power_timer_checkBox.setGeometry(QtCore.QRect(155, 0, 101, 22))
        self.power_timer_checkBox.setObjectName(_fromUtf8("timer_checkBox"))
		
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(0, 50, 101, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(189, 50, 51, 20))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(190, 100, 31, 20))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(0, 130, 101, 17))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.currentLCD = QtGui.QLCDNumber(self.groupBox)
        self.currentLCD.setGeometry(QtCore.QRect(0, 70, 181, 51))
        self.currentLCD.setObjectName(_fromUtf8("currentLCD"))
        self.setLCD = QtGui.QLCDNumber(self.groupBox)
        self.setLCD.setGeometry(QtCore.QRect(190, 70, 51, 23))
        self.setLCD.setNumDigits(4)
        self.setLCD.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.setLCD.setObjectName(_fromUtf8("setLCD"))
        self.setText = QtGui.QLineEdit(self.groupBox)
        self.setText.setGeometry(QtCore.QRect(160, 150, 51, 27))
        self.setText.setObjectName(_fromUtf8("setText"))
        self.setTextButton = QtGui.QPushButton(self.groupBox)
        self.setTextButton.setGeometry(QtCore.QRect(210, 150, 31, 27))
        self.setTextButton.setObjectName(_fromUtf8("setTextButton"))
        self.getPowerPushButton = QtGui.QPushButton(self.groupBox)
        self.getPowerPushButton.setGeometry(QtCore.QRect(100, 40, 61, 27))
        self.getPowerPushButton.setObjectName(_fromUtf8("getPowerPushButton"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 240, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
		
	screen = QtGui.QDesktopWidget().screenGeometry()
	mysize = MainWindow.geometry()
	MainWindow.move(screen.width() - mysize.width() - 15, 0)
		
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "LaserController", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Power", None, QtGui.QApplication.UnicodeUTF8))
        self.enable_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Enable Output", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Current Value", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Set Value", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("MainWindow", "mW", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("MainWindow", "Controls", None, QtGui.QApplication.UnicodeUTF8))
        self.setTextButton.setText(QtGui.QApplication.translate("MainWindow", "Set", None, QtGui.QApplication.UnicodeUTF8))
        self.getPowerPushButton.setText(QtGui.QApplication.translate("MainWindow", "GetPower", None, QtGui.QApplication.UnicodeUTF8))
        self.power_timer_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Poll Power", None, QtGui.QApplication.UnicodeUTF8))

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

