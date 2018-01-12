# -*- coding: utf-8 -*-

"""
***************************************************************************
    peukerdouglas.py
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

class PeukerDouglas(TauDemAlgorithm):

    PIT_FILLED = "PIT_FILLED"
    CENTER_WEIGHT = "CENTER_WEIGHT"
    SIDE_WEIGHT = "SIDE_WEIGHT"
    DIAGONAL_WEIGHT = "DIAGONAL_WEIGHT"
    STREAM_SOURCE = "STREAM_SOURCE"

    def name(self):
        return "peukerdouglas"

    def displayName(self):
        return self.tr("Peuker Douglas")

    def group(self):
        return self.tr("Stream network analysis")

    def groupId(self):
        return "sreamnalysis"

    def tags(self):
        return self.tr("dem,hydrology,smooth,peuker,douglas").split(",")

    def shortHelpString(self):
        return self.tr("Creates an indicator grid (1, 0) of valley form grid "
                       "cells according to the Peuker and Douglas algorithm.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/PeukerDouglas.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.PIT_FILLED,
                                                            self.tr("Pit filled elevation")))
        self.addParameter(QgsProcessingParameterNumber(self.CENTER_WEIGHT,
                                                       self.tr("Center smoothing weight"),
                                                       QgsProcessingParameterNumber.Double,
                                                       0.4,
                                                       False))
        self.addParameter(QgsProcessingParameterNumber(self.SIDE_WEIGHT,
                                                       self.tr("Side smoothing weight"),
                                                       QgsProcessingParameterNumber.Double,
                                                       0.1,
                                                       False))
        self.addParameter(QgsProcessingParameterNumber(self.DIAGONAL_WEIGHT,
                                                       self.tr("Diagonal smoothing weight"),
                                                       QgsProcessingParameterNumber.Double,
                                                       0.05,
                                                       False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.STREAM_SOURCE,
                                                                  self.tr("D8 slope")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-fel")
        arguments.append(self.parameterAsRasterLayer(parameters, self.PIT_FILLED, context).source())

        arguments.append("-par")
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.CENTER_WEIGHT, context)))
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.SIDE_WEIGHT, context)))
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.DIAGONAL_WEIGHT, context)))

        outputFile = self.parameterAsOutputLayer(parameters, self.STREAM_SOURCE, context)
        arguments.append("-ss")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
