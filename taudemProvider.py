# -*- coding: utf-8 -*-

"""
***************************************************************************
    taudemProvider.py
    ---------------------
    Date                 : May 2012
    Copyright            : (C) 2012-2017 by Alexander Bruy
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
__copyright__ = '(C) 2012-2017, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import QgsProcessingProvider, QgsMessageLog

from processing.core.ProcessingConfig import ProcessingConfig, Setting

from processing_taudem.taudemAlgorithm import TauDemAlgorithm
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

    def longName(self):
        version = taudemUtils.version()
        return 'TauDEM ({})'.format(version) if version is not None else 'TauDEM'

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

    def loadAlgorithms(self):
        self.algs = []
        folder = taudemUtils.descriptionPath()

        for descriptionFile in os.listdir(folder):
            if descriptionFile.endswith('txt'):
                try:
                    alg = TauDemAlgorithm(os.path.join(folder, descriptionFile))
                    if alg.name().strip() != '':
                        self.algs.append(alg)
                    else:
                        QgsMessageLog.logMessage(self.tr('Could not load TauDEM algorithm from file: {}'.format(descriptionFile)),
                                                 self.tr('Processing'), QgsMessageLog.CRITICAL)
                except Exception as e:
                    QgsMessageLog.logMessage(self.tr('Could not load TauDEM algorithm from file: {}\n{}'.format(descriptionFile, str(e))),
                                             self.tr('Processing'), QgsMessageLog.CRITICAL)

        for a in self.algs:
            self.addAlgorithm(a)

    def tr(self, string, context=''):
        if context == '':
            context = 'TauDemProvider'
        return QCoreApplication.translate(context, string)
