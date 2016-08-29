# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ModuleExport
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QMessageBox, QTableWidgetItem
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from ModuleExport_dialog import ModuleExportDialog
from DialogSelectFaune import DialogSelectFaune
from DialogSelectFlore import DialogSelectFlore
import os.path
import time
import psycopg2
from PyQt4.Qt import QPushButton, QSqlDatabase, QSqlTableModel
from xml.dom import minidom #Pour pouvoir générer notre fichier de metadata.
from subprocess import call

class ModuleExport:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):


        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ModuleExport_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialogs (after translation) and keep reference
        self.dlg = ModuleExportDialog(self.iface)
        self.dlg.setWindowTitle("module d'export")
        self.dlg_F = DialogSelectFaune(self.dlg)
        self.dlg_Flo = DialogSelectFlore(self.dlg)
        
        
        #Fonctions esthétiques: ajout d icones.
        self.dlg.ButtonFaune.setIcon(QIcon(self.plugin_dir+"/turtle-128.png"))
        self.dlg.ButtonFaune.setIcon(QIcon(self.plugin_dir+"/turtle-128.png"))
       
        
        self.dlg.ButtonFlore.setIcon(QIcon(self.plugin_dir+"/flower.png"))
        

        self.dlg_F.vider_faune.clicked.connect(lambda:self.vider_la_table('fa'))
        self.dlg_Flo.vider_flore.clicked.connect(lambda:self.vider_la_table('fl'))
        self.dlg.ButtonFaune.clicked.connect(self.fenetre_select_faune)
        self.dlg.ButtonFlore.clicked.connect(self.fenetre_select_flore)

        
        #Relier le bouton d'ajout d especefaune à mon SLOT dans DialogSelectFaune transvas_espece. 
        self.dlg_F.btn_ajoutfaune.clicked.connect(lambda: self.dlg_F.transvasajout__espece_faune())       
        self.dlg_F.btn_rmfaune.clicked.connect(lambda: self.dlg_F.transvasretrait_espece_faune())
        
        self.dlg_Flo.btn_ajoutflore.clicked.connect(lambda: self.dlg_Flo.transvasajout__espece_flore())       
        self.dlg_Flo.btn_rmflore.clicked.connect(lambda: self.dlg_Flo.transvasretrait_espece_flore())
        
        
        
        self.dlg_Flo.btn_visible.clicked.connect(lambda : self.dlg_Flo.visibilite(True))
        self.dlg_Flo.btn_invisible.clicked.connect(lambda : self.dlg_Flo.visibilite(False))       
 
        self.dlg_F.btn_visible.clicked.connect(lambda : self.dlg_F.visibilite(True))
        self.dlg_F.btn_invisible.clicked.connect(lambda : self.dlg_F.visibilite(False))
        
        

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&ModuleExport')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ModuleExport')
        self.toolbar.setObjectName(u'ModuleExport')


        #MEP du signal pour vider les selections.
        self.dlg_F.unselect.clicked.connect(lambda: self.dlg_F.clear())
        self.dlg_Flo.unselect.clicked.connect(lambda: self.dlg_Flo.clear())
        
        #MEP du signal pour la fonction de recherche.
        self.dlg_F.searchButton.clicked.connect(lambda: self.va_chercher('fa'))
        self.dlg_Flo.searchButton.clicked.connect(lambda: self.va_chercher('fl'))
        
        #Connexion des bouton de lancement et nettoyage de table 
        self.dlg.buttonLaunch.clicked.connect(lambda : self.lancement_des_operations())
        self.dlg.killButton.clicked.connect(lambda : self.nettoyage_des_tables())
        self.dlg.buttonCleanExport.clicked.connect(lambda : self.nettoyage_dossier_export())
        
        
    # noinspection PyMethodMayBeStatic

    def tr(self, message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ModuleExport', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(self.plugin_dir+"/icon.png")
        action = QAction(icon, "Module d'export", parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)
        #Ajout de notre action a la liste d actions.
        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = self.plugin_dir+"/icon.png"
        self.add_action(
            icon_path,
            text=self.tr(u'Module d export'),
            callback=self.run,
            whats_this = self.tr(u'Module permettant d\'exporter des données Faune / Flore vers une Shapefile ou un CSV.'),
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ModuleExport'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def peuplerComboExport(self):
        #creation connexion PGQT pour peupler la liste des type_export.
        self.QConn = QSqlDatabase("QPSQL")
        self.QConn.setHostName(self.get_host_ip())
        self.QConn.setDatabaseName(self.get_db_name())
        self.QConn.setUserName(self.get_dbuser_name())
        self.QConn.setPassword(self.get_pswrd())
        self.QConn.open()
        
        #Creation du modele de donnée pour peupler laQcombobox.
        self.Model_export = QSqlTableModel(db = self.QConn)
        self.Model_export.setTable("export.w_type_export")
        self.Model_export.select()
        #Peupler la Qcombobox
        self.dlg.comboExport.setModel(self.Model_export)
        self.dlg.comboExport.setModelColumn(self.Model_export.fieldIndex("nom"))    

####################################################################################
####################################################################################
##############                                                   ###################
##############                                                   ###################
##############        FONCTIONS DE RECUP DE DONNEES              ###################
##############               DANS PGSQL                          ###################
##############                                                   ###################
####################################################################################
####################################################################################
    def get_table_name(self):
        #Fonction pour obtenir le nom réel de la couche selectionnée. "Schema.table"
        table_name = str(self.iface.activeLayer().source())
        table_name = table_name.replace(table_name[0:table_name.find('table=')+6], "").replace('"','').split()

        return table_name[0]
    
    def get_db_name(self):
        #Fonction pour obtenir le nom de la base de données source
        madb = str(self.iface.activeLayer().source())
        madb = madb.replace(madb[0:madb.find('dbname=')+7], "").replace('"','').replace("'","").split()
        return madb[0]
    
    def get_host_ip(self):
        #Fonction pour obtenir le contenu de Host
        hname = str(self.iface.activeLayer().source())
        hname = hname.replace(hname[0:hname.find('host=')+5], "").replace('"','').replace("'","").split()
        return hname[0]
    
    def get_dbuser_name(self):
        #Fonction pour obtenir le nom du User
        usname = str(self.iface.activeLayer().source())
        usname = usname.replace(usname[0:usname.find('user=')+5], "").replace('"','').replace("'","").split()
        return usname[0]
    
    def get_pswrd(self):
        #Fonction pour obtenir le mot de passe
        pwrd = str(self.iface.activeLayer().source())
        pwrd = pwrd.replace(pwrd[0:pwrd.find('password=')+9], "").replace('"','').replace("'","").split()
        return pwrd[0]

    def recup_id(self):
                Mesobjet = self.iface.activeLayer().selectedFeatures ()
                Mesid = ', '.join([unicode(f['id']) for f in Mesobjet ])
                return Mesid




        
        

####################################################################################
####################################################################################
##############                                                   ###################
##############                                                   ###################
##############        FENETRES DE FAUNE FLORE                    ###################
##############                                                   ###################
##############                                                   ###################
####################################################################################
####################################################################################

    def fenetre_select_faune(self):


        self.dlg_F.combosearch.addItems([self.tr('taxon'), self.tr('nomcommun'), self.tr('classe'), self.tr('ordre'), self.tr('espece_id'),
                                         self.tr('cd_ref'), self.tr('cd_nom'), self.tr('rarepic'), self.tr('menapic')])

    
        idconnexion = ("dbname=%s host=%s user=%s password=%s") % (self.get_db_name(), self.get_host_ip(), self.get_dbuser_name(), self.get_pswrd())
    
        conn = psycopg2.connect(idconnexion)
        cur = conn.cursor()
        #fourniture d un echantillon basique et léger.
        marequete = """
        select w.espece_id, w.taxon, w.nomcommun, w.classe, w.ordre, w.cd_nom, w.cd_ref ,w.rarepic ,w.menapic
        from bdfauneflore.w_ref_faune w
        limit 100
        """
    
        cur.execute(marequete)

        for i in cur:
            self.dlg_F.peupler_table_from_base(self.dlg_F.matablewidget, i)
            
        
        cur.close()
        self.dlg_F.matablewidget.resizeColumnToContents(1)
        cur = conn.cursor()
        marequete2 = """
        select w.espece_id, w.taxon, w.nomcommun
        from export.w_faune_select w
        """
        cur.execute(marequete2)
        for i in cur:
            self.dlg_F.peupler_table_from_base_selected(self.dlg_F.tab_faune_selected,i)
        cur.close()   
        conn.close()
        
        #Si on appuie sur ok ou si l'utilisateur ferme la fenetre alors les listes sont vidées graphiquement. 
        
        #si l'utilisateur clique sur OK alors la liste d esepce selectionnee est transferee dans la table sleect_faune--/--flore.
        if self.dlg_F.exec_():
            self.ajout_ls_espece_pg('fa')
        
        if self.dlg_F.close():
            self.dlg_F.tab_faune_selected.clearContents()
            self.dlg_F.matablewidget.clearContents()
            self.dlg_F.tab_faune_selected.setRowCount(0)
            self.dlg_F.matablewidget.setRowCount(0)
            self.dlg_F.combosearch.clear()
            

        

            
            
    
    def fenetre_select_flore(self):


        self.dlg_Flo.combosearch.addItems([self.tr('taxon'), self.tr('nomcommun'), self.tr('classe'), self.tr('ordre'), self.tr('espece_id'),self.tr('cd_ref'), self.tr('cd_nom'), self.tr('rarepic'), self.tr('menapic')])

    
        idconnexion = ("dbname=%s host=%s user=%s password=%s") % (self.get_db_name(), self.get_host_ip(), self.get_dbuser_name(), self.get_pswrd())
    
        conn = psycopg2.connect(idconnexion)
        cur = conn.cursor()
        #fourniture d un echantillon basique et léger.
        marequete = """
        select w.espece_id, w.taxon, w.nomcommun, w.classe, w.ordre, w.cd_nom, w.cd_ref ,w.rarepic ,w.menapic
        from bdfauneflore.w_ref_flore w
        limit 100
        """
    
        cur.execute(marequete)

    
        
        for i in cur:
            self.dlg_Flo.peupler_table_from_base(self.dlg_Flo.matablewidget, i)
            
        
        cur.close()
        self.dlg_Flo.matablewidget.resizeColumnToContents(1)
        cur = conn.cursor()
        marequete2 = """
        select w.espece_id, w.taxon, w.nomcommun
        from export.w_flore_select w
        """
        cur.execute(marequete2)
        for i in cur:
            self.dlg_Flo.peupler_table_from_base_selected(self.dlg_Flo.tab_flore_selected,i)
        cur.close()   
        conn.close()
        
        #Si on appuie sur ok ou si l'utilisateur ferme la fenetre alors les listes sont vidées graphiquement. 
        
        #si l'utilisateur clique sur OK alors la liste d esepce selectionnee est transferee dans la table sleect_faune--/--flore.
        if self.dlg_Flo.exec_():
            self.ajout_ls_espece_pg('fl')
        
        if self.dlg_Flo.close():
            self.dlg_Flo.tab_flore_selected.clearContents()
            self.dlg_Flo.matablewidget.clearContents()
            self.dlg_Flo.tab_flore_selected.setRowCount(0)
            self.dlg_Flo.matablewidget.setRowCount(0)
            self.dlg_Flo.combosearch.clear()

        



    
            
####################################################################################        
##############        FONCTIONS POUR FAUNE FLORE                 ###################
####################################################################################
        
   
 
        
    
    #Fonction pour vider les tables de flore select et faune select.
    #Lacement de la suppression en mettant un parametre de type (flore ou faune : fl/fa)
    def vider_la_table(self,typesuppr):
        
        #CONTROLE: transformation du parametre en nom de table.
        if typesuppr == 'fa':
            matable = 'export.w_faune_select'
        elif typesuppr =='fl':
            matable = 'export.w_flore_select'
        else:
            print 'erreur sur la table à vider.'
        
        
        idconnexion = ("dbname=%s host=%s user=%s password=%s") % (self.get_db_name(), self.get_host_ip(), self.get_dbuser_name(), self.get_pswrd())
        conn = psycopg2.connect(idconnexion)
        cur = conn.cursor()
        marequete = """
        DELETE FROM %s
        """ % self.tr(matable)
        print marequete
        cur.execute(marequete)
        #passage du parametre pour taper dans daune ou flore.
        conn.commit()
        conn.close()
        #On vide la boite de dialogue.
        if typesuppr == 'fa':
            self.dlg_F.tab_faune_selected.clearContents()
            self.dlg_F.tab_faune_selected.setRowCount(0)
            
        if typesuppr == 'fl':
            self.dlg_Flo.tab_flore_selected.clearContents()
            self.dlg_Flo.tab_flore_selected.setRowCount(0)
            
            
            
            
    def ajout_ls_espece_pg(self,typeadd):
        #CONTROLE: transformation du parametre en noms de tables.
        if typeadd == 'fa':
            matable_select = self.tr('export.w_faune_select')
            ma_wref = self.tr('bdfauneflore.w_ref_faune')
                    #Création d'une liste convertie en string   + guillemets + parentheses pour la passer en parametre dans la requeet SQL.

                        
            compterow = self.dlg_F.tab_faune_selected.rowCount()
            
            malisteid=[]
            for i in xrange(0,compterow):
                malisteid.append(self.dlg_F.tab_faune_selected.item(i,0).text())

            
            
            
        
        elif typeadd =='fl':
            matable_select = self.tr('export.w_flore_select')
            ma_wref = self.tr('bdfauneflore.w_ref_flore')
                    #Création d'une liste convertie en string   + guillemets + parentheses pour la passer en parametre dans la requeet SQL.

                        
            compterow = self.dlg_Flo.tab_flore_selected.rowCount()
            
            malisteid=[]
            for i in xrange(0,compterow):
                malisteid.append(self.dlg_Flo.tab_flore_selected.item(i,0).text())

            
            
        
        if malisteid: #Syntaxe pour vérifier que la liste ne soit pas vide.   
            malisteid = "', '".join(malisteid)
            malisteid = self.tr("('" + malisteid + "')")
            idconnexion = ("dbname=%s host=%s user=%s password=%s") % (self.get_db_name(),
                                                                       self.get_host_ip(), self.get_dbuser_name(),
                                                                       self.get_pswrd())
            conn = psycopg2.connect(idconnexion)
            cur = conn.cursor()
            
            #On vide la table pour éviter d'insérer des doublons (optimisation)
            #TODO: Ajouter un Vaccum pour éviter une surcharge del a table à long terme.
            marequete1="""
            delete from %s
            """ %matable_select
            cur.execute(marequete1)
            conn.commit()
            cur.close()
            cur=conn.cursor()
                    
            #Envoi de nos parametres dans la liste espece_select
            especeid =   '(espece_id'    
            marequete2 ="""
            insert into %s  %s, taxon, nomcommun%s
            select espece_id, taxon, nomcommun 
            from %s bdf
            where bdf.espece_id in %s
            """ % (matable_select, self.tr('(espece_id'), self.tr(')'), ma_wref, malisteid)
            print marequete2
            cur.execute(marequete2)
            conn.commit()
            conn.close
    
            #Fonction pour lancer la recherche d'éléments dans la liste d'espèce.
    
    
    
    
    
    
    
    def va_chercher(self, typecherche):
        if typecherche == 'fa':
            matable_select = self.tr('export.w_faune_select')
            ma_wref = self.tr('bdfauneflore.w_ref_faune')
            maliste_wref = self.dlg_F.matablewidget
            marecherche = self.dlg_F.search_bar.text()
            moncritere = self.dlg_F.combosearch.currentText()
        elif typecherche == 'fl':
            matable_select = self.tr('export.w_flore_select')
            ma_wref = self.tr('bdfauneflore.w_ref_flore')
            maliste_wref = self.dlg_Flo.matablewidget
            marecherche = self.dlg_Flo.search_bar.text()
            moncritere = self.dlg_Flo.combosearch.currentText()
        
        if len(marecherche)<3:
            return
        else:
            maliste_wref.clearContents()
            maliste_wref.setRowCount(0)
            marecherche = '%' + marecherche + '%'
            idconnexion = ("dbname=%s host=%s user=%s password=%s") % (self.get_db_name(), self.get_host_ip(), self.get_dbuser_name(), self.get_pswrd())
            conn = psycopg2.connect(idconnexion)
            cur = conn.cursor()
            marequete = """
            select w.espece_id, w.taxon, w.nomcommun, w.classe, w.ordre, w.cd_nom, w.cd_ref ,w.rarepic ,w.menapic
            from %s w
            where %s%s%s iLIKE '%s'

            
            """ % (ma_wref, 'CAST(', moncritere, ' AS TEXT)', marecherche)
            # le ILIKE permet une recherche insensible à la casse, mais augmente considérablement le temps de requetage.
             
            cur.execute(marequete)
            
            if typecherche == 'fl':
                for i in cur:
                    self.dlg_Flo.peupler_table_from_base(self.dlg_Flo.matablewidget,i)
                #Trier les résultats par taxon.
                self.dlg_Flo.matablewidget.sortItems(1)

                    
            elif typecherche =='fa':
                for i in cur:
                    self.dlg_F.peupler_table_from_base(self.dlg_F.matablewidget,i)
                    self.dlg_F.matablewidget.sortItems(1)

            cur.close()
            conn.close()
            
            
            


           
        

####################################################################################
####################################################################################
##############                                                   ###################
##############                                                   ###################
##############            LANCE-REQUETE                          ###################
##############                                                   ###################
##############                                                   ###################
####################################################################################
####################################################################################


    def _1_requeteGenerale(self):
        
        idconnexion = ("dbname=%s host=%s user=%s password=%s") % (self.get_db_name(), self.get_host_ip(), self.get_dbuser_name(), self.get_pswrd())

        
        

        
        ##########################
        #APPEL DE LA PARTIE 1 / 3#
        ##########################
        conn = psycopg2.connect(idconnexion)
        cur = conn.cursor()
        marequete = """
        SELECT export._1_recupdesid('{%s}'::int[]) ;
        """ % self.recup_id()

        cur.execute(marequete)
        conn.commit()
        #DEBUG
        #Affichage des log PG
        #for notice in conn.notices:
            #print notice
        conn.close()
        
        print marequete  



    def _2_moissonneuse_bateuse(self):
        idconnexion = ("dbname=%s host=%s user=%s password=%s") % (self.get_db_name(), self.get_host_ip(), self.get_dbuser_name(), self.get_pswrd())

        #Récupération des DATES à passer en param
        #Conservation dun structure lourde en yyyy pour faciliter un eventuel passage en jj.mm.yyyy.
        if self.dlg.radioSaisie.isChecked() == True:
            self.datemin = self.dlg.date_min_pec.date().toString("dd-MM-yyyy")
            self.datemax = self.dlg.date_max_pec.date().toString("dd-MM-yyyy")
            self.booldate = 'True'
        elif self.dlg.radioObs.isChecked() == True:
            self.datemin = self.dlg.date_min_pec.date().toString("yyyy")
            self.datemax = self.dlg.date_max_pec.date().toString("yyyy")
            self.booldate ='False'
            
            
            
        #Récupération des ESPECES en checkant le RadioButton. 
        if self.dlg.rad_all_espece.isChecked() == True:
            self.boolespece = 'False'
        elif self.dlg.rad_slc_espece.isChecked()== True:
            self.boolespece = 'True'
            
            
        #Verification de si l on desire toute la flore ou toute la faune.
        if self.dlg.checkFlore.isChecked() == True:
            self.boolflore = 'True'
        else:
            self.boolflore = 'False'
            
        if self.dlg.checkFaune.isChecked() == True:
            self.boolfaune = 'True'
        else:
            self.boolfaune = 'False'        
        
        
        #Vérification de la checkbox du parametre pour définir si l'on veut les ESPECES VALIDES.
        if self.dlg.obj_valide.isChecked() == True:
            self.boolvalid = 'True'
        elif self.dlg.obj_valide.isChecked() == False:
            self.boolvalid = 'False'
        else:
            return
        
        
        
        #Vérification de la checkbox de parametres pour définir si l'on veut les éspèces PRESENTES.
        if self.dlg.obj_present.isChecked() == True:
            self.boolpresent = 'True'
        elif self.dlg.obj_present.isChecked() == False:
            self.boolpresent = 'False'
        else:
            return


        
        #Vérification de la checkbox de parametres pour définir si l'on veut les données externes.
        if self.dlg.radioExt.isChecked() == True:
            self.boolexterne = 'True'
        elif self.dlg.radioExt.isChecked() == False:
            self.boolexterne = 'False'
        else:
            return

        
        
        
         ##########################
         #APPEL DE LA PARTIE 2 / 3#
         ##########################
        conn = psycopg2.connect(idconnexion)
        cur = conn.cursor()
        marequete = """
        SELECT export._2_filtrage(%s, %s, %s, %s, '%s', '%s', %s, %s, %s) ;
        """ % (self.boolespece, self.boolfaune, self.boolflore, self.booldate,
                self.datemin, self.datemax, self.boolvalid, self.boolpresent,
                 self.boolexterne)
        
        cur.execute(marequete)
        conn.commit()
        #DEBUG
        #Affichage des log PG
        #for notice in conn.notices:
            #print notice
        conn.close()
        
        print marequete  
              
    
    
    
    
    #Appeler la fonction d export qui genere TABLES + CSV
    def _3_Fichier_CSV(self, typeExport):

            
            
        #Définition du nom par defaut.
        nomCsv = "\\ST_PRINCIPAL.csv"
        idconnexion = ("dbname=%s host=%s user=%s password=%s") % (self.get_db_name(), self.get_host_ip(), self.get_dbuser_name(), self.get_pswrd())
        conn = psycopg2.connect(idconnexion)
        cur = conn.cursor()
        
        #fonction géénrique de recuperation dans notre table de type d export la fonction associée au type.
        marequete = """select fonction from export.w_type_export where nom = '%s' """ % typeExport        
        cur.execute(marequete)
        myfunc = cur.fetchone()[0]
        #Appel de la fonction en replacant le nom de variable par la variable en parametre.
        marequete2 = "SELECT " + str(myfunc)
        cur.execute(marequete2)
        conn.commit()
        conn.close()

    
    
    #Fonction d Export SIG au format SHP.
    def _4_Export_SIG(self, typeExport):
        idconnexion = ("dbname=%s host=%s user=%s password=%s") % (self.get_db_name(), self.get_host_ip(), self.get_dbuser_name(), self.get_pswrd())
        conn = psycopg2.connect(idconnexion)
        cur = conn.cursor()
        marequete = """select ogr2ogr from export.w_type_export where nom = '%s' """ % typeExport 
        cur.execute(marequete)
        myOgr = cur.fetchone()[0]
        
        #Chercher le .bat à lancer.
        monpath = "S:/00_MODULE_EXPORT_BDCEN/batfiles/"
        print os.path.normpath(monpath + myOgr)
        call(os.path.normpath(monpath + myOgr),shell=True)
        
            





    
    def _5_Metadonne(self):
        idconnexion = ("dbname=%s host=%s user=%s password=%s") % (self.get_db_name(), self.get_host_ip(), self.get_dbuser_name(), self.get_pswrd())
        conn = psycopg2.connect(idconnexion)
        cur = conn.cursor()
        
        
        #Création du XML avec parametres adéquats.
        #Création de mon arbre XML en mémoire VIVE.
        modelExport = minidom.Document()
        
        #Création de ma racine. ROOT
        newroot = modelExport.createElement('root')
        #On ajoute le root a l arbre
        modelExport.appendChild(newroot)
        
        #Création de la grande secton de paramexport
        paramexport = modelExport.createElement('parametres_d_export')
        
        #On ajoute la paramexport a la root
        newroot.appendChild(paramexport)
        
        
        #Création de OBJETSSIG
        objetsig = modelExport.createElement('ObjetsSIG')
        paramexport.appendChild(objetsig)
        
        #Création des ENTITE dans objetSIG.
        #Remplacer liste par mes id.
        
        self.iface.activeLayer().selectedFeatures ()
        
        
        for i in self.iface.activeLayer().selectedFeatures():
            entite = modelExport.createElement('id')
            entite.setAttribute('ID', str(i[0]))
            entite.setAttribute('libelle', str(i[1]))
            objetsig.appendChild(entite)
            
        
        #Création de la section de PARAMETRE D OBJETS
        paramobjets = modelExport.createElement('paramobjets')
        
        
        
        #La donnée est-elle valide?
        if self.boolvalid == True:
            nodeValid = "Valide uniquement"
        else:
            nodeValid ="Valide et invalide"
        paramobjets.setAttribute('Validite_de_la_donnee', nodeValid)
        
        
        
        #La Présence de l espece est-elle une certitude?
        if self.boolpresent == True:
            nodePresabs = "Présence attestee"
        else:
            nodePresabs = "Absence"
        paramobjets.setAttribute('Certitude_de_presence', nodePresabs)
        
        #La donne externe est elle exclue?
        if self.boolexterne == True:
            nodeExt = "Inclusion"
        else:
            nodeExt = "Exclusion"
        paramobjets.setAttribute('Donnée_externe', nodeExt)
        
        paramexport.appendChild(paramobjets)
        
        
        
        
        
        #Création de la DATE.
        date = modelExport.createElement('param_date')
        
        
        #La date prote sur?
        if self.booldate == True:
            nodeDate = "La saisie"
        else:
            nodeDate = "La date d'observation"
        date.setAttribute('date_portant_sur', nodeDate)
        
        #date min de prise en compte     
        date.setAttribute('date_minimale_de_prise_en_compte', str(self.datemin))
        #date max de prise en compte
        date.setAttribute('date_maximale_de_prise_en_compte', str(self.datemax))
        
        paramobjets.appendChild(date)
        
        ############################################################################
        # RESUME_EXPORT
        resumexport = modelExport.createElement("Resume_export")
        typeexp = self.dlg.comboExport.currentText()
        typeexp = typeexp.encode('UTF-8','ignore')
        resumexport.setAttribute('Type_export',typeexp )
        newroot.appendChild(resumexport)
        
        #Qui est destinatiare?
        ledestina= modelExport.createElement("Destinataire")
        
        #nom export
        nomlabel = str(self.dlg.libele.text())
        nomlabel= nomlabel.encode('UTF-8', 'ignore')
        ledestina.setAttribute('libele_export', nomlabel)
        
        #interlocuteur
        nomdest = str(self.dlg.destinataire.text())
        nomdest=nomdest.encode('UTF-8', 'ignore')
        ledestina.setAttribute('interlocuteur', nomdest)
        
        #Structure
        nomstruc = str(self.dlg.structure.text())
        nomstruc=nomstruc.encode('UTF-8', 'ignore')
        ledestina.setAttribute('structure', nomstruc)
        
        resumexport.appendChild(ledestina)
        
        #STATISTIQUES
        #Somme individus
        statists = modelExport.createElement("stats_especes")
        marequete = "SELECT COUNT(i.id_perm) FROM export.r_id_all i WHERE i.presence IS TRUE"
        cur.execute(marequete)
        totalent = str(cur.fetchone()[0])
        statists.setAttribute("Nombre_total_d_entite",totalent)
        
        #Somme taxons
        marequete = """SELECT SUM (count)
                        FROM
                        (SELECT COUNT (DISTINCT t.taxon)
                        FROM 
                        export.r_id_all i, bdfauneflore.t_bilan_faune t 
                        WHERE i.id_perm = t.id_perm 
                        AND i.presence IS TRUE
                        UNION
                        SELECT COUNT (DISTINCT t.taxon)
                        FROM 
                        export.r_id_all i, bdfauneflore.t_bilan_flore t 
                        WHERE i.id_perm = t.id_perm 
                        AND i.presence IS TRUE) AS x"""
        cur.execute(marequete)
        totalent = str(cur.fetchone()[0])
        statists.setAttribute("Nombre_total_de_taxons", totalent)
        
        resumexport.appendChild(statists)
        
        #NB FAUNE EXPORT
        
        #compte d individus
        enfa = modelExport.createElement("faune_exportees")
        marequete= "SELECT COUNT (i.id_perm) FROM \
        export.r_id_all i, bdfauneflore.t_bilan_faune t WHERE i.id_perm = t.id_perm AND i.presence IS TRUE"
        cur.execute(marequete)
        nbenfa = str(cur.fetchone()[0])
        enfa.setAttribute('nombre_d_entites', nbenfa)


        # compte d especes.
        marequete= "SELECT COUNT (DISTINCT t.taxon) FROM \
        export.r_id_all i, bdfauneflore.t_bilan_faune t WHERE i.id_perm = t.id_perm AND i.presence IS TRUE"
        cur.execute(marequete)
        nbenfa = str(cur.fetchone()[0])
        enfa.setAttribute('nombre_d_especes', nbenfa)
        
        statists.appendChild(enfa)

        #LISTE TAXONS
        if nbenfa !=0:
            marequete= "SELECT DISTINCT t.taxon FROM  export.r_id_all i,\
             bdfauneflore.t_bilan_faune t WHERE i.id_perm = t.id_perm AND i.presence IS TRUE"
            cur.execute(marequete)

            for i in cur:
                nbesfa = i[0]
                
                childEnfa = modelExport.createElement("taxon")
                if nbesfa is None:#resolution de bug: si type est null alors valeur arbitraire
                    
                    childEnfa.setAttribute('Taxon', "NONETYPE")
                    enfa.appendChild(childEnfa)
                else:
                    nbesfa = nbesfa.encode('UTF-8','ignore')#necessite de reencoder
                    childEnfa.setAttribute('Taxon', nbesfa)
                    enfa.appendChild(childEnfa)
            

        #NB FLORE EXPORT
        
        #nb entite flore exportees
        efle = modelExport.createElement("flore_exportees")
        marequete= "SELECT COUNT (i.id_perm) FROM \
        export.r_id_all i, bdfauneflore.t_bilan_flore t WHERE i.id_perm = t.id_perm AND i.presence IS TRUE"
        cur.execute(marequete)
        nbefle = str(cur.fetchone()[0])
        efle.setAttribute('nombre_d_entites', nbefle)
        
        
        # compte d especes.
        marequete= "SELECT COUNT (DISTINCT t.taxon) FROM \
        export.r_id_all i, bdfauneflore.t_bilan_flore t WHERE i.id_perm = t.id_perm AND i.presence IS TRUE"
        cur.execute(marequete)
        nbefle = str(cur.fetchone()[0])
        efle.setAttribute('nombre_d_especes', nbefle)
        
        
        statists.appendChild(efle)

        #LISTE TAXON

        if nbefle != 0:
            marequete= "SELECT DISTINCT t.taxon FROM  export.r_id_all i,\
             bdfauneflore.t_bilan_flore t WHERE i.id_perm = t.id_perm AND i.presence IS TRUE"
            cur.execute(marequete)
    
            for i in cur:
                nbefle = i[0]
                childEsle = modelExport.createElement("taxon")
                if nbefle is None:
                    childEsle.setAttribute('Taxon', "NONETYPE")
                    efle.appendChild(childEsle)
                else:
                    nbefle = nbefle.encode('UTF-8','ignore')
                    childEsle.setAttribute('Taxon', nbefle)
                    efle.appendChild(childEsle)

        
        conn.commit()
        conn.close()
        
        ############################################################################
        
        #DESCRIPTION DE LA DONNEE
        descdata = modelExport.createElement("Description_des_donnees")
        newroot.appendChild(descdata)
        
        # dateexport 
        
        # resume des formats
        lesformats = modelExport.createElement("formats")
        dateExport = time.strftime("%d/%m/%Y")
        lesformats.setAttribute('date_export',dateExport)
        descdata.appendChild(lesformats)
        
        # Recap du CSV
        csv_xml = modelExport.createElement("csv_format")
        
        
        #Encodage
        csv_xml.setAttribute('encodage',"UTF-8")
        
        
        #separateur
        csv_xml.setAttribute('separateur',";")
        
        lesformats.appendChild(csv_xml)
        
        
        #sig_format
        sig_xml = modelExport.createElement("sig_format")
        
        
        # shapefile?
        sig_xml.setAttribute('extension',"Shapefile")
        # SCR?
        sig_xml.setAttribute('SCR',"Lambert 93")
        
        lesformats.appendChild(sig_xml)
        
        sortieXML = modelExport.toprettyxml()
        ecrirexml = open(os.path.normpath('S:/00_MODULE_EXPORT_BDCEN/exports/exportmedatada.xml'), 'w')
        ecrirexml.write(sortieXML)
        ecrirexml.close()
    
####################################################################################
######################### FONCTIONS NETTOYAGE ######################################
####################################################################################


    def nettoyage_des_tables(self):
        idconnexion = ("dbname=%s host=%s user=%s password=%s") % (self.get_db_name(), self.get_host_ip(), self.get_dbuser_name(), self.get_pswrd())
        conn = psycopg2.connect(idconnexion)
        cur = conn.cursor()
        marequete = """select export.kill_table()"""
        cur.execute(marequete)
        conn.commit()
        conn.close()
        QMessageBox.information(self.dlg,'Information',u'Nettoyage des tables effectué.')
        
        
    def nettoyage_dossier_export(self):
        mondossier = os.path.normpath('S:/00_MODULE_EXPORT_BDCEN/exports')
        cpt = 0
        listdel =[]
        for filename in os.listdir(mondossier) :
            cpt+=1
            listdel.append(os.path.split(mondossier + '/' + filename)[1])
            os.remove(mondossier + '/' + filename)

            
        elemsuppr = u"%s éléments ont étés supprimés:" %cpt
        QMessageBox.information(self.dlg,'Information',u'Nettoyage du dossier d\'export effectué.' + '\n' + elemsuppr \
                                + "\n" + ("\n".join(listdel)))
####################################################################################
####################################################################################
##############                                                   ###################
##############                                                   ###################
##############                      RUN                          ###################
##############                                                   ###################
##############                                                   ###################
####################################################################################
####################################################################################
    def lancement_des_operations(self):
        #Structure de controle date de saisie
        if self.dlg.radioSaisie.isChecked() == True:
            if self.dlg.date_min_pec.date() > self.dlg.date_max_pec.date():
                QMessageBox.warning(self.dlg,'Information',u'La date minimum de saisie doit être inférieure à la maximale')
                return
            
        #Structure de controle date d observation
        if self.dlg.radioObs.isChecked() == True:
            if self.dlg.date_min_pec.date() > self.dlg.date_max_pec.date():
                QMessageBox.warning(self.dlg,'Information',u'La date minimum d\'observation doit être inférieure à la maximale')
                return
          
         

        self.dlg.progressBar.show()
        self.dlg.avancee.show()
        
        self.dlg.avancee.setText(u'1.Procédure de filtrage géographique en cours.')
        self._1_requeteGenerale()
        self.dlg.progressBar.setValue(25)
        
        self.dlg.avancee.setText(u'2.Procédure de filtrage attributaire en cours.')
        self._2_moissonneuse_bateuse()
        self.dlg.progressBar.setValue(40)
        
        self.dlg.avancee.setText(u"3.Procédure de génération des tables et CSV en cours.")
        self._3_Fichier_CSV(typeExport = self.dlg.comboExport.currentText())
        self.dlg.progressBar.setValue(50)
        
        self.dlg.avancee.setText(u"4.Procédure d'export des éléments géographiques en cours")
        self._4_Export_SIG(typeExport = self.dlg.comboExport.currentText())
        self.dlg.progressBar.setValue(85)
        
        self.dlg.avancee.setText(u"5.Procédure de génération de métadonnées XML en cours")
        self._5_Metadonne()
        self.dlg.progressBar.setValue(100)
        self.dlg.avancee.setText(u"Export terminé")
        
        
        
        
        print self.get_db_name()
        print self.get_host_ip()
        print self.get_table_name()
        print self.get_dbuser_name()
        print self.get_pswrd()
            
        QMessageBox.information(self.dlg,'Information',u'L\'export a été réalisé avec succès!')
        
        if self.dlg.checkClean.isChecked():
            self.nettoyage_des_tables()
        self.dlg.progressBar.hide()
        self.dlg.avancee.hide()
    def run(self):
        
        #CONTROLE : verifier si une couche est bien selectionnée
        if self.iface.activeLayer() == None :
            QMessageBox.information(self.iface.mainWindow(),'Information',u'Veuillez selectionner une couche à connecter')
            return
        else : 
            #CONTROLE :  : Si couche selectioné est un raster => exit
            #MODIF LOIC
            if self.iface.activeLayer().type() == 2 or self.iface.activeLayer().type() == 1:
                QMessageBox.information(self.iface.mainWindow(),'Information',u'Veuillez selectionner une couche vecteur')
                return


        #CONTROLE :  verifier si des objets sont selectionnés
        if  self.iface.activeLayer().selectedFeatureCount () <= 0 :
            QMessageBox.information(self.iface.mainWindow(),'Information',u'Vous devez selectionner au moins un objet')
            return
        
        #CONTROLE : Si ma couche ne s'appelle pas z_export, alors erreur.
        if self.iface.activeLayer().name() != u"z_export" :
            QMessageBox.information(self.iface.mainWindow(),'Information',u'Vous devez selectionner la couche z_export')
            return
        
        
        
        self.peuplerComboExport()
        self.dlg.show()
        
