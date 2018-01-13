# -*- coding: utf-8 -*-

"""
***************************************************************************
    threshold.py
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

class Threshold(TauDemAlgorithm):

    ACCUM_STREAM_SOURCE = "ACCUM_STREAM_SOURCE"
    MASK_GRID = "MASK_GRID"
    THRESHOLD = "THRESHOLD"
    STREAM_RASTER = "STREAM_RASTER"

    def name(self):
        return "threshold"

    def displayName(self):
        return self.tr("Stream definition by threshold")

    def group(self):
        return self.tr("Stream network analysis")

    def groupId(self):
        return "streamanalysis"

    def tags(self):
        return self.tr("dem,hydrology,dem,threshold,compare").split(",")

    def shortHelpString(self):
        return self.tr("Operates on any grid and outputs an indicator (1, 0) "
                       "grid identifing cells with input values >= the "
                       "threshold value.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/StreamDefinitionByThreshold.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.ACCUM_STREAM_SOURCE,
                                                            self.tr("Accumulated stream source")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.MASK_GRID,
                                                            self.tr("Mask grid"),
                                                            optional=True))
        self.addParameter(QgsProcessingParameterNumber(self.THRESHOLD,
                                                       self.tr("Threshold"),
                                                       QgsProcessingParameterNumber.Double,
                                                       100.0,
                                                       False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.STREAM_RASTER,
                                                                  self.tr("Stream raster")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-ssa")
        arguments.append(self.parameterAsRasterLayer(parameters, self.ACCUM_STREAM_SOURCE, context).source())

        mask = self.parameterAsRasterLayer(parameters, self.MASK_GRID, context)
        if mask:
            arguments.append("-mask")
            arguments.append(mask.source())

        arguments.append("-thresh")
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.THRESHOLD, context)))

        outputFile = self.parameterAsOutputLayer(parameters, self.STREAM_RASTER, context)
        arguments.append("-src")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
