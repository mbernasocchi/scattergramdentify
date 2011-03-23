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
from qgis.core import *
import math
    
hasqwt = True
try:
    from PyQt4.Qwt5 import *
    from scattergramplot import ScattergramPlot
except:
    hasqwt = False

from scattergramwidgetbase import Ui_Dialog
from areamaptool import AreaMapTool



class ScattergramWidget(QDialog, Ui_Dialog):

    def __init__(self, iface, canvas):
        QWidget.__init__(self)
        
        Ui_Dialog.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Scattergram")

        
        self.iface = iface
        self.canvas = canvas

        QObject.connect(self.closeButton, SIGNAL("clicked()"), self.accept)
        QObject.connect(self.canvas, SIGNAL("layersChanged()"), self.setupItems)
        QObject.connect(self.trackbutton, SIGNAL("toggled(bool)"), self.trackEnabled)
        self.trackEnabled(self.trackbutton.isChecked())        
        QObject.connect(self.zoombutton, SIGNAL("toggled(bool)"), self.qwtPlot.zoomEnabled)
        QObject.connect(self.areabutton, SIGNAL("toggled(bool)"), self.areatoolEnabled)
        QObject.connect(self.identifybutton, SIGNAL("toggled(bool)"), self.showPointOnMapEnabled)

        self.setupItems()

        QObject.connect(self.bandX, SIGNAL("activated(int)"), self.plot)
        QObject.connect(self.bandY, SIGNAL("activated(int)"), self.plot)

        QObject.connect(self.npoints, SIGNAL("editingFinished()"), self.plot)

        self.plot()

    def setupItems(self):
        
        
        # add raster layers
        #
        saveX = unicode(self.bandX.currentText())
        saveY = unicode(self.bandY.currentText())
        firsttime = self.bandX.count() == 0
        
        self.bandX.clear()
        self.bandY.clear()
        self.comboArray = []
        for layerIndex in range(0, self.canvas.layerCount()):   # loop over the layers
            layer = self.canvas.layer(layerIndex)
            if (layer.type() == layer.RasterLayer) and (layer.providerKey() != "wms"):
                #self.layers.append(layer)
        
                for j in range(1, layer.bandCount() + 1):    # loop over the bands
                    name = unicode(layer.name())
                    if (layer.bandCount() > 1):
                        name += ' :' + unicode(layer.bandName(j))
                    self.bandX.addItem(name)
                    self.bandY.addItem(name)
                    if (saveX == name):
                        self.bandX.setCurrentIndex(self.bandX.count() - 1)
                    if (saveY == name):
                        self.bandY.setCurrentIndex(self.bandY.count() - 1)
                    self.comboArray.append((layerIndex, j))   ###layer.getRasterBandName(j)))
        
        if (firsttime and len(self.comboArray) >= 2):
            self.bandX.setCurrentIndex(0)
            self.bandY.setCurrentIndex(1)
        
        if (len(self.comboArray) == 0):
            self.areatoolEnabled(False)

    def plot(self):
        """plot scatterogram"""
        if (len(self.comboArray) == 0):
            return

        # delete all the plottasks and create a new one.
        self.plottasks = [{'istep': 0, 'extent': self.canvas.extent(),
              'focus': 0 , 'geom': None}]

        self.plotByStep()
        self.plotArea()

    
    def plotArea(self):
        """plot points in the area selected by the user"""
        if (len(self.comboArray) == 0):
            return
        try:
            self.tool
        except:
            return

        points = self.tool.points()
        if (len(points) == 0):
            return

        # add a plottask
        geom = QgsGeometry.fromPolygon([points])
        task = {'istep': 0, 'extent': geom.boundingBox(),
              'focus': 1 , 'geom':geom}
        self.plottasks.append(task)
        self.plotByStep()
        self.raise_()


    def plotByStep(self):
        """perform plotting operation step by step"""

        ntot = math.sqrt(self.npoints.value()) # total number of points along one dimension
        nstep = 50                             # number of points to sample along one dimension for 1 step
        if (len(self.plottasks) == 0):
            QObject.disconnect(self.timer, SIGNAL("timeout()"), self.plotByStep)
            return

        task = self.plottasks[0]
        istep = task['istep']
        
        if (nstep * istep > ntot or istep > 1000000 / nstep):
            self.plottasks.pop(0)
            return
        
        if (istep == 0):
            self.valuesX = []
            self.valuesY = []
            self.coords = {}
            try:
                self.timer
            except AttributeError:
                self.timer = QTimer(self)
            QObject.connect(self.timer, SIGNAL("timeout()"), self.plotByStep)
            self.timer.start(50)

        # get current X and Y layers
        layerX, ibandX = self.getLayerAndBand(self.bandX.currentIndex())
        layerY, ibandY = self.getLayerAndBand(self.bandY.currentIndex())

        # get Values


        # calculate steps
        extent = task['extent']
        firstpoint = QgsPoint(extent.xMinimum() + istep * extent.width() / ntot,
                            extent.yMinimum() + istep * extent.height() / ntot) # where to start the sampling

        firstrect = QgsRectangle(firstpoint.x(), firstpoint.y(), firstpoint.x() + extent.width() / nstep, firstpoint.y() + extent.height() / nstep) # calculate the step in x and y
        
        valuesX, valuesY, coords = self.getValues(layerX, ibandX, layerY, ibandY, nstep, firstrect, task['geom'])
        self.valuesX.extend(valuesX)
        self.valuesY.extend(valuesY)
        self.coords.update(coords)

        self.qwtPlot.setData(task['focus'], self.valuesX, self.valuesY)

        task['istep'] += 1


    def getValues(self, layerX, ibandX, layerY, ibandY, n, firstrect, geom):

        valuesX = []
        valuesY = []
        coords = {}
        for i in range(0, n):
            for j in range(0, n):
                point = QgsPoint(firstrect.xMinimum() + j * firstrect.width(), firstrect.yMinimum() + i * firstrect.height())
                
                if (geom != None):
                    if not(geom.contains(point)):
                        continue
                try:
                    vx = self.getValueFromIdentify(layerX, ibandX, point)
                    vy = self.getValueFromIdentify(layerY, ibandY, point)
                    valuesX.append(vx) # append only if getValueFromIdentify works for both layers
                    valuesY.append(vy)
                    #map plot coords to map coords
                    coords[vx, vy] = point
                except:
                    pass
                
        return valuesX, valuesY, coords


    def getValueFromIdentify(self, layer, iband, point):
        isok, ident = layer.identify(point)
        if (not(isok)):
            return 0    # not really normal!
        for j in ident:
            # layer must be one-band, so always this will be
            if j.right(1) == str(iband):
                return float(ident[j])


    def trackEnabled(self, enabled):
        if (enabled):
            QObject.connect(self.canvas, SIGNAL("xyCoordinates(QgsPoint)"), self.plotSingleValue)
        else:
            QObject.disconnect(self.canvas, SIGNAL("xyCoordinates(QgsPoint)"), self.plotSingleValue)
            self.qwtPlot.pointer.hide()


    def plotSingleValue(self, position):
        if (len(self.comboArray) == 0):
            return

        layerX, ibandX = self.getLayerAndBand(self.bandX.currentIndex())
        layerY, ibandY = self.getLayerAndBand(self.bandY.currentIndex())

        try:
            vx = self.getValueFromIdentify(layerX, ibandX, position)
            vy = self.getValueFromIdentify(layerY, ibandY, position)
            self.qwtPlot.pointer.show()
            self.qwtPlot.pointer.setValue(vx, vy)
        except:
            self.qwtPlot.pointer.hide()

    def getLayerAndBand(self, index):
        ilayer, iband = self.comboArray[index]
        layer = self.canvas.layer(ilayer)
        return layer, iband

    def areatoolEnabled(self, enable):

        if (enable):
            try:
                self.tool
            except:
                self.tool = AreaMapTool(self.canvas)
            QObject.connect(self.tool, SIGNAL("finished()"), self.plotArea)

            self.saveTool = self.canvas.mapTool()
            self.canvas.setMapTool(self.tool)
        else:
            self.qwtPlot.resetCurve(1)
            try:
                self.tool.deactivate()
            except:
                pass
            try:
                self.canvas.setMapTool(self.saveTool)
            except:
                pass

    def showPointOnMapEnabled(self, enabled):
        """check if showPointOnMap is Enabled"""
        if (enabled):
            self.showPointOnMapLayer = QgsVectorLayer("Point?crs=epsg:4326", "Scattergram point location", "memory")
            #symbol for qgis layer
            renderer = self.showPointOnMapLayer.rendererV2()
#            symbolLayer = renderer.symbol().symbolLayer(0)
            symbol = QgsMarkerSymbolV2()
            symbol.setColor(QColor('white'))
            renderer.setSymbol(symbol)
            
            QgsMapLayerRegistry.instance().addMapLayer(self.showPointOnMapLayer)
            QObject.connect(self.qwtPlot.picker, SIGNAL("selected (QwtDoublePoint)"), self.showPointOnMap)
            QObject.connect(self.qwtPlot.polygonPicker, SIGNAL("selected (QwtPolygon)"), self.showPointsOnMap)
            
            self.qwtPlot.polygonPicker.setRubberBand(QwtPicker.PolygonRubberBand)
            
        else:
            QObject.disconnect(self.qwtPlot.picker, SIGNAL("selected (QwtDoubleRect)"), self.showPointsOnMap)
            QObject.disconnect(self.qwtPlot.polygonPicker, SIGNAL("selected (QwtPolygon)"), self.showPointsOnMap)
            self.qwtPlot.polygonPicker.setRubberBand(QwtPicker.NoRubberBand)
            try:
                QgsMapLayerRegistry.instance().removeMapLayer(self.showPointOnMapLayer.id())
            except:
                pass
            self.qwtPlot.identifyPointer.hide()
            self.qwtPlot.identifyPolygon.hide()
            self.qwtPlot.replot()
            
    def clearPointsOnMap(self):
        """remove all points from the map canvas layer and removes the identify pointers"""
        self.qwtPlot.identifyPointer.hide()
        self.qwtPlot.identifyPolygon.hide()
        self.qwtPlot.replot()
        
        #delete everything from layer
        provider = self.showPointOnMapLayer.dataProvider()
        provider.select()
        feat = QgsFeature()
        fids = []
        while provider.nextFeature(feat):
            fids.append(feat.id())
        provider.deleteFeatures(fids)

    def showPointsOnMap(self, poly):
        """shows the selected points on the plot on the map canvas"""
        self.clearPointsOnMap()
        
        self.qwtPlot.identifyPolygon.setGeom(poly)
        self.qwtPlot.identifyPolygon.show()
        self.qwtPlot.replot()
        
        #create the new points
        curve = self.qwtPlot.curve[0]
        #data is in plot coords
        data = curve.data()
        
        #poly is in pixel coords, converting to plot coords
        points = []
        for i in range(0, poly.size()):
            point = self.qwtPlot.picker.invTransform(poly.at(i))
            points.append(point)
        
        poly = QPolygonF(points)
        bbox = poly.boundingRect()
        
        features = []
        for i in range(0, data.size()):
            x = data.x(i)
            y = data.y(i)
            
            if x >= bbox.x() and x <= bbox.x() + bbox.width() and \
               y >= bbox.y() and y <= bbox.y() + bbox.height():
                if poly.containsPoint(QPointF(x,y), 0):
                    #create points
                    feat = QgsFeature()
                    feat.setGeometry(QgsGeometry.fromPoint(self.coords[x, y]))
                    features.append(feat)
                
        self.showPointOnMapLayer.dataProvider().addFeatures( features )
        self.showPointOnMapLayer.updateExtents() 
        self.showPointOnMapLayer.triggerRepaint()
        
            
    def showPointOnMap(self, click):
        """shows the clicked point on the plot on the map canvas"""
        self.clearPointsOnMap()
        curve = self.qwtPlot.curve[0]
        clickPx = self.qwtPlot.picker.transform(click)
        
        try:
            closestPointIndex = curve.closestPoint(clickPx)[0]
            x = curve.data().x(closestPointIndex)
            y = curve.data().y(closestPointIndex)
            self.qwtPlot.identifyPointer.setValue(x, y)
            self.qwtPlot.identifyPointer.show()
            point = self.coords[x, y]
            
            fet = QgsFeature()
            fet.setGeometry(QgsGeometry.fromPoint(self.coords[x, y]))
            self.showPointOnMapLayer.dataProvider().addFeatures([ fet ])
            self.showPointOnMapLayer.updateExtents() 
            self.showPointOnMapLayer.triggerRepaint()
        except:
            print "Problem locating: "+ str(click.x()) + ", "+ str(click.y())
            print "Try using Zoom to get closer to the point you want to select"
            self.qwtPlot.identifyPointer.hide()
            
    def done(self, i):
        self.areatoolEnabled(False)  # remove the area
        self.plottasks = []            # no more task to plot
        try:
            QgsMapLayerRegistry.instance().removeMapLayer(self.showPointOnMapLayer.id())
        except:
            pass
        QDialog.done(self, i)
