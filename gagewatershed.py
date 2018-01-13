# -*- coding: utf-8 -*-

"""
***************************************************************************
    gagewatershed.py
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
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterFileDestination
                      )

from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils


class GageWatershed(TauDemAlgorithm):

    D8_FLOWDIR = "D8_FLOWDIR"
    OUTLETS = "OUTLETS"
    GAGE_WATERSHED = "GAGE_WATERSHED"
    WATERSHED_CONNECTIVITY = "WATERSHED_CONNECTIVITY"

    def name(self):
        return "gagewatershed"

    def displayName(self):
        return self.tr("Gage watershed")

    def group(self):
        return self.tr("Stream network analysis")

    def groupId(self):
        return "streamanalysis"

    def tags(self):
        return self.tr("dem,hydrology,gage,watershed").split(",")

    def shortHelpString(self):
        return self.tr("Calculates Gage watersheds grid.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/GageWatershed.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.D8_FLOWDIR,
                                                            self.tr("D8 flow directions")))
        self.addParameter(QgsProcessingParameterVectorLayer(self.OUTLETS,
                                                            self.tr("Outlets"),
                                                            types=[QgsProcessing.TypeVectorPoint],
                                                            optional=False))

        self.addParameter(QgsProcessingParameterRasterDestination(self.GAGE_WATERSHED,
                                                                  self.tr("Gage watershed")))
        self.addParameter(QgsProcessingParameterFileDestination(self.WATERSHED_CONNECTIVITY,
                                                                self.tr("Watershed downslope connectivity"),
                                                                self.tr("Text files (*.txt)"),
                                                                optional=True))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-p")
        arguments.append(self.parameterAsRasterLayer(parameters, self.D8_FLOWDIR, context).source())
        arguments.append("-o")
        arguments.append(self.parameterAsVectorLayer(parameters, self.OUTLETS, context).source())

        outputFile = self.parameterAsOutputLayer(parameters, self.GAGE_WATERSHED, context)
        arguments.append("-gw")
        arguments.append(outputFile)

        outputFile = self.parameterAsFileOutput(parameters, self.WATERSHED_CONNECTIVITY, context)
        if outputFile:
            arguments.append("-id")
            arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
