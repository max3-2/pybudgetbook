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
    QMainWindow, QMenu, QMenuBar, QSizePolicy,
    QSpacerItem, QSplitter, QTabWidget, QVBoxLayout,
    QWidget)

from .ui_support import (ColoredStatusBar, ModernButton, PandasViewer, SliderWithVal)

class Ui_pybb_MainWindow(object):
    def setupUi(self, pybb_MainWindow):
        if not pybb_MainWindow.objectName():
            pybb_MainWindow.setObjectName(u"pybb_MainWindow")
        pybb_MainWindow.resize(1392, 800)
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
        self.actionMove_on_Save.setCheckable(True)
        self.actionLogger_debug = QAction(pybb_MainWindow)
        self.actionLogger_debug.setObjectName(u"actionLogger_debug")
        self.actionLogger_debug.setCheckable(True)
        self.actionData_Directory = QAction(pybb_MainWindow)
        self.actionData_Directory.setObjectName(u"actionData_Directory")
        self.actionShow_Logger = QAction(pybb_MainWindow)
        self.actionShow_Logger.setObjectName(u"actionShow_Logger")
        self.actionAbout = QAction(pybb_MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionRaw_Text = QAction(pybb_MainWindow)
        self.actionRaw_Text.setObjectName(u"actionRaw_Text")
        self.actionDefault_Language = QAction(pybb_MainWindow)
        self.actionDefault_Language.setObjectName(u"actionDefault_Language")
        self.actionLogger_Popup_Level = QAction(pybb_MainWindow)
        self.actionLogger_Popup_Level.setObjectName(u"actionLogger_Popup_Level")
        self.actionAlways_Ask_for_Image = QAction(pybb_MainWindow)
        self.actionAlways_Ask_for_Image.setObjectName(u"actionAlways_Ask_for_Image")
        self.actionAlways_Ask_for_Image.setCheckable(True)
        self.actionGenerate_Unique_Name = QAction(pybb_MainWindow)
        self.actionGenerate_Unique_Name.setObjectName(u"actionGenerate_Unique_Name")
        self.actionGenerate_Unique_Name.setCheckable(True)
        self.actionShow_Logger_on_Start = QAction(pybb_MainWindow)
        self.actionShow_Logger_on_Start.setObjectName(u"actionShow_Logger_on_Start")
        self.actionShow_Logger_on_Start.setCheckable(True)
        self.actionExport_to_CSV = QAction(pybb_MainWindow)
        self.actionExport_to_CSV.setObjectName(u"actionExport_to_CSV")
        self.actionCreate_data_backup = QAction(pybb_MainWindow)
        self.actionCreate_data_backup.setObjectName(u"actionCreate_data_backup")
        self.actionCurrency = QAction(pybb_MainWindow)
        self.actionCurrency.setObjectName(u"actionCurrency")
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
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(4, 4, 6, 4)
        self.frame_buttonsMainLeft = QFrame(self.tabWidgetPage1)
        self.frame_buttonsMainLeft.setObjectName(u"frame_buttonsMainLeft")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame_buttonsMainLeft.sizePolicy().hasHeightForWidth())
        self.frame_buttonsMainLeft.setSizePolicy(sizePolicy2)
        self.frame_buttonsMainLeft.setMinimumSize(QSize(90, 0))
        self.frame_buttonsMainLeft.setFrameShape(QFrame.NoFrame)
        self.frame_buttonsMainLeft.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_buttonsMainLeft)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.modernButton_loadReceipt = ModernButton(self.frame_buttonsMainLeft)
        self.modernButton_loadReceipt.setObjectName(u"modernButton_loadReceipt")
        self.modernButton_loadReceipt.setMinimumSize(QSize(70, 70))

        self.verticalLayout_2.addWidget(self.modernButton_loadReceipt)

        self.label_receiptDisplayMode = QLabel(self.frame_buttonsMainLeft)
        self.label_receiptDisplayMode.setObjectName(u"label_receiptDisplayMode")
        font = QFont()
        font.setUnderline(True)
        self.label_receiptDisplayMode.setFont(font)

        self.verticalLayout_2.addWidget(self.label_receiptDisplayMode)

        self.comboBox_baseLang = QComboBox(self.frame_buttonsMainLeft)
        self.comboBox_baseLang.setObjectName(u"comboBox_baseLang")

        self.verticalLayout_2.addWidget(self.comboBox_baseLang)

        self.label_baseLang = QLabel(self.frame_buttonsMainLeft)
        self.label_baseLang.setObjectName(u"label_baseLang")
        self.label_baseLang.setFont(font)

        self.verticalLayout_2.addWidget(self.label_baseLang)

        self.comboBox_receiptDisplayMode = QComboBox(self.frame_buttonsMainLeft)
        self.comboBox_receiptDisplayMode.addItem("")
        self.comboBox_receiptDisplayMode.addItem("")
        self.comboBox_receiptDisplayMode.setObjectName(u"comboBox_receiptDisplayMode")

        self.verticalLayout_2.addWidget(self.comboBox_receiptDisplayMode)

        self.label_filterSlider = QLabel(self.frame_buttonsMainLeft)
        self.label_filterSlider.setObjectName(u"label_filterSlider")
        self.label_filterSlider.setFont(font)

        self.verticalLayout_2.addWidget(self.label_filterSlider)

        self.slider_FilterAmount = SliderWithVal(self.frame_buttonsMainLeft)
        self.slider_FilterAmount.setObjectName(u"slider_FilterAmount")
        sizePolicy.setHeightForWidth(self.slider_FilterAmount.sizePolicy().hasHeightForWidth())
        self.slider_FilterAmount.setSizePolicy(sizePolicy)
        self.slider_FilterAmount.setMinimumSize(QSize(0, 200))
        self.slider_FilterAmount.setOrientation(Qt.Vertical)

        self.verticalLayout_2.addWidget(self.slider_FilterAmount)


        self.horizontalLayout_3.addWidget(self.frame_buttonsMainLeft)

        self.splitter_mainPage = QSplitter(self.tabWidgetPage1)
        self.splitter_mainPage.setObjectName(u"splitter_mainPage")
        self.splitter_mainPage.setOrientation(Qt.Horizontal)
        self.splitter_mainPage.setHandleWidth(9)
        self.frame_recDisplay = QFrame(self.splitter_mainPage)
        self.frame_recDisplay.setObjectName(u"frame_recDisplay")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame_recDisplay.sizePolicy().hasHeightForWidth())
        self.frame_recDisplay.setSizePolicy(sizePolicy3)
        self.frame_recDisplay.setFrameShape(QFrame.NoFrame)
        self.frame_recDisplay.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_recDisplay)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_recDisplay = QVBoxLayout()
        self.verticalLayout_recDisplay.setSpacing(0)
        self.verticalLayout_recDisplay.setObjectName(u"verticalLayout_recDisplay")
        self.verticalLayout_recDisplay.setContentsMargins(0, 0, 0, 0)
        self.frame_plotReceipt = QFrame(self.frame_recDisplay)
        self.frame_plotReceipt.setObjectName(u"frame_plotReceipt")
        sizePolicy3.setHeightForWidth(self.frame_plotReceipt.sizePolicy().hasHeightForWidth())
        self.frame_plotReceipt.setSizePolicy(sizePolicy3)
        self.frame_plotReceipt.setMinimumSize(QSize(0, 0))
        self.frame_plotReceipt.setFrameShape(QFrame.StyledPanel)
        self.frame_plotReceipt.setFrameShadow(QFrame.Raised)

        self.verticalLayout_recDisplay.addWidget(self.frame_plotReceipt)


        self.horizontalLayout_8.addLayout(self.verticalLayout_recDisplay)

        self.splitter_mainPage.addWidget(self.frame_recDisplay)
        self.frame_dataDisplay = QFrame(self.splitter_mainPage)
        self.frame_dataDisplay.setObjectName(u"frame_dataDisplay")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.frame_dataDisplay.sizePolicy().hasHeightForWidth())
        self.frame_dataDisplay.setSizePolicy(sizePolicy4)
        self.frame_dataDisplay.setMinimumSize(QSize(650, 0))
        self.frame_dataDisplay.setFrameShape(QFrame.NoFrame)
        self.frame_dataDisplay.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_dataDisplay)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_dataDisplay = QVBoxLayout()
        self.verticalLayout_dataDisplay.setSpacing(0)
        self.verticalLayout_dataDisplay.setObjectName(u"verticalLayout_dataDisplay")
        self.verticalLayout_dataDisplay.setContentsMargins(0, 0, -1, -1)
        self.groupBox_additionalData = QGroupBox(self.frame_dataDisplay)
        self.groupBox_additionalData.setObjectName(u"groupBox_additionalData")
        sizePolicy5 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.groupBox_additionalData.sizePolicy().hasHeightForWidth())
        self.groupBox_additionalData.setSizePolicy(sizePolicy5)
        self.groupBox_additionalData.setFlat(False)
        self.horizontalLayout_5 = QHBoxLayout(self.groupBox_additionalData)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_additionalData = QGridLayout()
        self.gridLayout_additionalData.setSpacing(5)
        self.gridLayout_additionalData.setObjectName(u"gridLayout_additionalData")
        self.gridLayout_additionalData.setContentsMargins(-1, 0, -1, 5)
        self.comboBox_overalCat = QComboBox(self.groupBox_additionalData)
        self.comboBox_overalCat.setObjectName(u"comboBox_overalCat")

        self.gridLayout_additionalData.addWidget(self.comboBox_overalCat, 1, 2, 1, 1)

        self.checkBox_useDiffParsingLang = QCheckBox(self.groupBox_additionalData)
        self.checkBox_useDiffParsingLang.setObjectName(u"checkBox_useDiffParsingLang")

        self.gridLayout_additionalData.addWidget(self.checkBox_useDiffParsingLang, 4, 1, 1, 1)

        self.lineEdit_marketVendor = QLineEdit(self.groupBox_additionalData)
        self.lineEdit_marketVendor.setObjectName(u"lineEdit_marketVendor")

        self.gridLayout_additionalData.addWidget(self.lineEdit_marketVendor, 0, 2, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_additionalData.addItem(self.horizontalSpacer_3, 4, 0, 1, 1)

        self.label_overallCat = QLabel(self.groupBox_additionalData)
        self.label_overallCat.setObjectName(u"label_overallCat")

        self.gridLayout_additionalData.addWidget(self.label_overallCat, 1, 1, 1, 1)

        self.comboBox_diffParsingLang = QComboBox(self.groupBox_additionalData)
        self.comboBox_diffParsingLang.setObjectName(u"comboBox_diffParsingLang")
        self.comboBox_diffParsingLang.setEnabled(False)

        self.gridLayout_additionalData.addWidget(self.comboBox_diffParsingLang, 4, 2, 1, 1)

        self.dateEdit_shopDate = QDateEdit(self.groupBox_additionalData)
        self.dateEdit_shopDate.setObjectName(u"dateEdit_shopDate")
        self.dateEdit_shopDate.setDateTime(QDateTime(QDate(2023, 4, 14), QTime(13, 0, 0)))
        self.dateEdit_shopDate.setMaximumDateTime(QDateTime(QDate(2222, 12, 30), QTime(5, 59, 59)))
        self.dateEdit_shopDate.setMinimumDateTime(QDateTime(QDate(2000, 1, 1), QTime(7, 0, 0)))
        self.dateEdit_shopDate.setMinimumDate(QDate(2000, 1, 1))
        self.dateEdit_shopDate.setCurrentSection(QDateTimeEdit.DaySection)
        self.dateEdit_shopDate.setCalendarPopup(True)
        self.dateEdit_shopDate.setDate(QDate(2023, 4, 14))

        self.gridLayout_additionalData.addWidget(self.dateEdit_shopDate, 2, 2, 1, 1)

        self.label_marketVendor = QLabel(self.groupBox_additionalData)
        self.label_marketVendor.setObjectName(u"label_marketVendor")

        self.gridLayout_additionalData.addWidget(self.label_marketVendor, 0, 1, 1, 1)

        self.label_shopDate = QLabel(self.groupBox_additionalData)
        self.label_shopDate.setObjectName(u"label_shopDate")

        self.gridLayout_additionalData.addWidget(self.label_shopDate, 2, 1, 1, 1)


        self.horizontalLayout_5.addLayout(self.gridLayout_additionalData)


        self.verticalLayout_dataDisplay.addWidget(self.groupBox_additionalData)

        self.tableView_pandasViewer = PandasViewer(self.frame_dataDisplay)
        self.tableView_pandasViewer.setObjectName(u"tableView_pandasViewer")

        self.verticalLayout_dataDisplay.addWidget(self.tableView_pandasViewer)

        self.groupBox_saveReceipt = QGroupBox(self.frame_dataDisplay)
        self.groupBox_saveReceipt.setObjectName(u"groupBox_saveReceipt")
        sizePolicy5.setHeightForWidth(self.groupBox_saveReceipt.sizePolicy().hasHeightForWidth())
        self.groupBox_saveReceipt.setSizePolicy(sizePolicy5)
        font1 = QFont()
        font1.setBold(False)
        font1.setUnderline(False)
        self.groupBox_saveReceipt.setFont(font1)
        self.groupBox_saveReceipt.setFlat(False)
        self.horizontalLayout_6 = QHBoxLayout(self.groupBox_saveReceipt)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_saveReceipt = QGridLayout()
        self.gridLayout_saveReceipt.setObjectName(u"gridLayout_saveReceipt")
        self.label_totalAmountReceipt = QLabel(self.groupBox_saveReceipt)
        self.label_totalAmountReceipt.setObjectName(u"label_totalAmountReceipt")

        self.gridLayout_saveReceipt.addWidget(self.label_totalAmountReceipt, 0, 0, 1, 1)

        self.lineEdit_totalAmountReceipt = QLineEdit(self.groupBox_saveReceipt)
        self.lineEdit_totalAmountReceipt.setObjectName(u"lineEdit_totalAmountReceipt")
        sizePolicy6 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy6.setHorizontalStretch(100)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.lineEdit_totalAmountReceipt.sizePolicy().hasHeightForWidth())
        self.lineEdit_totalAmountReceipt.setSizePolicy(sizePolicy6)
        self.lineEdit_totalAmountReceipt.setMinimumSize(QSize(100, 0))
        self.lineEdit_totalAmountReceipt.setCursorPosition(0)
        self.lineEdit_totalAmountReceipt.setReadOnly(True)

        self.gridLayout_saveReceipt.addWidget(self.lineEdit_totalAmountReceipt, 0, 1, 1, 1)

        self.label_totalAmountData = QLabel(self.groupBox_saveReceipt)
        self.label_totalAmountData.setObjectName(u"label_totalAmountData")

        self.gridLayout_saveReceipt.addWidget(self.label_totalAmountData, 1, 0, 1, 1)

        self.label_totalAmountDataValue = QLabel(self.groupBox_saveReceipt)
        self.label_totalAmountDataValue.setObjectName(u"label_totalAmountDataValue")

        self.gridLayout_saveReceipt.addWidget(self.label_totalAmountDataValue, 1, 1, 1, 1)

        self.checkBox_feedbackMatch = QCheckBox(self.groupBox_saveReceipt)
        self.checkBox_feedbackMatch.setObjectName(u"checkBox_feedbackMatch")
        self.checkBox_feedbackMatch.setChecked(True)

        self.gridLayout_saveReceipt.addWidget(self.checkBox_feedbackMatch, 1, 2, 1, 1)

        self.lineEdit_tags = QLineEdit(self.groupBox_saveReceipt)
        self.lineEdit_tags.setObjectName(u"lineEdit_tags")

        self.gridLayout_saveReceipt.addWidget(self.lineEdit_tags, 0, 2, 1, 2)


        self.horizontalLayout_6.addLayout(self.gridLayout_saveReceipt)


        self.verticalLayout_dataDisplay.addWidget(self.groupBox_saveReceipt)


        self.horizontalLayout_4.addLayout(self.verticalLayout_dataDisplay)

        self.splitter_mainPage.addWidget(self.frame_dataDisplay)

        self.horizontalLayout_3.addWidget(self.splitter_mainPage)

        self.frame_buttonsMainRight = QFrame(self.tabWidgetPage1)
        self.frame_buttonsMainRight.setObjectName(u"frame_buttonsMainRight")
        sizePolicy2.setHeightForWidth(self.frame_buttonsMainRight.sizePolicy().hasHeightForWidth())
        self.frame_buttonsMainRight.setSizePolicy(sizePolicy2)
        self.frame_buttonsMainRight.setMinimumSize(QSize(90, 0))
        self.frame_buttonsMainRight.setFrameShape(QFrame.NoFrame)
        self.frame_buttonsMainRight.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_buttonsMainRight)
        self.verticalLayout_3.setSpacing(10)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, -1, 0, 0)
        self.modernButton_detectVendor = ModernButton(self.frame_buttonsMainRight)
        self.modernButton_detectVendor.setObjectName(u"modernButton_detectVendor")
        self.modernButton_detectVendor.setMinimumSize(QSize(70, 70))

        self.verticalLayout_3.addWidget(self.modernButton_detectVendor)

        self.modernButton_parseData = ModernButton(self.frame_buttonsMainRight)
        self.modernButton_parseData.setObjectName(u"modernButton_parseData")
        self.modernButton_parseData.setMinimumSize(QSize(70, 70))

        self.verticalLayout_3.addWidget(self.modernButton_parseData)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)

        self.modernButton_addRow = ModernButton(self.frame_buttonsMainRight)
        self.modernButton_addRow.setObjectName(u"modernButton_addRow")
        self.modernButton_addRow.setMinimumSize(QSize(70, 70))

        self.verticalLayout_3.addWidget(self.modernButton_addRow)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.modernButton_classData = ModernButton(self.frame_buttonsMainRight)
        self.modernButton_classData.setObjectName(u"modernButton_classData")
        self.modernButton_classData.setMinimumSize(QSize(70, 70))

        self.verticalLayout_3.addWidget(self.modernButton_classData)

        self.modernButton_fillData = ModernButton(self.frame_buttonsMainRight)
        self.modernButton_fillData.setObjectName(u"modernButton_fillData")
        self.modernButton_fillData.setMinimumSize(QSize(70, 70))

        self.verticalLayout_3.addWidget(self.modernButton_fillData)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)

        self.modernButton_saveData = ModernButton(self.frame_buttonsMainRight)
        self.modernButton_saveData.setObjectName(u"modernButton_saveData")
        self.modernButton_saveData.setMinimumSize(QSize(70, 70))

        self.verticalLayout_3.addWidget(self.modernButton_saveData)


        self.horizontalLayout_3.addWidget(self.frame_buttonsMainRight)

        self.centralTabWidget.addTab(self.tabWidgetPage1, "")
        self.tabWidgetPage2 = QWidget()
        self.tabWidgetPage2.setObjectName(u"tabWidgetPage2")
        self.horizontalLayout_2 = QHBoxLayout(self.tabWidgetPage2)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(4, 4, 6, 4)
        self.frame_plotButtonbar = QFrame(self.tabWidgetPage2)
        self.frame_plotButtonbar.setObjectName(u"frame_plotButtonbar")
        sizePolicy2.setHeightForWidth(self.frame_plotButtonbar.sizePolicy().hasHeightForWidth())
        self.frame_plotButtonbar.setSizePolicy(sizePolicy2)
        self.frame_plotButtonbar.setMinimumSize(QSize(90, 0))
        self.frame_plotButtonbar.setFrameShape(QFrame.NoFrame)
        self.frame_plotButtonbar.setFrameShadow(QFrame.Plain)
        self.verticalLayout = QVBoxLayout(self.frame_plotButtonbar)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.modernButton_loadPlotData = ModernButton(self.frame_plotButtonbar)
        self.modernButton_loadPlotData.setObjectName(u"modernButton_loadPlotData")
        self.modernButton_loadPlotData.setMinimumSize(QSize(70, 70))

        self.verticalLayout.addWidget(self.modernButton_loadPlotData)

        self.modernButton_plotStem = ModernButton(self.frame_plotButtonbar)
        self.modernButton_plotStem.setObjectName(u"modernButton_plotStem")
        self.modernButton_plotStem.setEnabled(False)
        self.modernButton_plotStem.setMinimumSize(QSize(70, 70))

        self.verticalLayout.addWidget(self.modernButton_plotStem)

        self.modernButton_plotPie = ModernButton(self.frame_plotButtonbar)
        self.modernButton_plotPie.setObjectName(u"modernButton_plotPie")
        self.modernButton_plotPie.setEnabled(False)
        self.modernButton_plotPie.setMinimumSize(QSize(70, 70))

        self.verticalLayout.addWidget(self.modernButton_plotPie)

        self.label_pieType = QLabel(self.frame_plotButtonbar)
        self.label_pieType.setObjectName(u"label_pieType")
        self.label_pieType.setFont(font)

        self.verticalLayout.addWidget(self.label_pieType)

        self.comboBox_PiePlotType = QComboBox(self.frame_plotButtonbar)
        self.comboBox_PiePlotType.setObjectName(u"comboBox_PiePlotType")
        sizePolicy7 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.comboBox_PiePlotType.sizePolicy().hasHeightForWidth())
        self.comboBox_PiePlotType.setSizePolicy(sizePolicy7)
        self.comboBox_PiePlotType.setMinimumSize(QSize(100, 0))

        self.verticalLayout.addWidget(self.comboBox_PiePlotType)


        self.horizontalLayout_2.addWidget(self.frame_plotButtonbar)

        self.frame_dataAnalysis = QFrame(self.tabWidgetPage2)
        self.frame_dataAnalysis.setObjectName(u"frame_dataAnalysis")
        sizePolicy5.setHeightForWidth(self.frame_dataAnalysis.sizePolicy().hasHeightForWidth())
        self.frame_dataAnalysis.setSizePolicy(sizePolicy5)
        self.frame_dataAnalysis.setFrameShape(QFrame.NoFrame)
        self.frame_dataAnalysis.setFrameShadow(QFrame.Plain)

        self.horizontalLayout_2.addWidget(self.frame_dataAnalysis)

        self.centralTabWidget.addTab(self.tabWidgetPage2, "")

        self.horizontalLayout.addWidget(self.centralTabWidget)

        pybb_MainWindow.setCentralWidget(self.centralwidget)
        self.pybb_menubar = QMenuBar(pybb_MainWindow)
        self.pybb_menubar.setObjectName(u"pybb_menubar")
        self.pybb_menubar.setGeometry(QRect(0, 0, 1392, 24))
        self.menuFile = QMenu(self.pybb_menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.pybb_menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuFlags = QMenu(self.menuEdit)
        self.menuFlags.setObjectName(u"menuFlags")
        self.menuHelp = QMenu(self.pybb_menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuShow = QMenu(self.pybb_menubar)
        self.menuShow.setObjectName(u"menuShow")
        pybb_MainWindow.setMenuBar(self.pybb_menubar)
        self.statusbar = ColoredStatusBar(pybb_MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        pybb_MainWindow.setStatusBar(self.statusbar)

        self.pybb_menubar.addAction(self.menuFile.menuAction())
        self.pybb_menubar.addAction(self.menuEdit.menuAction())
        self.pybb_menubar.addAction(self.menuShow.menuAction())
        self.pybb_menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionExport_to_CSV)
        self.menuFile.addAction(self.actionCreate_data_backup)
        self.menuEdit.addAction(self.menuFlags.menuAction())
        self.menuEdit.addAction(self.actionData_Directory)
        self.menuEdit.addAction(self.actionDefault_Language)
        self.menuEdit.addAction(self.actionCurrency)
        self.menuEdit.addAction(self.actionLogger_Popup_Level)
        self.menuFlags.addAction(self.actionMove_on_Save)
        self.menuFlags.addAction(self.actionGenerate_Unique_Name)
        self.menuFlags.addAction(self.actionAlways_Ask_for_Image)
        self.menuFlags.addAction(self.actionShow_Logger_on_Start)
        self.menuFlags.addAction(self.actionLogger_debug)
        self.menuHelp.addAction(self.actionAbout)
        self.menuShow.addAction(self.actionRaw_Text)
        self.menuShow.addAction(self.actionShow_Logger)

        self.retranslateUi(pybb_MainWindow)

        self.centralTabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(pybb_MainWindow)
    # setupUi

    def retranslateUi(self, pybb_MainWindow):
        pybb_MainWindow.setWindowTitle(QCoreApplication.translate("pybb_MainWindow", u"PyBudgetBook", None))
        self.actionMove_on_Save.setText(QCoreApplication.translate("pybb_MainWindow", u"Move on Save", None))
        self.actionMove_on_Save.setProperty("flag_name", QCoreApplication.translate("pybb_MainWindow", u"see_code", None))
        self.actionLogger_debug.setText(QCoreApplication.translate("pybb_MainWindow", u"Logger Show Debug", None))
        self.actionData_Directory.setText(QCoreApplication.translate("pybb_MainWindow", u"Data Directory", None))
        self.actionShow_Logger.setText(QCoreApplication.translate("pybb_MainWindow", u"Show Logger", None))
        self.actionAbout.setText(QCoreApplication.translate("pybb_MainWindow", u"About", None))
        self.actionRaw_Text.setText(QCoreApplication.translate("pybb_MainWindow", u"Raw Text", None))
        self.actionDefault_Language.setText(QCoreApplication.translate("pybb_MainWindow", u"Default Language", None))
        self.actionLogger_Popup_Level.setText(QCoreApplication.translate("pybb_MainWindow", u"Logger Popup Level", None))
        self.actionAlways_Ask_for_Image.setText(QCoreApplication.translate("pybb_MainWindow", u"Always Ask for Image", None))
        self.actionGenerate_Unique_Name.setText(QCoreApplication.translate("pybb_MainWindow", u"Generate Unique Name", None))
        self.actionShow_Logger_on_Start.setText(QCoreApplication.translate("pybb_MainWindow", u"Show Logger on Start", None))
        self.actionExport_to_CSV.setText(QCoreApplication.translate("pybb_MainWindow", u"Export to CSV", None))
        self.actionCreate_data_backup.setText(QCoreApplication.translate("pybb_MainWindow", u"Create data backup", None))
        self.actionCurrency.setText(QCoreApplication.translate("pybb_MainWindow", u"Currency", None))
        self.modernButton_loadReceipt.setText(QCoreApplication.translate("pybb_MainWindow", u"...", None))
        self.label_receiptDisplayMode.setText(QCoreApplication.translate("pybb_MainWindow", u"Lang.", None))
        self.label_baseLang.setText(QCoreApplication.translate("pybb_MainWindow", u"Show", None))
        self.comboBox_receiptDisplayMode.setItemText(0, QCoreApplication.translate("pybb_MainWindow", u"Original", None))
        self.comboBox_receiptDisplayMode.setItemText(1, QCoreApplication.translate("pybb_MainWindow", u"Filtered", None))

        self.label_filterSlider.setText(QCoreApplication.translate("pybb_MainWindow", u"Filter", None))
        self.groupBox_additionalData.setTitle(QCoreApplication.translate("pybb_MainWindow", u"Receipt Data", None))
#if QT_CONFIG(tooltip)
        self.checkBox_useDiffParsingLang.setToolTip(QCoreApplication.translate("pybb_MainWindow", u"<html><head/><body><p>This can be used to use a different language to parse the extracted string and group match the data. Examples are parsing a receipt in french or english from a vacation but adding and matching the data to the german patterns. <span style=\" font-weight:700; color:#ca4d69;\">Warning:</span> This can make your patterns slightly obscure!</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_useDiffParsingLang.setText(QCoreApplication.translate("pybb_MainWindow", u"Use different lang. for data parsing", None))
        self.label_overallCat.setText(QCoreApplication.translate("pybb_MainWindow", u"Overall Category:", None))
        self.label_marketVendor.setText(QCoreApplication.translate("pybb_MainWindow", u"Supermarket / Vendor:", None))
        self.label_shopDate.setText(QCoreApplication.translate("pybb_MainWindow", u"Date:", None))
        self.groupBox_saveReceipt.setTitle(QCoreApplication.translate("pybb_MainWindow", u"Save Receipt", None))
        self.label_totalAmountReceipt.setText(QCoreApplication.translate("pybb_MainWindow", u"Total amount extracted:", None))
        self.label_totalAmountData.setText(QCoreApplication.translate("pybb_MainWindow", u"Difference to data sum:", None))
        self.label_totalAmountDataValue.setText("")
        self.checkBox_feedbackMatch.setText(QCoreApplication.translate("pybb_MainWindow", u"Feedback matching data", None))
        self.lineEdit_tags.setText(QCoreApplication.translate("pybb_MainWindow", u"tag1;tag2", None))
        self.modernButton_detectVendor.setText(QCoreApplication.translate("pybb_MainWindow", u"...", None))
        self.modernButton_parseData.setText(QCoreApplication.translate("pybb_MainWindow", u"...", None))
        self.modernButton_addRow.setText(QCoreApplication.translate("pybb_MainWindow", u"...", None))
        self.modernButton_classData.setText(QCoreApplication.translate("pybb_MainWindow", u"...", None))
        self.modernButton_fillData.setText(QCoreApplication.translate("pybb_MainWindow", u"...", None))
        self.modernButton_saveData.setText(QCoreApplication.translate("pybb_MainWindow", u"...", None))
        self.centralTabWidget.setTabText(self.centralTabWidget.indexOf(self.tabWidgetPage1), QCoreApplication.translate("pybb_MainWindow", u"Add New Receipt", None))
        self.modernButton_loadPlotData.setText(QCoreApplication.translate("pybb_MainWindow", u"...", None))
        self.modernButton_plotStem.setText(QCoreApplication.translate("pybb_MainWindow", u"...", None))
        self.modernButton_plotPie.setText(QCoreApplication.translate("pybb_MainWindow", u"...", None))
        self.label_pieType.setText(QCoreApplication.translate("pybb_MainWindow", u"Pie", None))
        self.centralTabWidget.setTabText(self.centralTabWidget.indexOf(self.tabWidgetPage2), QCoreApplication.translate("pybb_MainWindow", u"Data Analysis", None))
        self.menuFile.setTitle(QCoreApplication.translate("pybb_MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("pybb_MainWindow", u"Edit", None))
        self.menuFlags.setTitle(QCoreApplication.translate("pybb_MainWindow", u"Flags", None))
        self.menuHelp.setTitle(QCoreApplication.translate("pybb_MainWindow", u"Help", None))
        self.menuShow.setTitle(QCoreApplication.translate("pybb_MainWindow", u"Show", None))
    # retranslateUi

