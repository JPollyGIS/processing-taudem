# -*- coding: utf-8 -*-

"""
***************************************************************************
    d8flowdir.py
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

class D8FlowDir(TauDemAlgorithm):

    PIT_FILLED = "PIT_FILLED"
    D8_FLOWDIR = "D8_FLOWDIR"
    D8_SLOPE = "D8_SLOPE"

    def name(self):
        return 'd8flowdir'

    def displayName(self):
        return self.tr("D8 flow directions")

    def group(self):
        return self.tr("Basic grid analysis")

    def groupId(self):
        return "basicanalysis"

    def tags(self):
        return self.tr("dem,hydrology,d8,flow directions,slope").split(",")

    def shortHelpString(self):
        return self.tr("Calculates 2 grids. The first contains the D8 Flow "
                       "directions which are defined, for each cell, as the "
                       "direction of one of its eight adjacent or diagonal "
                       "neighbors with the steepest downward slope. "
                       "The second contains the slope, as evaluated in the "
                       "direction of steepest descent and is reported as "
                       "drop/distance.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/D8FlowDirections.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.PIT_FILLED,
                                                            self.tr("Pit filled elevation")))

        self.addParameter(QgsProcessingParameterRasterDestination(self.D8_FLOWDIR,
                                                                  self.tr("D8 flow directions")))
        self.addParameter(QgsProcessingParameterRasterDestination(self.D8_SLOPE,
                                                                  self.tr("D8 slope")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-fel")
        arguments.append(self.parameterAsRasterLayer(parameters, self.PIT_FILLED, context).source())

        arguments.append("-p")
        arguments.append(self.parameterAsOutputLayer(parameters, self.D8_FLOWDIR, context))
        arguments.append("-sd8")
        arguments.append(self.parameterAsOutputLayer(parameters, self.D8_SLOPE, context))

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
