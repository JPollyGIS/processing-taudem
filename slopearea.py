# -*- coding: utf-8 -*-

"""
***************************************************************************
    slopearea.py
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

from qgis.core import (QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterDestination
                      )

from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils


class SlopeArea(TauDemAlgorithm):

    SLOPE = "SLOPE"
    AREA = "AREA"
    SLOPE_EXPONENT = "SLOPE_EXPONENT"
    AREA_EXPONENT = "AREA_EXPONENT"
    SLOPE_AREA = "SLOPE_AREA"

    def name(self):
        return "slopearea"

    def displayName(self):
        return self.tr("Slope area combination")

    def group(self):
        return self.tr("Stream network analysis")

    def groupId(self):
        return "sreamnalysis"

    def tags(self):
        return self.tr("dem,hydrology,dem,threshold,compare").split(",")

    def shortHelpString(self):
        return self.tr("Creates a grid of slope-area values = (S^m)·(A^n) "
                       "based on slope and specific catchment area grid "
                       "inputs, and parameters m and n.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/SlopeAreaCombination.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.SLOPE,
                                                            self.tr("Slope")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.AREA,
                                                            self.tr("Area")))
        self.addParameter(QgsProcessingParameterNumber(self.SLOPE_EXPONENT,
                                                       self.tr("Slope exponent"),
                                                       QgsProcessingParameterNumber.Double,
                                                       2.0,
                                                       False))
        self.addParameter(QgsProcessingParameterNumber(self.AREA_EXPONENT,
                                                       self.tr("Area exponent"),
                                                       QgsProcessingParameterNumber.Double,
                                                       1.0,
                                                       False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.SLOPE_AREA,
                                                                  self.tr("Slope area")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-slp")
        arguments.append(self.parameterAsRasterLayer(parameters, self.SLOPE, context).source())
        arguments.append("-sca")
        arguments.append(self.parameterAsRasterLayer(parameters, self.AREA, context).source())

        arguments.append("-par")
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.SLOPE_EXPONENT, context)))
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.AREA_EXPONENT, context)))

        outputFile = self.parameterAsOutputLayer(parameters, self.SLOPE_AREA, context)
        arguments.append("-sa")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
