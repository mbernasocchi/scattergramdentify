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

#
# python translation of QgsMeasureTool in the QGis API
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *


class AreaMapTool (QgsMapTool):

    def __init__(self,canvas):
        QgsMapTool.__init__( self,canvas )

        self.canvas=canvas
        self.mRubberBand = QgsRubberBand( canvas, True )

        self.cursor = QCursor(Qt.PointingHandCursor)

        #QPixmap myCrossHairQPixmap = QPixmap(( const char ** ) cross_hair_cursor );
        #mCursor = QCursor( myCrossHairQPixmap, 8, 8 );

        self.mRightMouseClicked = False

    def points(self):
        return self.mPoints

    def activate(self):

        QgsMapTool.activate(self)
        self.mRightMouseClicked = False
        self.restart()
        # ensure that we have correct settings
        #self.updateProjection()

        #// If we suspect that they have data that is projected, yet the
        #// map CRS is set to a geographic one, warn them.
        #if ( mCanvas->mapRenderer()->distArea()->geographic() &&
        #     ( mCanvas->extent().height() > 360 ||
        #       mCanvas->extent().width() > 720 ) )
        #{
        #    QMessageBox::warning( NULL, tr( "Incorrect measure results" ),
        #                  tr( "<p>This map is defined with a geographic coordinate system "
        #                      "(latitude/longitude) "
        #                      "but the map extents suggests that it is actually a projected "
        #                      "coordinate system (e.g., Mercator). "
        #                      "If so, the results from line or area measurements will be "
        #                      "incorrect.</p>"
        #                      "<p>To fix this, explicitly set an appropriate map coordinate "
        #                      "system using the <tt>Settings:Project Properties</tt> menu." ) );
        #mWrongProjectProjection = true;
        #}


    def deactivate(self):
        QgsMapTool.deactivate(self)
        self.mRubberBand.reset( True )    
        

    def restart(self):
        #self.updateProjection()
        self.mPoints=[]

        self.mRubberBand.reset( True );

        #// re-read color settings
        #QSettings settings;
        #int myRed = settings.value( "/qgis/default_measure_color_red", 180 ).toInt();
        #int myGreen = settings.value( "/qgis/default_measure_color_green", 180 ).toInt();
        #int myBlue = settings.value( "/qgis/default_measure_color_blue", 180 ).toInt();
        #mRubberBand->setColor( QColor( myRed, myGreen, myBlue ) );

        self.mRightMouseClicked = False
        self.mWrongProjectProjection = False



    def canvasPressEvent( self, e ):

        if ( e.button() == Qt.LeftButton ):
            if ( self.mRightMouseClicked ):
                self.restart()

            idPoint = self.canvas.getCoordinateTransform().toMapCoordinates( e.x(), e.y() )
        ###mDialog->mousePress( idPoint );


    def canvasMoveEvent( self,e ):

        if ( not(self.mRightMouseClicked) ):
            point = self.canvas.getCoordinateTransform().toMapCoordinates( e.pos().x(), e.pos().y() )
            self.mRubberBand.movePoint( point )
            #mDialog.mouseMove( point );


    def canvasReleaseEvent( self,e):
        point = self.canvas.getCoordinateTransform().toMapCoordinates( e.x(), e.y() )

        if ( e.button() == Qt.RightButton ):
            if ( self.mRightMouseClicked ):
                self.restart()
            else:
                self.mRightMouseClicked = True
                if (len(self.mPoints)>=3):
                    self.emit(SIGNAL("finished()"))
                else:
                    self.restart()

        elif ( e.button() == Qt.LeftButton ):
            self.addPoint( point )
            #mDialog.show();


    def addPoint( self,point ):
        #QgsDebugMsg( "point=" + point.toString() );

        #if ( mWrongProjectProjection ):
        #    updateProjection();
        #    mWrongProjectProjection = false;

        # don't add points with the same coordinates
        if ( len(self.mPoints) > 0 and point == self.mPoints[-1] ):
            return

        self.mPoints.append( point )

        self.mRubberBand.addPoint( point )
        #mDialog.addPoint( point );
