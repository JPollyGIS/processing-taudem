# -*- coding: utf-8 -*-

"""
***************************************************************************
    taudemUtils.py
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
import re
import subprocess

from qgis.core import QgsMessageLog, QgsProcessingFeedback
from processing.core.ProcessingLog import ProcessingLog
from processing.core.ProcessingConfig import ProcessingConfig

versionRegex = re.compile('([\d.]+)')
progressRegex = re.compile('\d+')

TAUDEM_ACTIVE = 'TAUDEM_ACTIVE'
TAUDEM_DIRECTORY = 'TAUDEM_DIRECTORY'
TAUDEM_MPICH = 'TAUDEM_MPICH'
TAUDEM_PROCESSES = 'TAUDEM_PROCESSES'
TAUDEM_VERBOSE = 'TAUDEM_VERBOSE'


def taudemDirectory():
    filePath = ProcessingConfig.getSetting(TAUDEM_DIRECTORY)
    return filePath if filePath is not None else ''


def mpichDirectory():
    filePath = ProcessingConfig.getSetting(TAUDEM_MPICH)
    return filePath if filePath is not None else ''


def descriptionPath():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "descriptions"))


def execute(commands, feedback=None):
    if feedback is None:
        feedback = QgsProcessingFeedback()

    fused_command = ' '.join([str(c) for c in commands])
    QgsMessageLog.logMessage(fused_command, 'Processing', QgsMessageLog.INFO)
    feedback.pushInfo('TauDEM command:')
    feedback.pushCommandInfo(fused_command)
    feedback.pushInfo('TauDEM command output:')

    loglines = []
    with subprocess.Popen(fused_command,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stdin=subprocess.DEVNULL,
                          stderr=subprocess.STDOUT,
                          universal_newlines=True) as proc:
        try:
            for line in iter(proc.stdout.readline, ''):
                if '%' in line:
                    try:
                        feedback.setProgress(int(progressRegex.search(line).group(0)))
                    except:
                        pass
                else:
                    feedback.pushConsoleInfo(line)
                    loglines.append(line)
        except:
            pass

    if ProcessingConfig.getSetting(TAUDEM_VERBOSE):
        QgsMessageLog.logMessage('\n'.join(loglines), 'Processing', QgsMessageLog.INFO)
