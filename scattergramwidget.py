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
                    #TODO not use INT
                    coords[int(vx),int(vy)] = point
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
        if (enabled):
            self.showPointOnMapLayer = QgsVectorLayer("Point?crs=epsg:4326", "Scattergram point location", "memory")
            fet = QgsFeature()
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(0,0)))
            self.showPointOnMapLayer.dataProvider().addFeatures([ fet ])
            
            renderer = self.showPointOnMapLayer.rendererV2()
            symbol = renderer.symbols()[0]
            color = QColor('white')
            symbol.setColor(color)
            
            QgsMapLayerRegistry.instance().addMapLayer(self.showPointOnMapLayer)
            QObject.connect(self.qwtPlot.picker, SIGNAL("selected (QwtDoublePoint)"), self.showPointOnMap)
        else:
            QObject.disconnect(self.qwtPlot.picker, SIGNAL("selected (QwtDoublePoint)"), self.showPointOnMap)
            QgsMapLayerRegistry.instance().removeMapLayer(self.showPointOnMapLayer.id())

    def showPointOnMap(self, pos):
        try:
            point = self.coords[int(pos.x()), int(pos.y())]
            geom = QgsGeometry.fromPoint(QgsPoint(point.x(), point.y()))
            self.showPointOnMapLayer.dataProvider().changeGeometryValues({1:geom})
            self.showPointOnMapLayer.updateExtents() 
            self.showPointOnMapLayer.triggerRepaint()
        except:
            print "problem locating: "+ str(pos)
        
    def done(self, i):
        self.areatoolEnabled(False)  # remove the area
        self.plottasks = []            # no more task to plot
        QDialog.done(self, i)