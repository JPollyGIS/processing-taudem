# -*- coding: utf-8 -*-

"""
***************************************************************************
    dinftranslimaccum.py
    ---------------------
    Date                 : June 2012
    Copyright            : (C) 2012-2018 by Alexander Bruy
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
__date__ = 'June 2012'
__copyright__ = '(C) 2012-2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterDestination
                      )
from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils


class DinfTransLimAccum(TauDemAlgorithm):

    DINF_FLOWDIR = "DINF_FLOWDIR"
    TRANSPORT_SUPPLY = "TRANSPORT_SUPPLY"
    TRANSPORT_CAPACITY = "TRANSPORT_CAPACITY"
    INPUT_CONCENTRATION = "INPUT_CONCENTRATION"
    OUTLETS = "OUTLETS"
    EDGE_CONTAMINATION = "EDGE_CONTAMINATION"
    TRANLIM_ACCUM = "TRANSLIM_ACCUM"
    DEPOSITION = "DEPOSITION"
    OUTPUT_CONCENTRATION = "OUTPUT_CONCENTRATION"

    def name(self):
        return "dinftranslimaccum"

    def displayName(self):
        return self.tr("D-infinity transport limited accumulation")

    def group(self):
        return self.tr("Specialized grid analysis")

    def groupId(self):
        return "specializedanalysis"

    def tags(self):
        return self.tr("dem,hydrology,d-infinity,transport,deposition").split(",")

    def shortHelpString(self):
        return self.tr("Calculates the transport and deposition of a substance "
                       "(e.g. sediment) that may be limited by both supply and "
                       "the capacity of the flow field to transport it.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/DInfinityTransportLimitedAccumulation.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.DINF_FLOWDIR,
                                                            self.tr("D-infinity flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.TRANSPORT_SUPPLY,
                                                            self.tr("Transport supply")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.TRANSPORT_CAPACITY,
                                                            self.tr("Transport capacity")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_CONCENTRATION,
                                                            self.tr("Input concentration"),
                                                            optional=True))
        self.addParameter(QgsProcessingParameterVectorLayer(self.OUTLETS,
                                                            self.tr("Outlets"),
                                                            types=[QgsProcessing.TypeVectorPoint],
                                                            optional=True))
        self.addParameter(QgsProcessingParameterBoolean(self.EDGE_CONTAMINATION,
                                                        self.tr("Check for edge contamination"),
                                                        defaultValue=False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.TRANLIM_ACCUM,
                                                                  self.tr("Transport limited accumulation")))
        self.addParameter(QgsProcessingParameterRasterDestination(self.DEPOSITION,
                                                                  self.tr("Deposition")))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_CONCENTRATION,
                                                                  self.tr("Output concentration"),
                                                                  optional=True))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-ang")
        arguments.append(self.parameterAsRasterLayer(parameters, self.DINF_FLOWDIR, context).source())
        arguments.append("-tsup")
        arguments.append(self.parameterAsRasterLayer(parameters, self.TRANSPORT_SUPPLY, context).source())
        arguments.append("-tc")
        arguments.append(self.parameterAsRasterLayer(parameters, self.TRANSPORT_CAPACITY, context).source())

        concentration = self.parameterAsRasterLayer(parameters, self.INPUT_CONCENTRATION, context)
        if concentration:
            arguments.append("-cs")
            arguments.append(concentration.source())

            concentration = self.parameterAsOutputLayer(parameters, self.OUTPUT_CONCENTRATION, context)
            if concentration:
                arguments.append("-ctpt")
                arguments.append(concentration.source())
            else:
                raise QgsProcessingException(self.tr("Output concentration is not set."))

        outlets = self.parameterAsVectorLayer(parameters, self.OUTLETS, context)
        if outlets:
            arguments.append("-o")
            arguments.append(outlets.source())

        edgeContamination = self.parameterAsBool(parameters, self.EDGE_CONTAMINATION, context)
        if edgeContamination:
            arguments.append("-nc")

        outputFile = self.parameterAsOutputLayer(parameters, self.TRANLIM_ACCUM, context)
        arguments.append("-tla")
        arguments.append(outputFile)

        outputFile = self.parameterAsOutputLayer(parameters, self.DEPOSITION, context)
        arguments.append("-tdep")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
