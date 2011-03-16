from scattergramplot import ScattergramPlot
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scattergramwidgetbase.ui'
#
# Created: Sat Sep 13 15:42:42 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,613,423).size()).expandedTo(Dialog.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(Dialog)
        self.vboxlayout.setObjectName("vboxlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.hboxlayout.addWidget(self.label)

        self.bandX = QtGui.QComboBox(Dialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bandX.sizePolicy().hasHeightForWidth())
        self.bandX.setSizePolicy(sizePolicy)
        self.bandX.setObjectName("bandX")
        self.hboxlayout.addWidget(self.bandX)

        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.hboxlayout.addWidget(self.label_2)

        self.bandY = QtGui.QComboBox(Dialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bandY.sizePolicy().hasHeightForWidth())
        self.bandY.setSizePolicy(sizePolicy)
        self.bandY.setObjectName("bandY")
        self.hboxlayout.addWidget(self.bandY)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.qwtPlot = ScattergramPlot(Dialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qwtPlot.sizePolicy().hasHeightForWidth())
        self.qwtPlot.setSizePolicy(sizePolicy)
        self.qwtPlot.setObjectName("qwtPlot")
        self.vboxlayout.addWidget(self.qwtPlot)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.trackbutton = QtGui.QToolButton(Dialog)
        self.trackbutton.setIcon(QtGui.QIcon(":/plugins/scattergram/tracking.png"))
        self.trackbutton.setCheckable(True)
        self.trackbutton.setChecked(True)
        self.trackbutton.setObjectName("trackbutton")
        self.hboxlayout1.addWidget(self.trackbutton)

        self.areabutton = QtGui.QToolButton(Dialog)
        self.areabutton.setIcon(QtGui.QIcon(":/plugins/scattergram/mArea.png"))
        self.areabutton.setCheckable(True)
        self.areabutton.setObjectName("areabutton")
        self.hboxlayout1.addWidget(self.areabutton)

        self.zoombutton = QtGui.QToolButton(Dialog)
        self.zoombutton.setIcon(QtGui.QIcon(":/plugins/scattergram/mActionZoom.png"))
        self.zoombutton.setCheckable(True)
        self.zoombutton.setChecked(False)
        self.zoombutton.setObjectName("zoombutton")
        self.hboxlayout1.addWidget(self.zoombutton)
        
        self.identifybutton = QtGui.QToolButton(Dialog)
        #self.identifybutton.setIcon(QtGui.QIcon(":/plugins/scattergram/mActionIdentify.png"))
        self.identifybutton.setCheckable(True)
        self.identifybutton.setChecked(False)
        self.identifybutton.setObjectName("identifybutton")
        self.hboxlayout1.addWidget(self.identifybutton)

        spacerItem = QtGui.QSpacerItem(200,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)

        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.hboxlayout1.addWidget(self.label_3)

        self.npoints = QtGui.QSpinBox(Dialog)
        self.npoints.setMinimum(1000)
        self.npoints.setMaximum(1000000)
        self.npoints.setSingleStep(5000)
        self.npoints.setProperty("value",QtCore.QVariant(10000))
        self.npoints.setObjectName("npoints")
        self.hboxlayout1.addWidget(self.npoints)

        spacerItem1 = QtGui.QSpacerItem(361,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)

        self.closeButton = QtGui.QPushButton(Dialog)
        self.closeButton.setCheckable(False)
        self.closeButton.setAutoDefault(False)
        self.closeButton.setObjectName("closeButton")
        self.hboxlayout1.addWidget(self.closeButton)
        self.vboxlayout.addLayout(self.hboxlayout1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "X:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Y:", None, QtGui.QApplication.UnicodeUTF8))
        self.trackbutton.setToolTip(QtGui.QApplication.translate("Dialog", "Track mouse movement on the map and report values on the scattergram", None, QtGui.QApplication.UnicodeUTF8))
        self.trackbutton.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.areabutton.setToolTip(QtGui.QApplication.translate("Dialog", "Select an area on the map to plot the scattergram of the inner points", None, QtGui.QApplication.UnicodeUTF8))
        self.areabutton.setText(QtGui.QApplication.translate("Dialog", "A", None, QtGui.QApplication.UnicodeUTF8))
        self.zoombutton.setToolTip(QtGui.QApplication.translate("Dialog", "Zoom in/out the scattergrammm", None, QtGui.QApplication.UnicodeUTF8))
        self.zoombutton.setText(QtGui.QApplication.translate("Dialog", "->", None, QtGui.QApplication.UnicodeUTF8))
        self.identifybutton.setToolTip(QtGui.QApplication.translate("Dialog", "Identify a scattergram point on the map canvas", None, QtGui.QApplication.UnicodeUTF8))
        self.identifybutton.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Sampled pixels:", None, QtGui.QApplication.UnicodeUTF8))
        self.closeButton.setText(QtGui.QApplication.translate("Dialog", "Close", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4.Qwt5 import QwtPlot
import resources_rc
