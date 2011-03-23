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

        self.picker = QwtPlotPicker(
            QwtPlot.xBottom,
            QwtPlot.yLeft,
            QwtPicker.RectSelection | QwtPicker.DragSelection,
            QwtPlotPicker.RectRubberBand,
            QwtPicker.AlwaysOn,
            self.canvas())
        self.picker.setRubberBandPen(QPen(Qt.blue))
        self.picker.setTrackerPen(QPen(Qt.blue))

        self.zoomer = QwtPlotZoomer(
            QwtPlot.xBottom,
            QwtPlot.yLeft,
            QwtPicker.DragSelection,
            QwtPicker.AlwaysOff,
            self.canvas())
        self.zoomer.setRubberBandPen(QPen(Qt.darkBlue))
        self.zoomEnabled(False)
        #self.pointer = QwtPlotMarker()
        #self.pointer.setSymbol(
        #    QwtSymbol(QwtSymbol.Ellipse,
        #              QBrush(Qt.NoBrush),
        #              QPen(Qt.red, 1),
        #              QSize(5, 5)))
        #self.pointer.attach(self)
        self.pointer = MyMarker(self)   ##QLabel("x",self)
        self.pointer.setSymbol(
            QwtSymbol(QwtSymbol.Ellipse,
                      QBrush(Qt.NoBrush),
                      QPen(Qt.red, 1),
                      QSize(5, 5)))
        self.pointer.hide()
        
        self.identifyPointer = MyMarker(self)   ##QLabel("x",self)
        self.identifyPointer.setSymbol(
            QwtSymbol(QwtSymbol.XCross,
                      QBrush(Qt.NoBrush),
                      QPen(Qt.blue, 1),
                      QSize(5, 5)))
        self.identifyPointer.hide()
        
        self.identifyRect = IdentifyItem(self, QRectF(), 'Rect', QPen(), QBrush())
        self.identifyRect.hide()

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

#        if on:
#            self.picker.setRubberBand(QwtPicker.NoRubberBand)
#        else:
#            self.picker.setRubberBand(QwtPicker.CrossRubberBand)

class IdentifyItem(QwtPlotItem):
    def __init__(self, plot, rect, type, pen, brush):
        QwtPlotItem.__init__(self)
        self.setZ(0.0)
        self.type = type
        self.pen = pen
        self.brush = brush
        self.rect = rect
        self.attach(plot)
    
    def rtti(self):
        return QwtPlotItemRtti_PlotUserItem
    
    def setRect(self, rect):
        if ( self.rect != rect ):
            self.rect = rect
            self.itemChanged()
            
    def setPen(self, pen):
        if ( pen != self.pen ):
            self.pen = pen
            self.itemChanged()

    def setBrush(self, brush):
        if ( brush != self.brush ):
            self.brush = brush
            self.itemChanged()
        
    def boundingRect(self):
        return self.rect
    
    def draw(self, painter, xMap, yMap, rect):
        if ( rect.isValid() ):
            lt = QPoint(xMap.transform(self.rect.left()), yMap.transform(self.rect.top()))
            rb = QPoint(xMap.transform(self.rect.right()), yMap.transform(self.rect.bottom()))
            r = QRect(lt, rb)
            
            painter.setPen(self.pen)
            painter.setBrush(self.brush)
            if ( self.type == 'Polygon' ):
                QwtPainter.drawPolygon(painter, r)
            elif ( self.type == 'Rect' ):
                QwtPainter.drawRect(painter, r)
            else:
                raise TypeError("Invalid IdentifyItem.type: "+self.type )
