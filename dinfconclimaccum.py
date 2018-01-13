# -*- coding: utf-8 -*-

"""
***************************************************************************
    dinfconclimaccum.py
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
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterDestination
                      )
from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils


class DinfConcLimAccum(TauDemAlgorithm):

    DINF_FLOWDIR = "DINF_FLOWDIR"
    DECAY_MULTIPLIER = "DECAY_MULTIPLIER"
    DISTURBANCE_INDICATOR = "DISTURBANCE_INDICATOR"
    RUNOFF_WEIGHT = "RUNOFF_WEIGHT"
    OUTLETS = "OUTLETS"
    CONCENTRATION_THRESHOLD = "CONCENTRATION_THRESHOLD"
    EDGE_CONTAMINATION = "EDGE_CONTAMINATION"
    CONCENTRATION = "CONCENTRATION"
    SPECIFIC_DISCHARGE = "SPECIFIC_DISCHARGE"

    def name(self):
        return "dinfconclimaccum"

    def displayName(self):
        return self.tr("D-infinity concentration limited acccumulation")

    def group(self):
        return self.tr("Specialized grid analysis")

    def groupId(self):
        return "specializedanalysis"

    def tags(self):
        return self.tr("dem,hydrology,d-infinity,concentration").split(",")

    def shortHelpString(self):
        return self.tr("Creates a grid of the concentration of a substance "
                       "at each location in the domain, where the supply of "
                       "substance from a supply area is loaded into the flow "
                       "at a concentration or solubility threshold.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/DInfinityConcentrationLimitedAccumulation.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.DINF_FLOWDIR,
                                                            self.tr("D-infinity flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.DECAY_MULTIPLIER,
                                                            self.tr("Decay multiplier")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.DISTURBANCE_INDICATOR,
                                                            self.tr("Disturbance indicator")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.RUNOFF_WEIGHT,
                                                            self.tr("Effective runoff weight")))
        self.addParameter(QgsProcessingParameterVectorLayer(self.OUTLETS,
                                                            self.tr("Outlets"),
                                                            types=[QgsProcessing.TypeVectorPoint],
                                                            optional=True))
        self.addParameter(QgsProcessingParameterNumber(self.CONCENTRATION_THRESHOLD,
                                                       self.tr("Concentration threshold"),
                                                       QgsProcessingParameterNumber.Double,
                                                       1,
                                                       True))
        self.addParameter(QgsProcessingParameterBoolean(self.EDGE_CONTAMINATION,
                                                        self.tr("Check for edge contamination"),
                                                        defaultValue=False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.CONCENTRATION,
                                                                  self.tr("Concentration")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-ang")
        arguments.append(self.parameterAsRasterLayer(parameters, self.DINF_FLOWDIR, context).source())
        arguments.append("-dm")
        arguments.append(self.parameterAsRasterLayer(parameters, self.DECAY_MULTIPLIER, context).source())
        arguments.append("-dg")
        arguments.append(self.parameterAsRasterLayer(parameters, self.DISTURBANCE_INDICATOR, context).source())
        arguments.append("-q")
        arguments.append(self.parameterAsRasterLayer(parameters, self.RUNOFF_WEIGHT, context).source())
        arguments.append("-csol")
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.CONCENTRATION_THRESHOLD, context)))

        outlets = self.parameterAsVectorLayer(parameters, self.OUTLETS, context)
        if outlets:
            arguments.append("-o")
            arguments.append(outlets.source())

        edgeContamination = self.parameterAsBool(parameters, self.EDGE_CONTAMINATION, context)
        if edgeContamination:
            arguments.append("-nc")

        outputFile = self.parameterAsOutputLayer(parameters, self.CONCENTRATION, context)
        arguments.append("-ctpt")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
