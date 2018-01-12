# -*- coding: utf-8 -*-

"""
***************************************************************************
    taudemProvider.py
    ---------------------
    Date                 : May 2012
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
__date__ = 'May 2012'
__copyright__ = '(C) 2012-2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import QgsProcessingProvider, QgsMessageLog

from processing.core.ProcessingConfig import ProcessingConfig, Setting

from processing_taudem.pitremove import PitRemove
from processing_taudem.aread8 import AreaD8
from processing_taudem.d8flowdir import D8FlowDir
from processing_taudem.areadinf import AreaDinf
from processing_taudem.dinfflowdir import DinfFlowDir
from processing_taudem.gridnet import GridNet

from processing_taudem.peukerdouglas import PeukerDouglas
from processing_taudem.threshold import Threshold
from processing_taudem.d8flowpathextremeup import D8FlowPathExtremeUp
from processing_taudem.slopearea import SlopeArea
from processing_taudem.lengtharea import LengthArea
from processing_taudem.dropanalysis import DropAnalysis
from processing_taudem.streamnet import StreamNet
from processing_taudem.moveoutletstostreams import MoveOutletsToStreams
from processing_taudem.gagewatershed import GageWatershed

from processing_taudem import taudemUtils

pluginPath = os.path.dirname(__file__)


class TauDemProvider(QgsProcessingProvider):

    def __init__(self):
        super().__init__()
        self.algs = []

    def id(self):
        return 'taudem'

    def name(self):
        return 'TauDEM'

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'icons', 'taudem.svg'))

    def load(self):
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(self.name(),
                                            taudemUtils.TAUDEM_ACTIVE,
                                            self.tr('Activate'),
                                            False))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            taudemUtils.TAUDEM_DIRECTORY,
                                            self.tr('TauDEM directory'),
                                            taudemUtils.taudemDirectory(),
                                            valuetype=Setting.FOLDER))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            taudemUtils.TAUDEM_MPICH,
                                            self.tr('MPICH2/OpenMPI bin directory'),
                                            taudemUtils.mpichDirectory(),
                                            valuetype=Setting.FOLDER))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            taudemUtils.TAUDEM_PROCESSES,
                                            self.tr('Number of MPI parallel processes to use'),
                                            2,
                                            valuetype=Setting.INT))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            taudemUtils.TAUDEM_VERBOSE,
                                            self.tr('Log commands output'),
                                            False))
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def unload(self):
        ProcessingConfig.removeSetting(taudemUtils.TAUDEM_ACTIVE)
        ProcessingConfig.removeSetting(taudemUtils.TAUDEM_DIRECTORY)
        ProcessingConfig.removeSetting(taudemUtils.TAUDEM_MPICH)
        ProcessingConfig.removeSetting(taudemUtils.TAUDEM_PROCESSES)
        ProcessingConfig.removeSetting(taudemUtils.TAUDEM_VERBOSE)

    def isActive(self):
        return ProcessingConfig.getSetting(taudemUtils.TAUDEM_ACTIVE)

    def setActive(self, active):
        ProcessingConfig.setSettingValue(taudemUtils.TAUDEM_ACTIVE, active)

    def supportsNonFileBasedOutput(self):
        return False

    def getAlgs(self):
        algs = [PitRemove(),
                AreaD8(),
                D8FlowDir(),
                AreaDinf(),
                DinfFlowDir(),
                GridNet(),
                PeukerDouglas(),
                Threshold(),
                D8FlowPathExtremeUp(),
                SlopeArea(),
                LengthArea(),
                DropAnalysis(),
                StreamNet(),
                MoveOutletsToStreams(),
                GageWatershed(),
               ]

        return algs

    def loadAlgorithms(self):
        self.algs = self.getAlgs()
        for a in self.algs:
            self.addAlgorithm(a)

    def tr(self, string, context=''):
        if context == '':
            context = 'TauDemProvider'
        return QCoreApplication.translate(context, string)
