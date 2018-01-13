# -*- coding: utf-8 -*-

"""
***************************************************************************
    slopearearatio.py
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
                       QgsProcessingParameterRasterDestination
                      )

from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils


class SlopeAreaRatio(TauDemAlgorithm):

    SLOPE = "SLOPE"
    AREA = "AREA"
    SLOPE_AREA_RATIO = "SLOPE_AREA_RATIO"

    def name(self):
        return "slopearearatio"

    def displayName(self):
        return self.tr("Slope over area ratio")

    def group(self):
        return self.tr("Specialized grid analysis")

    def groupId(self):
        return "specializedanalysis"

    def tags(self):
        return self.tr("dem,hydrology,slope,catchment,area").split(",")

    def shortHelpString(self):
        return self.tr("Calculates the ratio of the slope to the specific "
                       "catchment (contributing) area.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/SlopeOverAreaRatio.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.SLOPE,
                                                            self.tr("Slope")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.AREA,
                                                            self.tr("Specific catchment area")))

        self.addParameter(QgsProcessingParameterRasterDestination(self.SLOPE_AREA_RATIO,
                                                                  self.tr("Slope area ratio")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-slp")
        arguments.append(self.parameterAsRasterLayer(parameters, self.SLOPE, context).source())
        arguments.append("-sca")
        arguments.append(self.parameterAsRasterLayer(parameters, self.AREA, context).source())

        outputFile = self.parameterAsOutputLayer(parameters, self.SLOPE_AREA_RATIO, context)
        arguments.append("-sar")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
