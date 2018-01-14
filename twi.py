# -*- coding: utf-8 -*-

"""
***************************************************************************
    twi.py
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

class Twi(TauDemAlgorithm):

    SLOPE = "SLOPE"
    CONTRIB_AREA = "CONTRIB_AREA"
    TWI = "TWI"

    def name(self):
        return "twi"

    def displayName(self):
        return self.tr("Topographic wetness index")

    def group(self):
        return self.tr("Specialized grid analysis")

    def groupId(self):
        return "specializedanalysis"

    def tags(self):
        return self.tr("dem,hydrology,twi,index,topographic,wetness").split(",")

    def shortHelpString(self):
        return self.tr("Calculates the ratio of the natural log of the specific "
                       "catchment area (contributing area) to slope, ln(a/S), "
                       "or ln(a/tan (beta)).")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/TopographicWetnessIndex.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.SLOPE,
                                                            self.tr("Slope")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.CONTRIB_AREA,
                                                            self.tr("Specific catchment area")))

        self.addParameter(QgsProcessingParameterRasterDestination(self.TWI,
                                                                  self.tr("Wetness index")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-slp")
        arguments.append(self.parameterAsRasterLayer(parameters, self.SLOPE, context).source())
        arguments.append("-sca")
        arguments.append(self.parameterAsRasterLayer(parameters, self.CONTRIB_AREA, context).source())

        arguments.append("-twi")
        arguments.append(self.parameterAsOutputLayer(parameters, self.TWI, context))

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
