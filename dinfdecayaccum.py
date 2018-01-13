# -*- coding: utf-8 -*-

"""
***************************************************************************
    dinfdecayaccum.py
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


class DinfDecayAccum(TauDemAlgorithm):

    DINF_FLOWDIR = "DINF_FLOWDIR"
    DECAY_MULTIPLIER = "DECAY_MULTIPLIER"
    WEIGHT_GRID = "WEIGHT_GRID"
    OUTLETS = "OUTLETS"
    EDGE_CONTAMINATION = "EDGE_CONTAMINATION"
    DECAYED_AREA = "DECAYED_AREA"

    def name(self):
        return "dinfdecayaccum"

    def displayName(self):
        return self.tr("D-infinity decaying accumulation")

    def group(self):
        return self.tr("Specialized grid analysis")

    def groupId(self):
        return "specializedanalysis"

    def tags(self):
        return self.tr("dem,hydrology,d8,stream,distance").split(",")

    def shortHelpString(self):
        return self.tr("Creates a grid of the accumulated quantity at each "
                       "location in the domain where the quantity accumulates "
                       "with the D-infinity flow field, but is subject to "
                       "first order decay in moving from cell to cell.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/DInfinityDecayingAccumulation.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.DINF_FLOWDIR,
                                                            self.tr("D-infinity flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.DECAY_MULTIPLIER,
                                                            self.tr("Decay multiplier")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.WEIGHT_GRID,
                                                            self.tr("Weight grid"),
                                                            optional=True))
        self.addParameter(QgsProcessingParameterVectorLayer(self.OUTLETS,
                                                            self.tr("Outlets"),
                                                            types=[QgsProcessing.TypeVectorPoint],
                                                            optional=True))
        self.addParameter(QgsProcessingParameterBoolean(self.EDGE_CONTAMINATION,
                                                        self.tr("Check for edge contamination"),
                                                        defaultValue=False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.DECAYED_AREA,
                                                                  self.tr("Decayed specific catchment area")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-ang")
        arguments.append(self.parameterAsRasterLayer(parameters, self.DINF_FLOWDIR, context).source())
        arguments.append("-dm")
        arguments.append(self.parameterAsRasterLayer(parameters, self.DECAY_MULTIPLIER, context).source())

        weight = self.parameterAsRasterLayer(parameters, self.WEIGHT_GRID, context)
        if weight:
            arguments.append("-wg")
            arguments.append(weight.source())

        outlets = self.parameterAsVectorLayer(parameters, self.OUTLETS, context)
        if outlets:
            arguments.append("-o")
            arguments.append(outlets.source())

        edgeContamination = self.parameterAsBool(parameters, self.EDGE_CONTAMINATION, context)
        if edgeContamination:
            arguments.append("-nc")

        outputFile = self.parameterAsOutputLayer(parameters, self.DECAYED_AREA, context)
        arguments.append("-dsca")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
