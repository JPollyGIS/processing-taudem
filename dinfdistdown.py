# -*- coding: utf-8 -*-

"""
***************************************************************************
    dinfdistdown.py
    ---------------------
    Date                 : June 2012
    Copyright            : (C) 2012-2018 by Alexander Bruy
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
__date__ = 'June 2012'
__copyright__ = '(C) 2012-2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
from collections import OrderedDict

from qgis.core import (QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterDestination
                      )
from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils


class DinfDistDown(TauDemAlgorithm):

    PIT_FILLED = "PIT_FILLED"
    DINF_FLOWDIR = "DINF_FLOWDIR"
    STREAM_RASTER = "STREAM_RASTER"
    WEIGHT_GRID = "WEIGHT_GRID"
    STATISTICAL_METHOD = "STATISTICAL_METHOD"
    DISTANCE_METHOD = "DISTANCE_METHOD"
    EDGE_CONTAMINATION = "EDGE_CONTAMINATION"
    DISTANCE_DOWN = "DISTANCE_DOWN"

    def name(self):
        return "dinfdistdown"

    def displayName(self):
        return self.tr("D-infinity distance down")

    def group(self):
        return self.tr("Specialized grid analysis")

    def groupId(self):
        return "specializedalysis"

    def tags(self):
        return self.tr("dem,hydrology,d-infinity,downslope,distance").split(",")

    def shortHelpString(self):
        return self.tr("Calculates the distance downslope to a stream using "
                       "the D-infinity flow model.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/DInfinityDistanceDown.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.statisticalMethods = OrderedDict([(self.tr("Average"), "ave"),
                                               (self.tr("Minimum"), "min"),
                                               (self.tr("Maximum"), "max")])

        self.distanceMethods = OrderedDict([(self.tr("Horizontal"), "h"),
                                            (self.tr("Vertical"), "v"),
                                            (self.tr("Pythagoras"), "p"),
                                            (self.tr("Surface"), "s")])

        self.addParameter(QgsProcessingParameterRasterLayer(self.PIT_FILLED,
                                                            self.tr("Pit filled elevation")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.DINF_FLOWDIR,
                                                            self.tr("D-infinity flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.STREAM_RASTER,
                                                            self.tr("Stream raster")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.WEIGHT_GRID,
                                                            self.tr("Weight grid"),
                                                            optional=True))
        self.addParameter(QgsProcessingParameterEnum(self.STATISTICAL_METHOD,
                                                     self.tr("Statistical method"),
                                                     options=[i[0] for i in self.statisticalMethods],
                                                     allowMultiple=False,
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(self.DISTANCE_METHOD,
                                                     self.tr("Distance method"),
                                                     options=[i[0] for i in self.distanceMethods],
                                                     allowMultiple=False,
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterBoolean(self.EDGE_CONTAMINATION,
                                                        self.tr("Check for edge contamination"),
                                                        defaultValue=False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.DISTANCE_DOWN,
                                                                  self.tr("D-infinity drop to stream")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-fel")
        arguments.append(self.parameterAsRasterLayer(parameters, self.PIT_FILLED, context).source())
        arguments.append("-ang")
        arguments.append(self.parameterAsRasterLayer(parameters, self.DINF_FLOWDIR, context).source())
        arguments.append("-src")
        arguments.append(self.parameterAsRasterLayer(parameters, self.STREAM_RASTER, context).source())

        weight = self.parameterAsRasterLayer(parameters, self.WEIGHT_GRID, context)
        if weight:
            arguments.append("-wg")
            arguments.append(weight.source())

        statMethod = self.statiscitalMethods[self.parameterAsEnum(parameters, self.STATISTICAL_METHOD, context)][1]
        distMethod = self.statiscitalMethods[self.parameterAsEnum(parameters, self.DISTANCE_METHOD, context)][1]
        arguments.append("-m")
        arguments.append(statMethod)
        arguments.append(distMethod)

        edgeContamination = self.parameterAsBool(parameters, self.EDGE_CONTAMINATION, context)
        if edgeContamination:
            arguments.append("-nc")

        outputFile = self.parameterAsOutputLayer(parameters, self.DISTANCE_DOWN, context)
        arguments.append("-dd")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
