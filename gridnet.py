# -*- coding: utf-8 -*-

"""
***************************************************************************
    gridnet.py
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
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterDestination
                      )

from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils


class GridNet(TauDemAlgorithm):

    D8_FLOWDIR = "D8_FLOWDIR"
    MASK_GRID = "MASK_GRID"
    THRESHOLD = "THRESHOLD"
    OUTLETS = "OUTLETS"
    LONGEST_PATH = "LONGEST_PATH"
    TOTAL_PATH = "TOTAL_PATH"
    STRAHLER_ORDER = "STRAHLER_ORDER"

    def name(self):
        return "gridnet"

    def displayName(self):
        return self.tr("Grid Network")

    def group(self):
        return self.tr("Basic grid analysis")

    def groupId(self):
        return "basicanalysis"

    def tags(self):
        return self.tr("dem,hydrology,strahler,order,path").split(",")

    def shortHelpString(self):
        return self.tr("Creates 3 grids that contain for each grid cell: "
                       "1) the longest upslope path length, 2) the total "
                       "upslope path length, and 3) the Strahler order number.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/GridNetwork.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.D8_FLOWDIR,
                                                            self.tr("D9 flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.MASK_GRID,
                                                            self.tr("Mask grid"),
                                                            optional=True))
        self.addParameter(QgsProcessingParameterNumber(self.THRESHOLD,
                                                       self.tr("Mask threshold"),
                                                       QgsProcessingParameterNumber.Double,
                                                       100.0,
                                                       True))
        self.addParameter(QgsProcessingParameterVectorLayer(self.OUTLETS,
                                                            self.tr("Outlets"),
                                                            types=[QgsProcessing.TypeVectorPoint],
                                                            optional=True))

        self.addParameter(QgsProcessingParameterRasterDestination(self.LONGEST_PATH,
                                                                  self.tr("Longest upslope length")))
        self.addParameter(QgsProcessingParameterRasterDestination(self.TOTAL_PATH,
                                                                  self.tr("Total upslope length")))
        self.addParameter(QgsProcessingParameterRasterDestination(self.STRAHLER_ORDER,
                                                                  self.tr("Strahler network order")))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-p")
        arguments.append(self.parameterAsRasterLayer(parameters, self.D8_FLOWDIR, context).source())

        mask = self.parameterAsRasterLayer(parameters, self.MASK_GRID, context)
        if mask:
            arguments.append("-mask")
            arguments.append(mask.source())
            arguments.append("-thresh")
            arguments.append("{}".format(self.parameterAsDouble(parameters, self.THRESHOLD, context)))

        outlets = self.parameterAsVectorLayer(parameters, self.OUTLETS, context)
        if outlets:
            arguments.append("-o")
            arguments.append(outlets.source())

        outputFile = self.parameterAsOutputLayer(parameters, self.LONGEST_PATH, context)
        arguments.append("-plen")
        arguments.append(outputFile)

        outputFile = self.parameterAsOutputLayer(parameters, self.TOTAL_PATH, context)
        arguments.append("-tlen")
        arguments.append(outputFile)

        outputFile = self.parameterAsOutputLayer(parameters, self.STRAHLER_ORDER, context)
        arguments.append("-gord")
        arguments.append(outputFile)

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
