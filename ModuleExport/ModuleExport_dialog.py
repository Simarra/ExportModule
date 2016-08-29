# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ModuleExportDialog
                                 A QGIS plugin
 export
                             -------------------
        begin                : 2016-04-14
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Loic Martel
        email                : loic.martel@outlook.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic
from PyQt4.Qt import QDateEdit, QPushButton
from PyQt4.QtGui import QProgressBar
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ModuleExport_dialog_base.ui'))


class ModuleExportDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(ModuleExportDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface
        
        #Forcer le passage en premeir plan
        self.setModal(1)
        
        

        

        
        #Méthodes pour passer les dates en format annee ou jour
        self.date_min_pec.setDisplayFormat('yyyy')
        self.date_max_pec.setDisplayFormat('yyyy')
        self.radioSaisie.toggled.connect(lambda: self.date_min_pec.setDisplayFormat('dd-MM-yyyy'))
        self.radioSaisie.toggled.connect(lambda: self.date_max_pec.setDisplayFormat('dd-MM-yyyy'))
        self.radioObs.toggled.connect(lambda: self.date_min_pec.setDisplayFormat('yyyy'))
        self.radioObs.toggled.connect(lambda: self.date_max_pec.setDisplayFormat('yyyy'))
        self.radioSaisie.toggle()

        
        
        
        #self.ButtonFlore.setEnabled(0)
        #Méthodes pour afficher ou faire disparaitre les boutons de selection d especes..
        self.rad_all_espece.toggled.connect(lambda: self.ButtonFlore.hide())
        self.rad_all_espece.toggled.connect(lambda: self.ButtonFaune.hide())
        self.rad_all_espece.toggled.connect(lambda: self.checkFlore.hide())
        self.rad_all_espece.toggled.connect(lambda: self.checkFaune.hide())
        self.rad_slc_espece.toggled.connect(lambda: self.ButtonFaune.show())
        self.rad_slc_espece.toggled.connect(lambda: self.ButtonFlore.show())
        self.rad_slc_espece.toggled.connect(lambda: self.checkFlore.show())
        self.rad_slc_espece.toggled.connect(lambda: self.checkFaune.show())
        self.rad_all_espece.toggle()
        self.checkFlore.clicked.connect(lambda: self.griser_bouton(self.ButtonFlore))
        self.checkFaune.clicked.connect(lambda: self.griser_bouton(self.ButtonFaune))
        
        
        # Rendre le bouton d'export plus explicite.
        self.buttonLaunch.setStyleSheet('QPushButton {background-color: #CCF390;font-weight: bold}')
        self.killButton.setStyleSheet('QPushButton {background-color: #FC9D9A;font-weight: bold}')
        self.buttonCleanExport.setStyleSheet('QPushButton {background-color: #FC9D9A;font-weight: bold}')
        self.checkClean.setStyleSheet('QCheckBox{font-weight: bold}')
        #Cacher la progressbar
        self.progressBar.hide()
        self.avancee.hide()  
        
    
    def griser_bouton(self, monbouton):
        if monbouton.isEnabled()== True:
            return monbouton.setEnabled(0)
        else:
            return monbouton.setEnabled(1)
        
        