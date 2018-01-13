# -*- coding: utf-8 -*-

"""
***************************************************************************
    dinfupdependence.py
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


class DinfUpDependence(TauDemAlgorithm):

    DINF_FLOWDIR = "DINF_FLOWDIR"
    DISTURBANCE = "DISTURBANCE"
    UPSLOPE_DEPENDENCE = "UPSLOPE_DEPENDENCE"

    def name(self):
        return "dinfupdependence"

    def displayName(self):
        return self.tr("D-infinity upslope dependence")

    def group(self):
        return self.tr("Specialized grid analysis")

    def groupId(self):
        return "specializedanalysis"

    def tags(self):
        return self.tr("dem,hydrology,d8,stream,distance").split(",")

    def shortHelpString(self):
        return self.tr("Quantifies the amount each grid cell in the domain "
                       "contributes to a destination set of grid cells.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/DInfinityUpslopeDependence.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.DINF_FLOWDIR,
                                                            self.tr("D-infinity flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.DISTURBANCE,
                                                            self.tr("Disturbance")))

        self.addParameter(QgsProcessingParameterRasterDestination(self.UPSLOPE_DEPENDENCE,
                                                                  self.tr("Upslope dependence")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-and")
        arguments.append(self.parameterAsRasterLayer(parameters, self.DINF_FLOWDIR, context).source())
        arguments.append("-dg")
        arguments.append(self.parameterAsRasterLayer(parameters, self.DISTURBANCE, context).source())

        outputFile = self.parameterAsOutputLayer(parameters, self.UPSLOPE_DEPENDENCE, context)
        arguments.append("-dep")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
