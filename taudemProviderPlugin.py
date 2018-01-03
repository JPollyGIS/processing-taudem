# -*- coding: utf-8 -*-

"""
***************************************************************************
    taudemProviderPlugin.py
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

from qgis.core import QgsApplication

from processing_taudem.taudemProvider import TauDemProvider


class TauDemProviderPlugin:

    def __init__(self):
        self.provider = TauDemProvider()

    def initGui(self):
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
