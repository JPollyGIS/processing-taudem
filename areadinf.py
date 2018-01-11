# -*- coding: utf-8 -*-

"""
***************************************************************************
    areadinf.py
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

class AreaDinf(TauDemAlgorithm):

    DINF_FLOWDIR = "DINF_FLOWDIR"
    WEIGHT_GRID = "WEIGHT_GRID"
    OUTLETS = "OUTLETS"
    EDGE_CONTAMINATION = "EDGE_CONTAMINATION"
    DINF_CONTRIB_AREA = "DINF_CONTRIB_AREA"

    def name(self):
        return 'areadinf'

    def displayName(self):
        return self.tr("D-infinity contributing area")

    def group(self):
        return self.tr("Basic grid analysis")

    def groupId(self):
        return "basicanalysis"

    def tags(self):
        return self.tr("dem,hydrology,d-infinity,contributing area,catchment area").split(",")

    def shortHelpString(self):
        return self.tr("Calculates a grid of specific catchment area which is "
                       "the contributing area per unit contour length using "
                       "the multiple flow direction D-infinity approach.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/DInfinityContributingArea.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.DINF_FLOWDIR,
                                                            self.tr("D-infinity flow directions")))
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

        self.addParameter(QgsProcessingParameterRasterDestination(self.DINF_CONTRIB_AREA,
                                                                  self.tr("D-infinity specific catchment area")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-ang")
        arguments.append(self.parameterAsRasterLayer(parameters, self.DINF_FLOWDIR, context).source())

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

        outputFile = self.parameterAsOutputLayer(parameters, self.DINF_CONTRIB_AREA, context)
        arguments.append("-sca")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
