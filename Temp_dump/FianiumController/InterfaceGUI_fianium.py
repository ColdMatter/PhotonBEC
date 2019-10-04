#This is a horrific hack, but might work
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
		MainWindow.resize(250, 420)
		self.centralwidget = QtGui.QWidget(MainWindow)
		self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
		self.groupBox = QtGui.QGroupBox(self.centralwidget)
		self.groupBox.setGeometry(QtCore.QRect(0, 20, 260, 421))
		self.groupBox.setObjectName(_fromUtf8("groupBox"))

		self.enable_checkBox = QtGui.QCheckBox(self.groupBox)
		self.enable_checkBox.setGeometry(QtCore.QRect(50, 10, 101, 22))
		self.enable_checkBox.setObjectName(_fromUtf8("enable_checkBox"))

		self.power_timer_checkBox = QtGui.QCheckBox(self.groupBox)
		self.power_timer_checkBox.setGeometry(QtCore.QRect(155, 10, 101, 22))
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

		self.label_5 = QtGui.QLabel(self.groupBox)
		self.label_5.setGeometry(QtCore.QRect(190, 180, 31, 20))
		self.label_5.setObjectName(_fromUtf8("label_5"))

		self.label_6 = QtGui.QLabel(self.groupBox)
		self.label_6.setGeometry(QtCore.QRect(0, 70, 101, 17))
		self.label_6.setObjectName(_fromUtf8("label_6"))

		self.label_7 = QtGui.QLabel(self.groupBox)
		self.label_7.setGeometry(QtCore.QRect(0, 150, 101, 17))
		self.label_7.setObjectName(_fromUtf8("label_6"))

		self.label_8 = QtGui.QLabel(self.groupBox)
		self.label_8.setGeometry(QtCore.QRect(75, 280, 31, 27))
		self.label_8.setObjectName(_fromUtf8("label_7"))

		self.label_9 = QtGui.QLabel(self.groupBox)
		self.label_9.setGeometry(QtCore.QRect(205, 280, 31, 27))
		self.label_9.setObjectName(_fromUtf8("label_7"))


		self.currentLCD_pulse_energy = QtGui.QLCDNumber(self.groupBox)
		self.currentLCD_pulse_energy.setGeometry(QtCore.QRect(0, 90, 181, 51))
		self.currentLCD_pulse_energy.setObjectName(_fromUtf8("currentLCD_Energy"))

		self.currentLCD_rr = QtGui.QLCDNumber(self.groupBox)
		self.currentLCD_rr.setGeometry(QtCore.QRect(0, 170, 181, 51))
		self.currentLCD_rr.setObjectName(_fromUtf8("currentLCD_RepRate"))

		self.setLCD_pulse_energy = QtGui.QLCDNumber(self.groupBox)
		self.setLCD_pulse_energy.setGeometry(QtCore.QRect(20, 280, 51, 27))
		self.setLCD_pulse_energy.setObjectName(_fromUtf8("currentLCD_Energy"))

		self.currentLCD_alarms = QtGui.QTextEdit(self.groupBox)
		self.currentLCD_alarms.setGeometry(QtCore.QRect(20, 320,200, 51))
		self.currentLCD_alarms.setObjectName(_fromUtf8("LaserSafetyAlarms"))

		self.setLCD_rr = QtGui.QLCDNumber(self.groupBox)
		self.setLCD_rr.setGeometry(QtCore.QRect(150, 280, 51, 27))
		self.setLCD_rr.setObjectName(_fromUtf8("currentLCD_RepRate"))
		   

		self.setText_pulse_energy = QtGui.QLineEdit(self.groupBox)
		self.setText_pulse_energy.setGeometry(QtCore.QRect(20, 250, 51, 27))
		self.setText_pulse_energy.setObjectName(_fromUtf8("setText_Energy"))
		self.setTextButton_pulse_energy = QtGui.QPushButton(self.groupBox)
		self.setTextButton_pulse_energy.setGeometry(QtCore.QRect(75, 250, 31, 27))
		self.setTextButton_pulse_energy.setObjectName(_fromUtf8("setTextButton1"))

		self.setText_rr = QtGui.QLineEdit(self.groupBox)
		self.setText_rr.setGeometry(QtCore.QRect(150, 250, 51, 27))
		self.setText_rr.setObjectName(_fromUtf8("setText_RepRate"))
		self.setTextButton_rr = QtGui.QPushButton(self.groupBox)
		self.setTextButton_rr.setGeometry(QtCore.QRect(205, 250, 31, 27))
		self.setTextButton_rr.setObjectName(_fromUtf8("setTextButton2"))

		self.getDataPushButton = QtGui.QPushButton(self.groupBox)
		self.getDataPushButton.setGeometry(QtCore.QRect(150, 40, 61, 27))
		self.getDataPushButton.setObjectName(_fromUtf8("getEnergyPushButton"))


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
		MainWindow.move(screen.width() - mysize.width() - 275, 0)

		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

		
        #p=self.palette()
        #p.setColor(self.backgroundRole(),Qt.red)
        #self.setPalette(p)
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "FianiumController", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Power", None, QtGui.QApplication.UnicodeUTF8))
        self.enable_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Enable Output", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("MainWindow", "nJ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("MainWindow", "MHz", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("MainWindow", "Pulse Energy", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("MainWindow", "Repetition Rate", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("MainWindow", "nJ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("MainWindow", "MHz", None, QtGui.QApplication.UnicodeUTF8))
        self.setTextButton_pulse_energy.setText(QtGui.QApplication.translate("MainWindow", "Set", None, QtGui.QApplication.UnicodeUTF8))
        self.setTextButton_rr.setText(QtGui.QApplication.translate("MainWindow", "Set", None, QtGui.QApplication.UnicodeUTF8))
        self.getDataPushButton.setText(QtGui.QApplication.translate("MainWindow", "Get Data", None, QtGui.QApplication.UnicodeUTF8))
        self.power_timer_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Poll Power", None, QtGui.QApplication.UnicodeUTF8))

if __name__ == "__main__":
	import sys
	app = QtGui.QApplication(sys.argv)
	MainWindow = QtGui.QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	app_icon = QtGui.QIcon()
	app_icon.addFile('fianium_icon.png',QtCore.QSize(16,16))
	app.setWindowIcon(app_icon)
	MainWindow.show()
	sys.exit(app.exec_())

