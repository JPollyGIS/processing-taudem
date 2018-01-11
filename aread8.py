# -*- coding: utf-8 -*-

"""
***************************************************************************
    aread8.py
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

from qgis.core import (QgsProcessing,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterDestination
                      )

from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils

class AreaD8(TauDemAlgorithm):

    D8_FLOWDIR = "D8_FLOWDIR"
    WEIGHT_GRID = "WEIGHT_GRID"
    OUTLETS = "OUTLETS"
    EDGE_CONTAMINATION = "EDGE_CONTAMINATION"
    D8_CONTRIB_AREA = "D8_CONTRIB_AREA"

    def name(self):
        return 'aread8'

    def displayName(self):
        return self.tr("D8 contributing area")

    def group(self):
        return self.tr("Basic grid analysis")

    def groupId(self):
        return "basicanalysis"

    def tags(self):
        return self.tr("dem,hydrology,d8,contributing area,catchment area").split(",")

    def shortHelpString(self):
        return self.tr("Calculates a grid of contributing areas using the "
                       "single direction D8 flow model.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/D8ContributingArea.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.D8_FLOWDIR,
                                                            self.tr("D8 flow directions")))
        self.addParameter(QgsProcessingParameterVectorLayer(self.OUTLETS,
                                                            self.tr("Outlets"),
                                                            types=[QgsProcessing.TypeVectorPoint],
                                                            optional=True))
        self.addParameter(QgsProcessingParameterRasterLayer(self.WEIGHT_GRID,
                                                            self.tr("Weight grid"),
                                                            optional=True))
        self.addParameter(QgsProcessingParameterBoolean(self.EDGE_CONTAMINATION,
                                                        self.tr("Check for edge contamination"),
                                                        defaultValue=False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.D8_CONTRIB_AREA,
                                                                  self.tr("D8 specific catchment area")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-p")
        arguments.append(self.parameterAsRasterLayer(parameters, self.D8_FLOWDIR, context).source())

        outlets = self.parameterAsVectorLayer(parameters, self.OUTLETS, context)
        if outlets:
            arguments.append("-o")
            arguments.append(outlets.source())

        weight = self.parameterAsRasterLayer(parameters, self.WEIGHT_GRID, context)
        if weight:
            arguments.append("-wg")
            arguments.append(weight.source())

        edgeContamination = self.parameterAsBool(parameters, self.EDGE_CONTAMINATION, context)
        if edgeContamination:
            arguments.append("-nc")

        outputFile = self.parameterAsOutputLayer(parameters, self.D8_CONTRIB_AREA, context)
        arguments.append("-ad8")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
