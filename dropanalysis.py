# -*- coding: utf-8 -*-

"""
***************************************************************************
    dropanalysis.py
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
from collections import OrderedDict

from qgis.core import (QgsProcessing,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFileDestination
                      )

from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils


class DropAnalysis(TauDemAlgorithm):

    PIT_FILLED = "PIT_FILLED"
    D8_FLOWDIR = "D8_FLOWDIR"
    D8_CONTRIB_AREA = "D8_CONTRIB_AREA"
    ACCUM_STREAM_SOURCE = "ACCUM_STREAM_SOURCE"
    OUTLETS = "OUTLETS"
    MIN_TRESHOLD = "MIN_TRESHOLD"
    MAX_THRESHOLD = "MAX_THRESHOLD"
    DROP_TRESHOLDS = "DROP_TRESHOLDS"
    STEP = "STEP"
    DROP_ANALYSIS = "DROP_ANALYSIS"

    def name(self):
        return "dropanalysis"

    def displayName(self):
        return self.tr("Stream drop analysis")

    def group(self):
        return self.tr("Stream network analysis")

    def groupId(self):
        return "streamanalysis"

    def tags(self):
        return self.tr("dem,hydrology,stream,drop,statistics").split(",")

    def shortHelpString(self):
        return self.tr("Applies a series of thresholds (determined from the "
                       "input parameters) to the input accumulated stream "
                       "source grid and outputs the results in the stream "
                       "drop statistics table.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/StreamDropAnalysis.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.STEPS = OrderedDict([(self.tr("Logarithmic"), 0),
                                  (self.tr("Arithmetic"), 1)])

        self.addParameter(QgsProcessingParameterRasterLayer(self.PIT_FILLED,
                                                            self.tr("Pit filled elevation")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.D8_FLOWDIR,
                                                            self.tr("D8 flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.D8_CONTRIB_AREA,
                                                            self.tr("D8 contributing area")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.ACCUM_STREAM_SOURCE,
                                                            self.tr("Accumulated stream source")))
        self.addParameter(QgsProcessingParameterVectorLayer(self.OUTLETS,
                                                            self.tr("Outlets"),
                                                            types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterNumber(self.MIN_TRESHOLD,
                                                       self.tr("Minimum threshold"),
                                                       QgsProcessingParameterNumber.Double,
                                                       5,
                                                       False))
        self.addParameter(QgsProcessingParameterNumber(self.MAX_THRESHOLD,
                                                       self.tr("Maximum threshold"),
                                                       QgsProcessingParameterNumber.Double,
                                                       500,
                                                       False))
        self.addParameter(QgsProcessingParameterNumber(self.DROP_TRESHOLDS,
                                                       self.tr("Number of drop thresholds"),
                                                       QgsProcessingParameterNumber.Double,
                                                       10,
                                                       False))
        keys = list(self.STEPS.keys())
        kernel_shape_param = QgsProcessingParameterEnum(self.STEP,
                                                        self.tr("Type of threshold step"),
                                                        keys,
                                                        allowMultiple=False,
                                                        defaultValue=0)

        self.addParameter(QgsProcessingParameterFileDestination(self.DROP_ANALYSIS,
                                                                self.tr("Drop analysis"),
                                                                self.tr("Text files (*.txt)")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-fel")
        arguments.append(self.parameterAsRasterLayer(parameters, self.PIT_FILLED, context).source())
        arguments.append("-p")
        arguments.append(self.parameterAsRasterLayer(parameters, self.D8_FLOWDIR, context).source())
        arguments.append("-ad8")
        arguments.append(self.parameterAsRasterLayer(parameters, self.D8_CONTRIB_AREA, context).source())
        arguments.append("-ssa")
        arguments.append(self.parameterAsRasterLayer(parameters, self.ACCUM_STREAM_SOURCE, context).source())
        arguments.append("-o")
        arguments.append(self.parameterAsVectorLayer(parameters, self.OUTLETS, context).source())

        arguments.append("-par")
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.MIN_TRESHOLD, context)))
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.MAX_TRESHOLD, context)))
        arguments.append("{}".format(self.parameterAsDouble(parameters, self.DROP_TRESHOLDS, context)))
        arguments.append("{}".format(self.parameterAsEnum(parameters, self.STEP, context)))

        outputFile = self.parameterAsFileOutput(parameters, self.DROP_ANALYSIS, context)
        arguments.append("-drp")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
