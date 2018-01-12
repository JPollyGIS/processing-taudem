# -*- coding: utf-8 -*-

"""
***************************************************************************
    streamnet.py
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
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterFileDestination
                      )

from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils


class StreamNet(TauDemAlgorithm):

    PIT_FILLED = "PIT_FILLED"
    D8_FLOWDIR = "D8_FLOWDIR"
    D8_CONTRIB_AREA = "D8_CONTRIB_AREA"
    STREAM_RASTER = "STREAM_RASTER"
    OUTLETS = "OUTLETS"
    SINGLE_WATERSHED = "SINGLE_WATERSHED"
    STREAM_ORDER = "STREAM_ORDER"
    WATERSHED = "WATERSHED"
    STREAM_REACH = "STREAM_REACH"
    NETWORK_CONNECTIVITY = "NETWORK_CONNECTIVITY"
    NETWORK_COORDINATES = "NETWORK_COORDINATES"

    def name(self):
        return "streamnet"

    def displayName(self):
        return self.tr("Stream reach and watershed")

    def group(self):
        return self.tr("Stream network analysis")

    def groupId(self):
        return "sreamnalysis"

    def tags(self):
        return self.tr("dem,hydrology,dem,stream,network,watershed").split(",")

    def shortHelpString(self):
        return self.tr("Produces a vector network from the Stream Raster grid "
                       "by tracing down from each source grid cell.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/StreamReachAndWatershed.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.PIT_FILLED,
                                                            self.tr("Pit filled elevation")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.D8_FLOWDIR,
                                                            self.tr("D8 flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.D8_CONTRIB_AREA,
                                                            self.tr("D8 contributing area")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.STREAM_RASTER,
                                                            self.tr("Stream raster")))
        self.addParameter(QgsProcessingParameterVectorLayer(self.OUTLETS,
                                                            self.tr("Outlets"),
                                                            types=[QgsProcessing.TypeVectorPoint],
                                                            optional=True))
        self.addParameter(QgsProcessingParameterBoolean(self.SINGLE_WATERSHED,
                                                        self.tr("Delineate single watershed"),
                                                        defaultValue=False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.STREAM_ORDER,
                                                                  self.tr("Stream order")))
        self.addParameter(QgsProcessingParameterRasterDestination(self.WATERSHED,
                                                                  self.tr("Watershed")))
        self.addParameter(QgsProcessingParameterVectorDestination(self.STREAM_REACH,
                                                                  self.tr('Channel network'),
                                                                  QgsProcessing.TypeVectorLine))
        self.addParameter(QgsProcessingParameterFileDestination(self.NETWORK_CONNECTIVITY,
                                                                self.tr("Network connectivity tree"),
                                                                self.tr("Data files (*.dat)")))
        self.addParameter(QgsProcessingParameterFileDestination(self.NETWORK_COORDINATES,
                                                                self.tr("Network coordinates"),
                                                                self.tr("Data files (*.dat)")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-fel")
        arguments.append(self.parameterAsRasterLayer(parameters, self.PIT_FILLED, context).source())
        arguments.append("-p")
        arguments.append(self.parameterAsRasterLayer(parameters, self.D8_FLOWDIR, context).source())
        arguments.append("-ad8")
        arguments.append(self.parameterAsRasterLayer(parameters, self.D8_CONTRIB_AREA, context).source())
        arguments.append("-src")
        arguments.append(self.parameterAsRasterLayer(parameters, self.STREAM_RASTER, context).source())

        outlets = self.parameterAsVectorLayer(parameters, self.OUTLETS, context)
        if outlets:
            arguments.append("-o")
            arguments.append(outlets.source())

        singleWatershed = self.parameterAsBool(parameters, self.SINGLE_WATERSHED, context)
        if singleWatershed:
            arguments.append("-sw")

        outputFile = self.parameterAsOutputLayer(parameters, self.STREAM_ORDER, context)
        arguments.append("-ord")
        arguments.append(outputFile)

        outputFile = self.parameterAsOutputLayer(parameters, self.WATERSHED, context)
        arguments.append("-w")
        arguments.append(outputFile)

        outputFile = self.parameterAsOutputLayer(parameters, self.STREAM_REACH, context)
        arguments.append("-net")
        arguments.append(outputFile)

        outputFile = self.parameterAsFileOutput(parameters, self.NETWORK_CONNECTIVITY, context)
        arguments.append("-tree")
        arguments.append(outputFile)

        outputFile = self.parameterAsFileOutput(parameters, self.NETWORK_COORDINATES, context)
        arguments.append("-coord")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
