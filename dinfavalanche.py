# -*- coding: utf-8 -*-

"""
***************************************************************************
    dinfavalanche.py
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

from qgis.core import (QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterDestination
                      )
from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils


class DinfAvalanche(TauDemAlgorithm):

    PIT_FILLED = "PIT_FILLED"
    DINF_FLOWDIR = "DINF_FLOWDIR"
    AVALANCHE_SOURCE = "AVALANCHE_SOURCE"
    THRESHOLD = "THRESHOLD"
    ANGLE = "ANGLE"
    DIRECT = "DIRECT"
    AVALANCHE_RUNOUT = "AVALANCHE_RUNOUT"
    DISTANCE_DOWN = "DISTANCE_DOWN"

    def name(self):
        return "dinfavalanche"

    def displayName(self):
        return self.tr("D-infinity avalanche runout")

    def group(self):
        return self.tr("Specialized grid analysis")

    def groupId(self):
        return "specializedanalysis"

    def tags(self):
        return self.tr("dem,hydrology,d-infinity,avalanche").split(",")

    def shortHelpString(self):
        return self.tr("Identifies an avalanche's affected area and the flow "
                       "path length to each cell in that affected area.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/DInfinityAvalancheRunout.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.PIT_FILLED,
                                                            self.tr("Pit filled elevation")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.DINF_FLOWDIR,
                                                            self.tr("D-infinity flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.AVALANCHE_SOURCE,
                                                            self.tr("Avalanche source site")))
        self.addParameter(QgsProcessingParameterNumber(self.THRESHOLD,
                                                       self.tr("Proportion threshold"),
                                                       QgsProcessingParameterNumber.Double,
                                                       0.2,
                                                       True))
        self.addParameter(QgsProcessingParameterNumber(self.ANGLE,
                                                       self.tr("Alpha angle threshold"),
                                                       QgsProcessingParameterNumber.Double,
                                                       18,
                                                       True))
        self.addParameter(QgsProcessingParameterBoolean(self.DIRECT,
                                                        self.tr("Measure distance as a straight line"),
                                                        defaultValue=False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.AVALANCHE_RUNOUT,
                                                                  self.tr("Runout zone")))
        self.addParameter(QgsProcessingParameterRasterDestination(self.DISTANCE_DOWN,
                                                                  self.tr("Path distance")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-fel")
        arguments.append(self.parameterAsRasterLayer(parameters, self.PIT_FILLED, context).source())
        arguments.append("-ang")
        arguments.append(self.parameterAsRasterLayer(parameters, self.DINF_FLOWDIR, context).source())
        arguments.append("-ass")
        arguments.append(self.parameterAsRasterLayer(parameters, self.AVALANCHE_SOURCE, context).source())
        arguments.append("-thresh")
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.THRESHOLD, context)))
        arguments.append("-alpha")
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.ANGLE, context)))

        direct = self.parameterAsBool(parameters, self.DIRECT, context)
        if edgeContamination:
            arguments.append("-direct")

        outputFile = self.parameterAsOutputLayer(parameters, self.AVALANCHE_RUNOUT, context)
        arguments.append("-rz")
        arguments.append(outputFile)

        outputFile = self.parameterAsOutputLayer(parameters, self.DISTANCE_DOWN, context)
        arguments.append("-dfs")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
