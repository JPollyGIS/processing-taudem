# -*- coding: utf-8 -*-

"""
***************************************************************************
    slopeavedown.py
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
                       QgsProcessingParameterRasterDestination
                      )
from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils


class SlopeAveDown(TauDemAlgorithm):

    PIT_FILLED = "PIT_FILLED"
    D8_FLOWDIR = "D8_FLOWDIR"
    DISTANCE = "DISTANCE"
    SLOPE_DOWN = "SLOPE_DOWN"

    def name(self):
        return "slopeavedown"

    def displayName(self):
        return self.tr("Slope average down")

    def group(self):
        return self.tr("Specialized grid analysis")

    def groupId(self):
        return "specializedanalysis"

    def tags(self):
        return self.tr("dem,hydrology,d8,slope,downslope").split(",")

    def shortHelpString(self):
        return self.tr("Computes slope in a D8 downslope direction averaged "
                       "over a user selected distance.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/SlopeAverageDown.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.PIT_FILLED,
                                                            self.tr("Pit filled elevation")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.D8_FLOWDIR,
                                                            self.tr("D8 flow directions")))
        self.addParameter(QgsProcessingParameterNumber(self.DISTANCE,
                                                       self.tr("Downslope distance"),
                                                       QgsProcessingParameterNumber.Double,
                                                       50,
                                                       True))

        self.addParameter(QgsProcessingParameterRasterDestination(self.SLOPE_DOWN,
                                                                  self.tr("Slope average down")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-fel")
        arguments.append(self.parameterAsRasterLayer(parameters, self.PIT_FILLED, context).source())
        arguments.append("-p")
        arguments.append(self.parameterAsRasterLayer(parameters, self.D8_FLOWDIR, context).source())
        arguments.append("-dn")
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.DISTANCE, context)))

        outputFile = self.parameterAsOutputLayer(parameters, self.SLOPE_DOWN, context)
        arguments.append("-slpd")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
