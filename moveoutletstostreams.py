# -*- coding: utf-8 -*-

"""
***************************************************************************
    moveoutletstostreams.py
    ---------------------
    Date                 : January 2018
    Copyright            : (C) 2018 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'January 2018'
__copyright__ = '(C) 2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.core import (QgsProcessing,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterVectorDestination,
                      )

from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils


class MoveOutletsToStreams(TauDemAlgorithm):

    D8_FLOWDIR = "D8_FLOWDIR"
    STREAM_RASTER = "STREAM_RASTER"
    OUTLETS = "OUTLETS"
    CELLS_TRAVERSE = "CELLS_TRAVERSE"
    MOVED_OUTLETS = "MOVED_OUTLETS"

    def name(self):
        return "moveoutletstostreams"

    def displayName(self):
        return self.tr("Move outlets to Streams")

    def group(self):
        return self.tr("Stream network analysis")

    def groupId(self):
        return "streamanalysis"

    def tags(self):
        return self.tr("dem,hydrology,stream,outlet").split(",")

    def shortHelpString(self):
        return self.tr("Moves outlet points that are not aligned with "
                       "a stream cell from a stream raster grid, downslope "
                       "along the D8 flow direction until a stream raster "
                       "cell is encountered.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/MoveOutletsToStreams.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.D8_FLOWDIR,
                                                            self.tr("D8 flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.STREAM_RASTER,
                                                            self.tr("Stream raster")))
        self.addParameter(QgsProcessingParameterVectorLayer(self.OUTLETS,
                                                            self.tr("Outlets"),
                                                            types=[QgsProcessing.TypeVectorPoint],
                                                            optional=False))
        self.addParameter(QgsProcessingParameterNumber(self.CELLS_TRAVERSE,
                                                       self.tr("Maximum number of grid cells to traverse"),
                                                       QgsProcessingParameterNumber.Integer,
                                                       50,
                                                       False))

        self.addParameter(QgsProcessingParameterVectorDestination(self.MOVED_OUTLETS,
                                                                  self.tr("Moved outlets"),
                                                                  QgsProcessing.TypeVectorPoint))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-p")
        arguments.append(self.parameterAsRasterLayer(parameters, self.D8_FLOWDIR, context).source())
        arguments.append("-src")
        arguments.append(self.parameterAsRasterLayer(parameters, self.STREAM_RASTER, context).source())
        arguments.append("-o")
        arguments.append(self.parameterAsVectorLayer(parameters, self.OUTLETS, context).source())
        arguments.append("-md")
        arguments.append("{}".format(self.parameterAsInt(parameters, self.CELLS_TRAVERSE, context)))

        outputFile = self.parameterAsOutputLayer(parameters, self.MOVED_OUTLETS, context)
        arguments.append("-om")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
