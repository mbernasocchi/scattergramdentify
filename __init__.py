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

from scattergram import Scattergram

def name(): 
  return "Scattergram" 

def description():
  return "Plot the scattergram of two raster layers" 

def version(): 
  return "Version 0.2.2" 

def qgisMinimumVersion():
  return '1.0'

def authorName():
  return 'Ghislain Picard'

def classFactory(iface): 
  return Scattergram(iface) 

