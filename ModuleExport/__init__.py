# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ModuleExport
                                 A QGIS plugin
 export
                             -------------------
        begin                : 2016-04-14
        copyright            : (C) 2016 by Loic Martel
        email                : loic.martel@outlook.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ModuleExport class from file ModuleExport.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ModuleExport import ModuleExport
    return ModuleExport(iface)
