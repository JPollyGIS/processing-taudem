# -*- coding: utf-8 -*-

"""
***************************************************************************
    dinfflowdir.py
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

class DinfFlowDir(TauDemAlgorithm):

    PIT_FILLED = "PIT_FILLED"
    DINF_FLOWDIR = "DINF_FLOWDIR"
    DINF_SLOPE = "DINF_SLOPE"

    def name(self):
        return 'dinfflowdir'

    def displayName(self):
        return self.tr("D-infinity flow directions")

    def group(self):
        return self.tr("Basic grid analysis")

    def groupId(self):
        return "basicanalysis"

    def tags(self):
        return self.tr("dem,hydrology,d-infinity,flow directions,slope").split(",")

    def shortHelpString(self):
        return self.tr("Assigns a flow direction based on the D-infinity flow "
                       "method using the steepest slope of a triangular facet "
                       "(Tarboton, 1997, 'A New Method for the Determination "
                       "of Flow Directions and Contributing Areas in Grid "
                       "Digital Elevation Models', Water Resources Research, "
                       "33(2): 309-319)")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/DInfinityFlowDirections.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.PIT_FILLED,
                                                            self.tr("Pit filled elevation")))

        self.addParameter(QgsProcessingParameterRasterDestination(self.DINF_FLOWDIR,
                                                                  self.tr("D-infinity flow directions")))
        self.addParameter(QgsProcessingParameterRasterDestination(self.DINF_SLOPE,
                                                                  self.tr("D-infinity slope")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-fel")
        arguments.append(self.parameterAsRasterLayer(parameters, self.PIT_FILLED, context).source())

        arguments.append("-ang")
        arguments.append(self.parameterAsOutputLayer(parameters, self.DINF_FLOWDIR, context))
        arguments.append("-slp")
        arguments.append(self.parameterAsOutputLayer(parameters, self.DINF_SLOPE, context))

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
