"""
/***************************************************************************
         Scattergram       - A QGIS plugin to plot scattergram
                             -------------------
    begin                : 2008-09-04
    copyright            : (C) 2008 by G. Picard
    email                : 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qwt5 import *



class MyMarker(QWidget):
    """class to draw a symbol on the graph. Much faster than using QwtMarker"""
    def __init__(self, qwtPlot):
        QWidget.__init__(self, qwtPlot)
        self.qwtPlot = qwtPlot

    def setSymbol(self, symbol):
        self.symbol = symbol
        self.resize(symbol.size())

    def setValue(self, x, y):
        pos0 = self.qwtPlot.canvas().pos()
        self.move(self.qwtPlot.transform(QwtPlot.xBottom, x) + pos0.x(),
                  self.qwtPlot.transform(QwtPlot.yLeft, y) + pos0.y())


    def paintEvent(self, paintevent):
        if self.symbol != None:
            p = QPainter(self)
            p.setPen(Qt.blue);
            size = self.symbol.size()
            self.symbol.draw(p, size.width() / 2, size.height() / 2)  ##self.pos())


class ScattergramPlot(QwtPlot):
    
    def __init__(self, *args):
        QwtPlot.__init__(self, *args)

        self.setCanvasBackground(Qt.white)
        self.curve = [None, None]
        self.curve[0] = QwtPlotCurve()
        self.curve[0].setStyle(QwtPlotCurve.Dots)
        self.curve[0].attach(self)

        self.curve[1] = QwtPlotCurve()
        self.curve[1].setStyle(QwtPlotCurve.Dots)
        pen = QPen(Qt.red)
        self.curve[1].setPen(pen)
        self.curve[1].attach(self)
        
        #point picker
        self.picker = QwtPlotPicker(
            QwtPlot.xBottom,
            QwtPlot.yLeft,
            QwtPicker.PointSelection,
            QwtPlotPicker.CrossRubberBand,
            QwtPicker.AlwaysOn,
            self.canvas())
        self.picker.setRubberBandPen(QPen(Qt.blue))
        self.picker.setTrackerPen(QPen(Qt.blue))
        
        #polygon picker used by identify
        self.polygonPicker = QwtPlotPicker(
            QwtPlot.xBottom,
            QwtPlot.yLeft,
            QwtPicker.PolygonSelection | QwtPicker.DragSelection,
            QwtPlotPicker.NoRubberBand,
            QwtPicker.AlwaysOn,
            self.canvas())
        self.polygonPicker.setRubberBandPen(QPen(Qt.blue))
        self.polygonPicker.setTrackerPen(QPen(Qt.blue))
        #make this picker react to the sequence:
        #start polygon:     shift+leftMouse
        #add point:         shift+rightMouse
        #end polygon:       shift+leftMouse
        self.polygonPicker.setMousePattern(QwtEventPattern.MouseSelect1, Qt.LeftButton, Qt.ShiftModifier)
        self.polygonPicker.setMousePattern(QwtEventPattern.MouseSelect2, Qt.RightButton, Qt.ShiftModifier)

        self.zoomer = QwtPlotZoomer(
            QwtPlot.xBottom,
            QwtPlot.yLeft,
            QwtPicker.DragSelection,
            QwtPicker.AlwaysOff,
            self.canvas())
        self.zoomer.setRubberBandPen(QPen(Qt.darkBlue))
        
        #pointer used by tracker
        self.pointer = MyMarker(self)   ##QLabel("x",self)
        self.pointer.setSymbol(
            QwtSymbol(QwtSymbol.Ellipse,
                      QBrush(Qt.NoBrush),
                      QPen(Qt.red, 1),
                      QSize(5, 5)))
        self.pointer.hide()
        
        #pointer used by identify
        self.identifyPointer = MyMarker(self)   ##QLabel("x",self)
        self.identifyPointer.setSymbol(
            QwtSymbol(QwtSymbol.XCross,
                      QBrush(Qt.NoBrush),
                      QPen(Qt.blue, 2),
                      QSize(5, 5)))
        self.identifyPointer.hide()
        
        #polygon item that stays on the canvas until hidden
        self.identifyPolygon = IdentifyItem(self,
                                             QPolygonF(),
                                             'Polygon',
                                             QBrush(Qt.NoBrush),
                                             QPen(Qt.blue, 1))
        self.identifyPolygon.hide()
        self.zoomEnabled(False)

    def setData(self, curvenumber, valuesX, valuesY):
        self.curve[curvenumber].setData(valuesX, valuesY)
        self.replot()
        self.zoomer.setZoomBase() # reinitialize the scale

    def resetCurve(self, curvenumber):
        self.curve[curvenumber].setData([], [])
        self.replot()
        self.zoomer.setZoomBase() # reinitialize the scale

    def zoomEnabled(self, on):
        self.zoomer.setEnabled(on)
        self.zoomer.zoom(0)
        self.identifyPolygon.hide()
        self.replot()
        if on:
            self.picker.setRubberBand(QwtPicker.NoRubberBand)
        else:
            self.picker.setRubberBand(QwtPicker.CrossRubberBand)

class IdentifyItem(QwtPlotItem):
    def __init__(self, plot, geom, type, brush, pen):
        QwtPlotItem.__init__(self)
        self.setZ(0.0)
        self.type = type
        self.pen = pen
        self.brush = brush
        self.geom = geom
        self.attach(plot)
    
    def rtti(self):
        return QwtPlotItemRtti_PlotUserItem
    
    def setGeom(self, geom):
        if ( self.geom != geom ):
            self.geom = geom
            self.itemChanged()
    
    def setPen(self, pen):
        if ( pen != self.pen ):
            self.pen = pen
            self.itemChanged()

    def setBrush(self, brush):
        if ( brush != self.brush ):
            self.brush = brush
            self.itemChanged()
        
    def draw(self, painter, xMap, yMap, rect):
        if ( rect.isValid() ):
            #r = self.poly.boundingRect()
            painter.setPen(self.pen)
            painter.setBrush(self.brush)
            if ( self.type == 'Polygon' ):
                QwtPainter.drawPolygon(painter, self.geom)
            elif ( self.type == 'Rect' ):
                QwtPainter.drawRect(painter, self.geom)
            else:
                raise TypeError("Invalid IdentifyItem.type: "+self.type )
