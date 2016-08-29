# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DialogSelectflore
                                 A QGIS plugin
 export
                             -------------------
        begin                : 2016-04-19
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
from PyQt4.QtCore import *
from PyQt4.Qt import QTableWidget, QAbstractItemView, QTableWidgetItem, QMessageBox
from PyQt4.QtGui import QIcon
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ModuleExport_dialog_flore.ui'))


class DialogSelectFlore(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(DialogSelectFlore, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setWindowTitle("Selection de la flore.")
        
        #définir les titres de mes colonnes
        header_labels = ["espece_id", "taxons", "nomcommun", 'class', 'ordre', "cd_nom", "cd_ref", "rarete", "menace" ]
        self.matablewidget.setHorizontalHeaderLabels(header_labels)
        #On cache la colonne d espece
        
        for i in range(3,9):
            self.matablewidget.setColumnHidden(i, True)

        #La selection sur la vue wref ne pourra se faire que par lignes
        self.matablewidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        #Notre table ne doit pas être éditable
        self.matablewidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        

        header_labels = ["espece_id", "taxon", "nomcommun"]
        self.tab_flore_selected.setHorizontalHeaderLabels(header_labels)
        #On cache la colonne d espece
        self.tab_flore_selected.setColumnHidden(2, True)
        
        #La selection sur la vue wref ne pourra se faire que par lignes
        self.tab_flore_selected.setSelectionBehavior(QAbstractItemView.SelectRows)
        #Notre table ne doit pas être éditable
        self.tab_flore_selected.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.plugin_dir = os.path.dirname(__file__)
        self.btn_ajoutflore.setIcon(QIcon(self.plugin_dir+"/btn_add.png"))
        self.btn_rmflore.setIcon(QIcon(self.plugin_dir+"/btn_remove.png"))
        self.vider_flore.setIcon(QIcon(self.plugin_dir+"/btn_suppr.png"))
        self.unselect.setIcon(QIcon(self.plugin_dir+"/unselect.png"))
        self.btn_visible.setIcon(QIcon(self.plugin_dir+"/visible.png"))
        self.btn_invisible.setIcon(QIcon(self.plugin_dir+"/invisible.png"))
        
        self.searchButton.setStyleSheet('QPushButton {background-color: #CCF390;font-weight: bold}') 






    def visibilite(self, bool = False):
            if bool == False:
                for i in range(3,9):
                    self.matablewidget.setColumnHidden(i, True)
                self.tab_flore_selected.setColumnHidden(2, True)
                
            if bool == True:
                for i in range(3,9):
                    self.matablewidget.setColumnHidden(i, False)
                self.tab_flore_selected.setColumnHidden(2, False)
        
    
    #Méthode d'ajout d'éspèce dans les colonnes de selection
    #On supprime les doublons également
    #Choix d'une rédaction des "row" sans boucle pour meilleure lisbilité malgré longueur du code.
    def transvasajout__espece_flore(self):

        
        #CREATION D UNE LISTE ANTI DOUBLON
        #Variables qui contiennt les elements des cellules dans les rows selectionnés
        #Quadriliste de non-doublons


        compterow = self.tab_flore_selected.rowCount()
        old_maliste0=[]
        for i in xrange(0,compterow):
            old_maliste0.append(self.tab_flore_selected.item(i,0).text())

                
        #MON TRANSVASAGE
        #Controle        
        if self.matablewidget.selectionModel().hasSelection() != True:
            QMessageBox.information(self,'Information',u'Veuillez selectionner des entites a transferer.')
            
        else:
            
            #Variables qui contiennt les elements des cellules dans les rows selectionnés
            mesrows0 = self.matablewidget.selectionModel().selectedRows(0) 
            mesrows1 = self.matablewidget.selectionModel().selectedRows(1) 
            mesrows2 = self.matablewidget.selectionModel().selectedRows(2) 
                   
            #Threeliste
            maliste0 = []
            for i in mesrows0:                
                if i.data() not in old_maliste0:
                    maliste0.append(i.data())
            
            maliste1 = []
            for i in mesrows1:                
                maliste1.append(i.data())

            maliste2 = []
            for i in mesrows2:                
                maliste2.append(i.data())

                    

                         
            #On réparti les listes dans des QTableWidget!
            for i in xrange(0, len(maliste0)):
                self.tab_flore_selected.insertRow(self.tab_flore_selected.rowCount())
                self.tab_flore_selected.setItem(self.tab_flore_selected.rowCount()-1,0 ,QTableWidgetItem(self.tr(maliste0[i])))
                self.tab_flore_selected.setItem(self.tab_flore_selected.rowCount()-1,1 ,QTableWidgetItem(maliste1[i]))
                self.tab_flore_selected.setItem(self.tab_flore_selected.rowCount()-1,2 ,QTableWidgetItem(self.tr(maliste2[i])))

                
                


            
    #Méthode de retrait d'éspèce dans la colonne de selection
    def transvasretrait_espece_flore(self):

        rows = self.tab_flore_selected.selectionModel().selectedRows()
        #liste inversée pour régler les pb d'index.
        rows = sorted(rows, reverse = True)
        for r in rows:
            self.tab_flore_selected.removeRow(r.row())
            
    #SLOT pour déselectionner tout les éléments des 2 tableaux.        
    def clear(self):

        #deselection tableau    
        self.matablewidget.clearSelection()
        self.tab_flore_selected.clearSelection()
            
    
    #Param: Type de tableau cible, itération.
    def peupler_table_from_base(self,tableurcible, iter):

            tableurcible.insertRow(tableurcible.rowCount())
            for i in range(0,9):
                tableurcible.setItem(tableurcible.rowCount()-1,i ,QTableWidgetItem(unicode(iter[i])))
                
           
            
            
    def peupler_table_from_base_selected(self,tableurcible, iter):
            tableurcible.insertRow(tableurcible.rowCount())
            tableurcible.setItem(tableurcible.rowCount()-1,0 ,QTableWidgetItem(unicode(iter[0])))
            tableurcible.setItem(tableurcible.rowCount()-1,1 ,QTableWidgetItem((iter[1])))
            tableurcible.setItem(tableurcible.rowCount()-1,2 ,QTableWidgetItem((iter[2])))
            
    

            
            
