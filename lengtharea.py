# -*- coding: utf-8 -*-

"""
***************************************************************************
    lengtharea.py
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


class LengthArea(TauDemAlgorithm):

    LENGTH = "LENGTH"
    CONTRIB_AREA = "CONTRIB_AREA"
    THRESHOLD = "THRESHOLD"
    EXPONENT = "EXPONENT"
    STREAM_SOURCE = "STREAM_SOURCE"

    def name(self):
        return "lengtharea"

    def displayName(self):
        return self.tr("Length area stream source")

    def group(self):
        return self.tr("Stream network analysis")

    def groupId(self):
        return "streamanalysis"

    def tags(self):
        return self.tr("dem,hydrology,dem,threshold,compare").split(",")

    def shortHelpString(self):
        return self.tr("Creates an indicator grid (1, 0) that evaluates "
                       "A >= M·(L^y) based on upslope path length, D8 "
                       "contributing area grid inputs, and parameters M and y.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/LengthAreaStreamSource.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.LENGTH,
                                                            self.tr("Maximum upslope length")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.CONTRIB_AREA,
                                                            self.tr("Contributing area")))
        self.addParameter(QgsProcessingParameterNumber(self.THRESHOLD,
                                                       self.tr("Multiplier (M)"),
                                                       QgsProcessingParameterNumber.Double,
                                                       0.03,
                                                       False))
        self.addParameter(QgsProcessingParameterNumber(self.EXPONENT,
                                                       self.tr("Exponent (y)"),
                                                       QgsProcessingParameterNumber.Double,
                                                       1.3,
                                                       False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.STREAM_SOURCE,
                                                                  self.tr("Stream source")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-plen")
        arguments.append(self.parameterAsRasterLayer(parameters, self.LENGTH, context).source())
        arguments.append("-ad8")
        arguments.append(self.parameterAsRasterLayer(parameters, self.CONTRIB_AREA, context).source())

        arguments.append("-par")
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.THRESHOLD, context)))
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.EXPONENT, context)))

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
