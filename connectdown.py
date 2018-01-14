# -*- coding: utf-8 -*-

"""
***************************************************************************
    connectdown.py
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
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterVectorDestination
                      )

from processing_taudem.taudemAlgorithm import TauDemAlgorithm
from processing_taudem import taudemUtils

class ConnectDown(TauDemAlgorithm):

    D8_FLOWDIR = "D8_FLOWDIR"
    D8_CONTRIB_AREA = "D8_CONTRIB_AREA"
    WATERSHED = "WATERSHED"
    CELLS = "CELLS"
    OUTLETS = "OUTLETS"
    MOVED_OUTLETS = "MOVED_OUTLETS"

    def name(self):
        return "connectdown"

    def displayName(self):
        return self.tr("Connect down")

    def group(self):
        return self.tr("Stream network analysis")

    def groupId(self):
        return "streamanalysis"

    def tags(self):
        return self.tr("dem,hydrology,connect,outlet,downflow").split(",")

    def shortHelpString(self):
        return self.tr("For each zone in a raster entered (e.g. HUC converted "
                       "to grid) it identifies the point with largest area D8.")

    def helpUrl(self):
        return "http://hydrology.usu.edu/taudem/taudem5/help53/ConnectDown.html"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.D8_FLOWDIR,
                                                            self.tr("D8 flow directions")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.D8_CONTRIB_AREA,
                                                            self.tr("D8 contributing area")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.WATERSHED,
                                                            self.tr("Watershed")))
        self.addParameter(QgsProcessingParameterNumber(self.CELLS,
                                                       self.tr("Grid cells move to downstream"),
                                                       QgsProcessingParameterNumber.Integer,
                                                       1,
                                                       True))

        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTLETS,
                                                                  self.tr("Outlets"),
                                                                  QgsProcessing.TypeVectorPoint))
        self.addParameter(QgsProcessingParameterVectorDestination(self.MOVED_OUTLETS,
                                                                  self.tr("Moved outlets"),
                                                                  QgsProcessing.TypeVectorPoint))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(taudemUtils.taudemDirectory(), self.name()))

        arguments.append("-p")
        arguments.append(self.parameterAsRasterLayer(parameters, self.D8_FLOWDIR, context).source())
        arguments.append("-ad8")
        arguments.append(self.parameterAsRasterLayer(parameters, self.D8_CONTRIB_AREA, context).source())
        arguments.append("-w")
        arguments.append(self.parameterAsRasterLayer(parameters, self.WATERSHED, context).source())
        arguments.append("-d")
        arguments.append("{}".format(self.parameterAsInt(parameters, self.CELLS, context)))

        arguments.append("-o")
        arguments.append(self.parameterAsOutputLayer(parameters, self.OUTLETS, context))
        arguments.append("-od")
        arguments.append(self.parameterAsOutputLayer(parameters, self.MOVED_OUTLETS, context))

        taudemUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
