# -*- coding: utf-8 -*-

"""
***************************************************************************
    d8flowpathextremeup.py
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

class D8FlowPathExtremeUp(TauDemAlgorithm):

    D8_FLOWDIR = "D8_FLOWDIR"
    SLOPE_AREA = "SLOPE_AREA"
    OUTLETS = "OUTLETS"
    MIN_UPSLOPE = "MIN_UPSLOPE"
    EDGE_CONTAMINATION = "EDGE_CONTAMINATION"
    EXTREME_VALUE = "EXTREME_VALUE"

    def name(self):
        return "d8flowpathextremeup"

    def displayName(self):
        return self.tr("D8 Extreme Upslope Value")

    def group(self):
        return self.tr("Stream network analysis")

    def groupId(self):
        return "streamanalysis"

    def tags(self):
        return self.tr("dem,hydrology,d8,upslope,extreme").split(",")

    def shortHelpString(self):
        return self.tr("Evaluates the extreme (either maximum or minimum) "
                       "upslope value from an input grid based on the D8 flow "
                       "model.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/D8ExtremeUpslopeValue.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.D8_FLOWDIR,
                                                            self.tr("D8 flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.SLOPE_AREA,
                                                            self.tr("Slope area")))
        self.addParameter(QgsProcessingParameterVectorLayer(self.OUTLETS,
                                                            self.tr("Outlets"),
                                                            types=[QgsProcessing.TypeVectorPoint],
                                                            optional=True))
        self.addParameter(QgsProcessingParameterBoolean(self.MIN_UPSLOPE,
                                                        self.tr("Calculate minimum upslope value"),
                                                        defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.EDGE_CONTAMINATION,
                                                        self.tr("Check for edge contamination"),
                                                        defaultValue=False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.EXTREME_VALUE,
                                                                  self.tr("Extreme value")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-p")
        arguments.append(self.parameterAsRasterLayer(parameters, self.D8_FLOWDIR, context).source())

        arguments.append("-sa")
        arguments.append(self.parameterAsRasterLayer(parameters, self.SLOPE_AREA, context).source())

        outlets = self.parameterAsVectorLayer(parameters, self.OUTLETS, context)
        if outlets:
            arguments.append("-o")
            arguments.append(outlets.source())

        minUpslope = self.parameterAsBool(parameters, self.MIN_UPSLOPE, context)
        if minUpslope:
            arguments.append("-min")

        edgeContamination = self.parameterAsBool(parameters, self.EDGE_CONTAMINATION, context)
        if edgeContamination:
            arguments.append("-nc")

        outputFile = self.parameterAsOutputLayer(parameters, self.EXTREME_VALUE, context)
        arguments.append("-ssa")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
