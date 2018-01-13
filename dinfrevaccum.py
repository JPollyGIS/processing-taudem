# -*- coding: utf-8 -*-

"""
***************************************************************************
    dinfrevaccum.py
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


class DinfRevAccum(TauDemAlgorithm):

    DINF_FLOWDIR = "DINF_FLOWDIR"
    WEIGHT_GRID = "WEIGHT_GRID"
    REVERSE_ACCUM = "REVERSE_ACCUM"
    MAX_DOWNSLOPE = "MAX_DOWNSLOPE"

    def name(self):
        return "dinfrevaccum"

    def displayName(self):
        return self.tr("D-infinity reverse accumulation")

    def group(self):
        return self.tr("Specialized grid analysis")

    def groupId(self):
        return "specializedanalysis"

    def tags(self):
        return self.tr("dem,hydrology,d-infinity,accumulation,reverse").split(",")

    def shortHelpString(self):
        return self.tr("Works in a similar way to evaluation of weighted "
                       "contributing area, except that the accumulation is by "
                       "propagating the weight loadings upslope along the "
                       "reverse of the flow directions to accumulate the "
                       "quantity of weight loading downslope from each grid "
                       "cell.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/DInfinityReverseAccumulation.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.DINF_FLOWDIR,
                                                            self.tr("D-infinity flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.WEIGHT_GRID,
                                                            self.tr("Weight grid")))

        self.addParameter(QgsProcessingParameterRasterDestination(self.REVERSE_ACCUM,
                                                                  self.tr("Reverse accumulation")))
        self.addParameter(QgsProcessingParameterRasterDestination(self.MAX_DOWNSLOPE,
                                                                  self.tr("Maximum downslope")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-ang")
        arguments.append(self.parameterAsRasterLayer(parameters, self.DINF_FLOWDIR, context).source())
        arguments.append("-wg")
        arguments.append(self.parameterAsRasterLayer(parameters, self.WEIGHT_GRID, context).source())

        outputFile = self.parameterAsOutputLayer(parameters, self.REVERSE_ACCUM, context)
        arguments.append("-racc")
        arguments.append(outputFile)

        outputFile = self.parameterAsOutputLayer(parameters, self.MAX_DOWNSLOPE, context)
        arguments.append("-dmax")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
