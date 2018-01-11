# -*- coding: utf-8 -*-

"""
***************************************************************************
    pitremove.py
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
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterDestination
                      )

from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils

class PitRemove(TauDemAlgorithm):

    ELEVATION = "ELEVATION"
    DEPRESSION_MASK = "DEPRESSION_MASK"
    FOUR_NEIGHBOURS = "FOUR_NEIGHBOURS"
    PIT_FILLED = "PIT_FILLED"

    def name(self):
        return 'pitremove'

    def displayName(self):
        return self.tr("Pit remove")

    def group(self):
        return self.tr("Basic grid analysis")

    def groupId(self):
        return "basicanalysis"

    def tags(self):
        return self.tr("dem,hydrology,pit,remove").split(",")

    def shortHelpString(self):
        return self.tr("Identifies all pits in the DEM and raises their "
                       "elevation to the level of the lowest pour point "
                       "around their edge.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/PitRemove.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.ELEVATION,
                                                            self.tr("Elevation")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.DEPRESSION_MASK,
                                                            self.tr("Depression mask "),
                                                            optional=True))
        self.addParameter(QgsProcessingParameterBoolean(self.FOUR_NEIGHBOURS,
                                                        self.tr("Consider only 4 way neighbors"),
                                                        defaultValue=False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.PIT_FILLED,
                                                                  self.tr("Pit removed elevation")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-z")
        arguments.append(self.parameterAsRasterLayer(parameters, self.ELEVATION, context).source())

        mask = self.parameterAsRasterLayer(parameters, self.DEPRESSION_MASK, context)
        if mask:
            arguments.append("-depmask")
            arguments.append(mask.source())

        fourWay = self.parameterAsBool(parameters, self.FOUR_NEIGHBOURS, context)
        if fourWay:
            arguments.append("-4way")

        outputFile = self.parameterAsOutputLayer(parameters, self.PIT_FILLED, context)
        arguments.append("-fel")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
