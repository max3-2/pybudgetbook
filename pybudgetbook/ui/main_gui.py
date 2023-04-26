# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_gui.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit,
    QDateTimeEdit, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSlider, QSpacerItem, QStatusBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_pybb_MainWindow(object):
    def setupUi(self, pybb_MainWindow):
        if not pybb_MainWindow.objectName():
            pybb_MainWindow.setObjectName(u"pybb_MainWindow")
        pybb_MainWindow.resize(1500, 992)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(pybb_MainWindow.sizePolicy().hasHeightForWidth())
        pybb_MainWindow.setSizePolicy(sizePolicy)
        icon = QIcon()
        iconThemeName = u"applications-office"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)

        pybb_MainWindow.setWindowIcon(icon)
        pybb_MainWindow.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.actionMove_on_Save = QAction(pybb_MainWindow)
        self.actionMove_on_Save.setObjectName(u"actionMove_on_Save")
        self.actionUpdate_Groups = QAction(pybb_MainWindow)
        self.actionUpdate_Groups.setObjectName(u"actionUpdate_Groups")
        self.actionData_Directory = QAction(pybb_MainWindow)
        self.actionData_Directory.setObjectName(u"actionData_Directory")
        self.actionShow_Logger = QAction(pybb_MainWindow)
        self.actionShow_Logger.setObjectName(u"actionShow_Logger")
        self.actionAbout = QAction(pybb_MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.centralwidget = QWidget(pybb_MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.centralTabWidget = QTabWidget(self.centralwidget)
        self.centralTabWidget.setObjectName(u"centralTabWidget")
        self.tabWidgetPage1 = QWidget()
        self.tabWidgetPage1.setObjectName(u"tabWidgetPage1")
        self.horizontalLayout_3 = QHBoxLayout(self.tabWidgetPage1)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_tabWidgetPage1 = QGridLayout()
        self.gridLayout_tabWidgetPage1.setObjectName(u"gridLayout_tabWidgetPage1")
        self.gridLayout_tabWidgetPage1.setContentsMargins(4, 4, 6, 4)
        self.frame_plotReceipt = QFrame(self.tabWidgetPage1)
        self.frame_plotReceipt.setObjectName(u"frame_plotReceipt")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame_plotReceipt.sizePolicy().hasHeightForWidth())
        self.frame_plotReceipt.setSizePolicy(sizePolicy2)
        self.frame_plotReceipt.setMinimumSize(QSize(600, 700))
        self.frame_plotReceipt.setFrameShape(QFrame.StyledPanel)
        self.frame_plotReceipt.setFrameShadow(QFrame.Raised)

        self.gridLayout_tabWidgetPage1.addWidget(self.frame_plotReceipt, 2, 0, 2, 1)

        self.groupBox_inputControl = QGroupBox(self.tabWidgetPage1)
        self.groupBox_inputControl.setObjectName(u"groupBox_inputControl")
        sizePolicy1.setHeightForWidth(self.groupBox_inputControl.sizePolicy().hasHeightForWidth())
        self.groupBox_inputControl.setSizePolicy(sizePolicy1)
        self.groupBox_inputControl.setMinimumSize(QSize(0, 150))
        self.groupBox_inputControl.setFlat(True)
        self.groupBox_inputControl.setCheckable(False)
        self.horizontalLayout_7 = QHBoxLayout(self.groupBox_inputControl)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_inputControl = QGridLayout()
        self.gridLayout_inputControl.setObjectName(u"gridLayout_inputControl")
        self.label_receiptDisplayMode = QLabel(self.groupBox_inputControl)
        self.label_receiptDisplayMode.setObjectName(u"label_receiptDisplayMode")

        self.gridLayout_inputControl.addWidget(self.label_receiptDisplayMode, 1, 1, 1, 1)

        self.comboBox_receiptDisplayMode = QComboBox(self.groupBox_inputControl)
        self.comboBox_receiptDisplayMode.addItem("")
        self.comboBox_receiptDisplayMode.addItem("")
        self.comboBox_receiptDisplayMode.setObjectName(u"comboBox_receiptDisplayMode")

        self.gridLayout_inputControl.addWidget(self.comboBox_receiptDisplayMode, 2, 2, 1, 1)

        self.label_baseLang = QLabel(self.groupBox_inputControl)
        self.label_baseLang.setObjectName(u"label_baseLang")

        self.gridLayout_inputControl.addWidget(self.label_baseLang, 2, 1, 1, 1)

        self.comboBox_baseLang = QComboBox(self.groupBox_inputControl)
        self.comboBox_baseLang.setObjectName(u"comboBox_baseLang")

        self.gridLayout_inputControl.addWidget(self.comboBox_baseLang, 1, 2, 1, 1)

        self.labelFilterValue = QLabel(self.groupBox_inputControl)
        self.labelFilterValue.setObjectName(u"labelFilterValue")

        self.gridLayout_inputControl.addWidget(self.labelFilterValue, 2, 5, 1, 1)

        self.horizontalSliderFilterAmount = QSlider(self.groupBox_inputControl)
        self.horizontalSliderFilterAmount.setObjectName(u"horizontalSliderFilterAmount")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.horizontalSliderFilterAmount.sizePolicy().hasHeightForWidth())
        self.horizontalSliderFilterAmount.setSizePolicy(sizePolicy3)
        self.horizontalSliderFilterAmount.setMinimum(50)
        self.horizontalSliderFilterAmount.setMaximum(200)
        self.horizontalSliderFilterAmount.setSingleStep(5)
        self.horizontalSliderFilterAmount.setValue(80)
        self.horizontalSliderFilterAmount.setOrientation(Qt.Horizontal)
        self.horizontalSliderFilterAmount.setTickPosition(QSlider.NoTicks)

        self.gridLayout_inputControl.addWidget(self.horizontalSliderFilterAmount, 2, 3, 1, 2)

        self.pushButton_parseVendor = QPushButton(self.groupBox_inputControl)
        self.pushButton_parseVendor.setObjectName(u"pushButton_parseVendor")

        self.gridLayout_inputControl.addWidget(self.pushButton_parseVendor, 4, 4, 1, 2)

        self.horizontalSpacer = QSpacerItem(300, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout_inputControl.addItem(self.horizontalSpacer, 1, 3, 1, 3)

        self.pushButton_loadNewReceipt = QPushButton(self.groupBox_inputControl)
        self.pushButton_loadNewReceipt.setObjectName(u"pushButton_loadNewReceipt")

        self.gridLayout_inputControl.addWidget(self.pushButton_loadNewReceipt, 0, 2, 1, 4)


        self.horizontalLayout_7.addLayout(self.gridLayout_inputControl)


        self.gridLayout_tabWidgetPage1.addWidget(self.groupBox_inputControl, 0, 0, 2, 1)

        self.frame_dataDisplay = QFrame(self.tabWidgetPage1)
        self.frame_dataDisplay.setObjectName(u"frame_dataDisplay")
        sizePolicy4 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.frame_dataDisplay.sizePolicy().hasHeightForWidth())
        self.frame_dataDisplay.setSizePolicy(sizePolicy4)
        self.frame_dataDisplay.setMinimumSize(QSize(700, 0))
        self.frame_dataDisplay.setFrameShape(QFrame.StyledPanel)
        self.frame_dataDisplay.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_dataDisplay)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_dataDisplay = QVBoxLayout()
        self.verticalLayout_dataDisplay.setObjectName(u"verticalLayout_dataDisplay")
        self.verticalLayout_dataDisplay.setContentsMargins(0, 0, -1, -1)
        self.groupBox_additionalData = QGroupBox(self.frame_dataDisplay)
        self.groupBox_additionalData.setObjectName(u"groupBox_additionalData")
        self.groupBox_additionalData.setFlat(True)
        self.horizontalLayout_5 = QHBoxLayout(self.groupBox_additionalData)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_additionalData = QGridLayout()
        self.gridLayout_additionalData.setSpacing(5)
        self.gridLayout_additionalData.setObjectName(u"gridLayout_additionalData")
        self.gridLayout_additionalData.setContentsMargins(-1, 0, -1, 10)
        self.label_shopDate = QLabel(self.groupBox_additionalData)
        self.label_shopDate.setObjectName(u"label_shopDate")

        self.gridLayout_additionalData.addWidget(self.label_shopDate, 2, 0, 1, 1)

        self.lineEdit_marketVendor = QLineEdit(self.groupBox_additionalData)
        self.lineEdit_marketVendor.setObjectName(u"lineEdit_marketVendor")

        self.gridLayout_additionalData.addWidget(self.lineEdit_marketVendor, 0, 1, 1, 1)

        self.pushButton = QPushButton(self.groupBox_additionalData)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout_additionalData.addWidget(self.pushButton, 0, 2, 1, 1)

        self.label_overallCat = QLabel(self.groupBox_additionalData)
        self.label_overallCat.setObjectName(u"label_overallCat")

        self.gridLayout_additionalData.addWidget(self.label_overallCat, 1, 0, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_additionalData.addItem(self.horizontalSpacer_3, 4, 0, 1, 1)

        self.label_marketVendor = QLabel(self.groupBox_additionalData)
        self.label_marketVendor.setObjectName(u"label_marketVendor")

        self.gridLayout_additionalData.addWidget(self.label_marketVendor, 0, 0, 1, 1)

        self.pushButton_parseData = QPushButton(self.groupBox_additionalData)
        self.pushButton_parseData.setObjectName(u"pushButton_parseData")

        self.gridLayout_additionalData.addWidget(self.pushButton_parseData, 4, 2, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_additionalData.addItem(self.horizontalSpacer_2, 4, 1, 1, 1)

        self.comboBox_overalCat = QComboBox(self.groupBox_additionalData)
        self.comboBox_overalCat.setObjectName(u"comboBox_overalCat")

        self.gridLayout_additionalData.addWidget(self.comboBox_overalCat, 1, 1, 1, 1)

        self.dateEdit_shopDate = QDateEdit(self.groupBox_additionalData)
        self.dateEdit_shopDate.setObjectName(u"dateEdit_shopDate")
        self.dateEdit_shopDate.setDateTime(QDateTime(QDate(2023, 4, 14), QTime(13, 0, 0)))
        self.dateEdit_shopDate.setMaximumDateTime(QDateTime(QDate(2222, 12, 31), QTime(17, 59, 59)))
        self.dateEdit_shopDate.setMinimumDateTime(QDateTime(QDate(2000, 1, 1), QTime(19, 0, 0)))
        self.dateEdit_shopDate.setMinimumDate(QDate(2000, 1, 1))
        self.dateEdit_shopDate.setCurrentSection(QDateTimeEdit.DaySection)
        self.dateEdit_shopDate.setCalendarPopup(True)
        self.dateEdit_shopDate.setDate(QDate(2023, 4, 14))

        self.gridLayout_additionalData.addWidget(self.dateEdit_shopDate, 2, 1, 1, 1)


        self.horizontalLayout_5.addLayout(self.gridLayout_additionalData)


        self.verticalLayout_dataDisplay.addWidget(self.groupBox_additionalData)

        self.tableWidget_mainData = QTableWidget(self.frame_dataDisplay)
        self.tableWidget_mainData.setObjectName(u"tableWidget_mainData")

        self.verticalLayout_dataDisplay.addWidget(self.tableWidget_mainData)

        self.groupBox_saveReceipt = QGroupBox(self.frame_dataDisplay)
        self.groupBox_saveReceipt.setObjectName(u"groupBox_saveReceipt")
        font = QFont()
        font.setUnderline(False)
        self.groupBox_saveReceipt.setFont(font)
        self.groupBox_saveReceipt.setFlat(True)
        self.horizontalLayout_6 = QHBoxLayout(self.groupBox_saveReceipt)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_saveReceipt = QGridLayout()
        self.gridLayout_saveReceipt.setObjectName(u"gridLayout_saveReceipt")
        self.label_totalAmountReceipt = QLabel(self.groupBox_saveReceipt)
        self.label_totalAmountReceipt.setObjectName(u"label_totalAmountReceipt")

        self.gridLayout_saveReceipt.addWidget(self.label_totalAmountReceipt, 0, 0, 1, 1)

        self.checkBox_feedbackMatch = QCheckBox(self.groupBox_saveReceipt)
        self.checkBox_feedbackMatch.setObjectName(u"checkBox_feedbackMatch")

        self.gridLayout_saveReceipt.addWidget(self.checkBox_feedbackMatch, 0, 2, 1, 1)

        self.lineEdit_totalAmountReceipt = QLineEdit(self.groupBox_saveReceipt)
        self.lineEdit_totalAmountReceipt.setObjectName(u"lineEdit_totalAmountReceipt")
        sizePolicy5 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy5.setHorizontalStretch(100)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.lineEdit_totalAmountReceipt.sizePolicy().hasHeightForWidth())
        self.lineEdit_totalAmountReceipt.setSizePolicy(sizePolicy5)
        self.lineEdit_totalAmountReceipt.setMinimumSize(QSize(100, 0))

        self.gridLayout_saveReceipt.addWidget(self.lineEdit_totalAmountReceipt, 0, 1, 1, 1)

        self.label_totalAmountData = QLabel(self.groupBox_saveReceipt)
        self.label_totalAmountData.setObjectName(u"label_totalAmountData")

        self.gridLayout_saveReceipt.addWidget(self.label_totalAmountData, 1, 0, 1, 1)

        self.lineEdit_totalAmountData = QLineEdit(self.groupBox_saveReceipt)
        self.lineEdit_totalAmountData.setObjectName(u"lineEdit_totalAmountData")
        sizePolicy5.setHeightForWidth(self.lineEdit_totalAmountData.sizePolicy().hasHeightForWidth())
        self.lineEdit_totalAmountData.setSizePolicy(sizePolicy5)
        self.lineEdit_totalAmountData.setMinimumSize(QSize(100, 0))

        self.gridLayout_saveReceipt.addWidget(self.lineEdit_totalAmountData, 1, 1, 1, 1)

        self.pushButton_saveData = QPushButton(self.groupBox_saveReceipt)
        self.pushButton_saveData.setObjectName(u"pushButton_saveData")

        self.gridLayout_saveReceipt.addWidget(self.pushButton_saveData, 1, 3, 1, 1)


        self.horizontalLayout_6.addLayout(self.gridLayout_saveReceipt)


        self.verticalLayout_dataDisplay.addWidget(self.groupBox_saveReceipt)


        self.horizontalLayout_4.addLayout(self.verticalLayout_dataDisplay)


        self.gridLayout_tabWidgetPage1.addWidget(self.frame_dataDisplay, 0, 1, 4, 1)


        self.horizontalLayout_3.addLayout(self.gridLayout_tabWidgetPage1)

        self.centralTabWidget.addTab(self.tabWidgetPage1, "")
        self.tabWidgetPage2 = QWidget()
        self.tabWidgetPage2.setObjectName(u"tabWidgetPage2")
        self.horizontalLayout_2 = QHBoxLayout(self.tabWidgetPage2)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_tabWidgetPage2 = QGridLayout()
        self.gridLayout_tabWidgetPage2.setObjectName(u"gridLayout_tabWidgetPage2")
        self.gridLayout_tabWidgetPage2.setContentsMargins(4, 4, 6, 4)
        self.frame_dataAnalysis = QFrame(self.tabWidgetPage2)
        self.frame_dataAnalysis.setObjectName(u"frame_dataAnalysis")
        self.frame_dataAnalysis.setFrameShape(QFrame.StyledPanel)
        self.frame_dataAnalysis.setFrameShadow(QFrame.Raised)

        self.gridLayout_tabWidgetPage2.addWidget(self.frame_dataAnalysis, 0, 0, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout_tabWidgetPage2)

        self.centralTabWidget.addTab(self.tabWidgetPage2, "")

        self.horizontalLayout.addWidget(self.centralTabWidget)

        pybb_MainWindow.setCentralWidget(self.centralwidget)
        self.pybb_menubar = QMenuBar(pybb_MainWindow)
        self.pybb_menubar.setObjectName(u"pybb_menubar")
        self.pybb_menubar.setGeometry(QRect(0, 0, 1500, 24))
        self.menuFile = QMenu(self.pybb_menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.pybb_menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuFlags = QMenu(self.menuEdit)
        self.menuFlags.setObjectName(u"menuFlags")
        self.menuHelp = QMenu(self.pybb_menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        pybb_MainWindow.setMenuBar(self.pybb_menubar)
        self.statusbar = QStatusBar(pybb_MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        pybb_MainWindow.setStatusBar(self.statusbar)

        self.pybb_menubar.addAction(self.menuFile.menuAction())
        self.pybb_menubar.addAction(self.menuEdit.menuAction())
        self.pybb_menubar.addAction(self.menuHelp.menuAction())
        self.menuEdit.addAction(self.menuFlags.menuAction())
        self.menuEdit.addAction(self.actionData_Directory)
        self.menuFlags.addAction(self.actionMove_on_Save)
        self.menuFlags.addAction(self.actionUpdate_Groups)
        self.menuHelp.addAction(self.actionShow_Logger)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(pybb_MainWindow)

        self.centralTabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(pybb_MainWindow)
    # setupUi

    def retranslateUi(self, pybb_MainWindow):
        pybb_MainWindow.setWindowTitle(QCoreApplication.translate("pybb_MainWindow", u"PyBudgetBook", None))
        self.actionMove_on_Save.setText(QCoreApplication.translate("pybb_MainWindow", u"Move on Save", None))
        self.actionMove_on_Save.setProperty("flag_name", QCoreApplication.translate("pybb_MainWindow", u"see_code", None))
        self.actionUpdate_Groups.setText(QCoreApplication.translate("pybb_MainWindow", u"Update Groups", None))
        self.actionData_Directory.setText(QCoreApplication.translate("pybb_MainWindow", u"Data Directory", None))
        self.actionShow_Logger.setText(QCoreApplication.translate("pybb_MainWindow", u"Show Logger", None))
        self.actionAbout.setText(QCoreApplication.translate("pybb_MainWindow", u"About", None))
        self.groupBox_inputControl.setTitle(QCoreApplication.translate("pybb_MainWindow", u"Input control", None))
        self.label_receiptDisplayMode.setText(QCoreApplication.translate("pybb_MainWindow", u"Language:", None))
        self.comboBox_receiptDisplayMode.setItemText(0, QCoreApplication.translate("pybb_MainWindow", u"Original", None))
        self.comboBox_receiptDisplayMode.setItemText(1, QCoreApplication.translate("pybb_MainWindow", u"Filtered", None))

        self.label_baseLang.setText(QCoreApplication.translate("pybb_MainWindow", u"Show:", None))
        self.labelFilterValue.setText("")
        self.pushButton_parseVendor.setText(QCoreApplication.translate("pybb_MainWindow", u"Parse Vendor", None))
        self.pushButton_loadNewReceipt.setText(QCoreApplication.translate("pybb_MainWindow", u"Load Receipt", None))
        self.groupBox_additionalData.setTitle(QCoreApplication.translate("pybb_MainWindow", u"Receipt Data", None))
        self.label_shopDate.setText(QCoreApplication.translate("pybb_MainWindow", u"Date:", None))
        self.pushButton.setText(QCoreApplication.translate("pybb_MainWindow", u"Detect Vendor", None))
        self.label_overallCat.setText(QCoreApplication.translate("pybb_MainWindow", u"Overall Category:", None))
        self.label_marketVendor.setText(QCoreApplication.translate("pybb_MainWindow", u"Supermarket / Vendor:", None))
        self.pushButton_parseData.setText(QCoreApplication.translate("pybb_MainWindow", u"Parse Data", None))
        self.groupBox_saveReceipt.setTitle(QCoreApplication.translate("pybb_MainWindow", u"Save Receipt", None))
        self.label_totalAmountReceipt.setText(QCoreApplication.translate("pybb_MainWindow", u"Total amount extracted:", None))
        self.checkBox_feedbackMatch.setText(QCoreApplication.translate("pybb_MainWindow", u"Feedback matching data", None))
        self.label_totalAmountData.setText(QCoreApplication.translate("pybb_MainWindow", u"Difference to data sum:", None))
        self.pushButton_saveData.setText(QCoreApplication.translate("pybb_MainWindow", u"Save Data", None))
        self.centralTabWidget.setTabText(self.centralTabWidget.indexOf(self.tabWidgetPage1), QCoreApplication.translate("pybb_MainWindow", u"Add New Receipt", None))
        self.centralTabWidget.setTabText(self.centralTabWidget.indexOf(self.tabWidgetPage2), QCoreApplication.translate("pybb_MainWindow", u"Data Analysis", None))
        self.menuFile.setTitle(QCoreApplication.translate("pybb_MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("pybb_MainWindow", u"Edit", None))
        self.menuFlags.setTitle(QCoreApplication.translate("pybb_MainWindow", u"Flags", None))
        self.menuHelp.setTitle(QCoreApplication.translate("pybb_MainWindow", u"Help", None))
    # retranslateUi

