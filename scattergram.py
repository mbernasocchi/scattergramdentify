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


from scattergramwidget import ScattergramWidget

#from selectPointTool import *

class Scattergram:
  def __init__(self, iface):
    # save reference to the QGIS interface
    self.iface = iface
    self.canvas = iface.mapCanvas()

  def initGui(self):
    # create action that will start plugin configuration
    self.action = QAction(QIcon(":/plugins/scattergram/icon.png"), "Scattergram", self.iface.mainWindow())
    self.action.setWhatsThis("Scattergram")
    QObject.connect(self.action, SIGNAL("activated()"), self.run)
    # add toolbar button and menu item
    self.iface.addToolBarIcon(self.action)
    self.iface.addPluginToMenu("&Analyses", self.action)
    # add the tool to select feature
   

###Qt.AllDockWidgetAreas
  def unload(self):
    # remove the plugin menu item and icon
    self.iface.removePluginMenu("&Analyses", self.action)
    self.iface.removeToolBarIcon(self.action)
    try:
      self.scattergramwidget.close()
      QgsMapLayerRegistry.instance().removeMapLayer(self.scattergramwidget.showPointOnMapLayer.id())
    except:
      pass

  def run(self):
    # create the widget to display information
    self.scattergramwidget = ScattergramWidget(self.iface, self.canvas)
    self.scattergramwidget.show()
