# -*- coding: utf-8 -*-

"""
***************************************************************************
    d8hdisttostrm.py
    ---------------------
    Date                 : January 2012
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

from qgis.core import (QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterFileDestination
                      )

from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils


class D8HDistToStrm(TauDemAlgorithm):

    D8_FLOWDIR = "D8_FLOWDIR"
    STREAM_RASTER = "STREAM_RASTER"
    TRESHOLD = "TRESHOLD"
    STREAMS_DISTANCE = "STREAMS_DISTANCE"

    def name(self):
        return "d8hdisttostrm"

    def displayName(self):
        return self.tr("D8 distance to streams")

    def group(self):
        return self.tr("Specialized grid analysis")

    def groupId(self):
        return "specializedalysis"

    def tags(self):
        return self.tr("dem,hydrology,d8,stream,distance").split(",")

    def shortHelpString(self):
        return self.tr("Computes the horizontal distance to stream for each "
                       "grid cell, moving downslope according to the D8 flow "
                       "model, until a stream grid cell is encountered.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/D8DistanceToStreams.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.D8_FLOWDIR,
                                                            self.tr("D8 flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.STREAM_RASTER,
                                                            self.tr("Stream raster")))
        self.addParameter(QgsProcessingParameterNumber(self.TRESHOLD,
                                                       self.tr("Threshold"),
                                                       QgsProcessingParameterNumber.Double,
                                                       50,
                                                       True))
        self.addParameter(QgsProcessingParameterRasterDestination(self.STREAMS_DISTANCE,
                                                                  self.tr("Distance to streams")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-p")
        arguments.append(self.parameterAsRasterLayer(parameters, self.D8_FLOWDIR, context).source())
        arguments.append("-src")
        arguments.append(self.parameterAsRasterLayer(parameters, self.STREAM_RASTER, context).source())
        arguments.append("-thresh")
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.TRESHOLD, context)))

        outputFile = self.parameterAsOutputLayer(parameters, self.STREAMS_DISTANCE, context)
        arguments.append("-dist")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
