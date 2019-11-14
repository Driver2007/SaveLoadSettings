from javax.swing import JButton, JFrame, JTable, JScrollPane, JLabel, JPanel, BoxLayout, Box, JFileChooser, JOptionPane
from javax.swing.filechooser import FileNameExtensionFilter
from javax.swing.table import DefaultTableModel, DefaultTableCellRenderer
from javax.swing.event import TableModelEvent, TableModelListener
from java.lang import Boolean, Object
from java.io import File
from java.awt import Font, Dimension, BorderLayout

from org.csstudio.opibuilder.scriptUtil import PVUtil
from org.csstudio.opibuilder.util import BOYPVFactory
from org.eclipse.core.runtime.jobs import Job
from org.eclipse.core.runtime import Status

#import time
import datetime
import os

DEFAULT_EXTENSION = "set"
### keep the following variables consistent!
PV_COLUMN = 0
ID_COLUMN = 1
VALUE_COLUMN = 2
SETTING_COLUMN = 3 # only exists if savemode == True
RESTORE_COL_LOADMODE = 4
RESTORE_COL_SAVEMODE = 3
TABLE_HEADER_SAVEMODE = ('PV', 'ID', 'Current', 'Save?')
TABLE_HEADER_LOADMODE = ('PV', 'ID', 'Current', 'Setting', 'Load?')
### **********************************
FONT_FAMILY = "Lucida Sans Typewriter"

###############################################################################################
###########################     Helper classes    #############################################
###############################################################################################

class MyTableModel(DefaultTableModel):
    def __init__(self, *args, **kwargs):
        savemode = False
        if 'savemode' in kwargs:
            savemode = kwargs.pop('savemode')
        DefaultTableModel.__init__(self, *args, **kwargs)
        if savemode:
            self.checkbox_column = 3
        else:
            self.checkbox_column = 4

    def isCellEditable(self, row, column):
        return column==self.checkbox_column or column==2

    def getColumnClass(self, column):
        if column == self.checkbox_column:
            return Boolean
        return DefaultTableModel.getColumnClass(self, column)

class BackgroundPVWriter(Job):
    # this PV writer does not report any errors (workaround for faulty asyncWrite in TangoPV)
    def __init__(self, pvname, val):
        Job.__init__(self, "Writing PV " + pvname)
        self.pvname = pvname
        self.val = val
        self.setPriority(Job.SHORT)

    def run(self, monitor):
        ipv = BOYPVFactory.createPV(self.pvname)
        ipv.start()
        ipv.setValue(self.val, 2000) # timeout of 2 seconds
        ipv.stop()
        return Status.OK_STATUS

class MyTableModelListener(TableModelListener):
    def __init__(self, *args, **kwargs):
        savemode = False
        if 'savemode' in kwargs:
            savemode = kwargs.pop('savemode')
        TableModelListener.__init__(self, *args, **kwargs)
        self.savemode = savemode

    def tableChanged(self, tablemodelevent):
        if not tablemodelevent.getType() in (tablemodelevent.UPDATE, tablemodelevent.INSERT):
            return
        if tablemodelevent.getColumn() != VALUE_COLUMN:
            return # only write PV when the user edited a value in the 'Current' column
        row = tablemodelevent.getFirstRow()
        tm = tablemodelevent.getSource() # get the table model (i.e. table data)
        val = tm.getValueAt(row, VALUE_COLUMN)
        pvname = tm.getValueAt(row, PV_COLUMN)
        # try to convert to int. If unsuccesful, convert to float. If unsuccesful, leave as string
        try:  
            val = int(val)
        except ValueError:
            try:
                val = float(val)
            except ValueError:
                pass
        #PVUtil.writePV(pvname, val)
        pv_writer = BackgroundPVWriter(pvname, val)
        pv_writer.schedule()
        # if not in savemode (i.e. if in load mode), deactivate the restore checkbox
        # because the user will not want to load the value if he edited the current value
        if not self.savemode:
            tm.setValueAt(False, row, RESTORE_COL_LOADMODE)
        

class MyTableCellRenderer(DefaultTableCellRenderer):
    def __init__(self, *args, **kwargs):
        font, fontsize, style = "SansSerif", 12, Font.PLAIN
        if 'fontsize' in kwargs:
            fontsize = kwargs.pop('fontsize')
        if 'style' in kwargs:
            style = kwargs.pop('style')
        if 'font' in kwargs:
            font = kwargs.pop('font')
        DefaultTableCellRenderer.__init__(self, *args, **kwargs)
        self.font_ = Font(font, style, fontsize)

    def getTableCellRendererComponent(self, table, val, isSel, hasFoc, row, column):
        c = DefaultTableCellRenderer.getTableCellRendererComponent(self, table, val, isSel, hasFoc, row, column)
        c.setFont(self.font_)
        return c

def SetFontRecursively(ComponentArray, font):
    for c in ComponentArray:
        subcomps = None
        try:
            subcomps = c.getComponents()
            SetFontRecursively(subcomps, font)
        except:
            pass
        try:
            c.setFont(font)
        except:
            pass

###############################################################################################
#################     SettingsTableFrame class    #############################################
###############################################################################################

class SettingsTableFrame(JFrame):
    def __init__(self, *args, **kwargs):
        # do not create any class members before calling JFrame.__init__ !
        s, size, title, savemode = None, None, None, False
        self.OKstatus = True
        if 'settings_config' in kwargs:
    	    s = kwargs.pop('settings_config')
        else:
            s = None
        if 'size' in kwargs:
            size = kwargs.pop('size')
        else:
            size = (300,300)
        if 'widget' in kwargs:
            widget = kwargs.pop('widget')
        else:
            widget = None
        if 'savemode' in kwargs:
            savemode = kwargs.pop('savemode')
        defaultdir = None
        if 'defaultdir' in kwargs:
            defaultdir = kwargs.pop('defaultdir')
        if len(args)>0:
            title = args[0]
        else:
            title = 'Save Settings'
        JFrame.__init__(self, title, size=size, **kwargs)
        self.widget = widget
        if self.widget==None:
            print "Need to pass keyword argument widget=widget when creating SettingsTableFrame" 
        self.s = s
        self.savemode = savemode
        self.defaultdir = defaultdir
        # create FileChooser, make its window bigger and choose smaller font
        if self.defaultdir!=None:
            self.fc = JFileChooser(self.defaultdir)
        else:
            self.fc = JFileChooser()
        self.fc.setPreferredSize(Dimension(800,600))
        smallfont = Font("Lucida Sans", Font.PLAIN, 12)
        SetFontRecursively(self.fc.getComponents(), smallfont)
        filefilter = FileNameExtensionFilter("Settings Files", (DEFAULT_EXTENSION,))
        self.fc.setFileFilter(filefilter)
        # fill the table, in save mode only with the current values, in load mode with current and setting values
        self.prepare_tabledata()
        # if not savemode, we first pop up a filechooser to select a loadable setting
        if self.savemode==False:
            self.OKstatus = self.load_setting()
            if not self.OKstatus:
                return
        # listener for data edited by user, good for providing PV write access within the table to the user
        self.dataListener = MyTableModelListener(savemode=self.savemode)
        self.dataModel.addTableModelListener(self.dataListener)
        self.table = JTable(self.dataModel)
        # create Buttons
        self.bu_do_label = "Save" if self.savemode==True else "Load"
        self.bu_do_handler = self.bu_save_handler if self.savemode==True else self.bu_load_handler
        self.bu_do = JButton(self.bu_do_label, actionPerformed=self.bu_do_handler)
        self.bu_cancel = JButton("Cancel", actionPerformed=self.bu_cancel_handler)
        # BEGIN visual adaptations of JTable
        self.table.setRowHeight(24)
        self.table.getColumnModel().getColumn(0).setMinWidth(200)
        if self.savemode:
            self.table.getColumnModel().getColumn(3).setMaxWidth(60)
        else:
            self.table.getColumnModel().getColumn(4).setMaxWidth(60)            
        smallfontr = MyTableCellRenderer(font=FONT_FAMILY, style=Font.PLAIN, fontsize=10)
        smallfontr.setHorizontalAlignment(JLabel.CENTER)
        bigfontplainr = MyTableCellRenderer(font=FONT_FAMILY, style=Font.PLAIN, fontsize=18)
        bigfontplainr.setHorizontalAlignment(JLabel.CENTER)
        bigfontr = MyTableCellRenderer(font=FONT_FAMILY, style=Font.BOLD, fontsize=18)
        bigfontr.setHorizontalAlignment(JLabel.CENTER)
        self.table.getColumnModel().getColumn(0).setCellRenderer(smallfontr)
        self.table.getColumnModel().getColumn(1).setCellRenderer(bigfontplainr)
        self.table.getColumnModel().getColumn(2).setCellRenderer(bigfontr)
        if not self.savemode:
            self.table.getColumnModel().getColumn(3).setCellRenderer(bigfontr)
        # END visual adaptations of JTable
        ## BEGIN layout of window (JFrame)
        self.getContentPane().setLayout(BorderLayout())
        self.add(JScrollPane(self.table))
        self.bottompanel = JPanel()
        self.bottompanel.setLayout(BoxLayout(self.bottompanel, BoxLayout.LINE_AXIS))
        self.bottompanel.add(Box.createHorizontalGlue())
        self.bottompanel.add(self.bu_do)
        self.bottompanel.add(Box.createRigidArea(Dimension(20,0)))
        self.bottompanel.add(self.bu_cancel)
        self.bottompanel.add(Box.createHorizontalGlue())
        self.add(self.bottompanel, BorderLayout.SOUTH)
        # END layout of window (JFrame)

    def bu_cancel_handler(self, event):
        self.dispose()

    def bu_save_handler(self, event):
        dlg_answer = self.fc.showSaveDialog(self)
        if dlg_answer==self.fc.CANCEL_OPTION:
            return
        if dlg_answer==self.fc.APPROVE_OPTION: # user clicked SAVE
            f = self.fc.getSelectedFile().getAbsolutePath()
            if not str(f).endswith("." + DEFAULT_EXTENSION):
                f = f + "." + DEFAULT_EXTENSION
            if os.path.exists(f): # file already exists, let user confirm overwriting
                choice = JOptionPane.showConfirmDialog(self, "The file exists, overwrite?", "Existing file",
                        JOptionPane.YES_NO_CANCEL_OPTION);
                if choice in (JOptionPane.NO_OPTION, JOptionPane.CANCEL_OPTION):
                    return
                if choice == JOptionPane.YES_OPTION:
                    self.do_save(f)
                    self.dispose()
            else: # file does not exist, yet -> don't need to ask
                self.do_save(f)
                self.dispose()

    def bu_load_handler(self, event):
        for i in range(self.dataModel.getRowCount()):
            if self.dataModel.getValueAt(i, RESTORE_COL_LOADMODE)==False:
                continue
            curval = self.dataModel.getValueAt(i, VALUE_COLUMN)
            setval = self.dataModel.getValueAt(i, SETTING_COLUMN)
            if curval=='---' or setval=='---': # either PV does not exist or value missing in the settings file
                continue
            pvname = self.dataModel.getValueAt(i, PV_COLUMN)
            writejob = BackgroundPVWriter(pvname, setval)
            writejob.schedule()
        self.dispose()

    def load_setting(self):
        dlg_answer = self.fc.showOpenDialog(self)
        if dlg_answer==self.fc.CANCEL_OPTION:
            return False
        if dlg_answer==self.fc.APPROVE_OPTION:
            f = self.fc.getSelectedFile().getAbsolutePath()
            self.parse_setting(f)
            return True
    
    def parse_setting(self, fpath): # compatible to old set files
        with open(fpath, "r") as f:
            idxset = set(range(self.dataModel.getRowCount()))
            #lbuf = [l for l in f] # need to create a file buffer to traverse twice through the file
            for l in f:
                if len(l)==0 or l.startswith('#'):
                    continue
                els = l.split()
                idstr = els[0]
                checkcolumn = ID_COLUMN
                for i in idxset:
                    if self.dataModel.getValueAt(i, checkcolumn)==idstr:
                        self.dataModel.setValueAt(els[1], i, SETTING_COLUMN)
                        idxset.remove(i)
                        
            # remove restore flag for PVs that were missing in the settings file
            for i in idxset:
                self.dataModel.setValueAt(False, i, RESTORE_COL_LOADMODE)

    def parse_setting_pvtable_format(self, fpath):
        with open(fpath, "r") as f:
            idxset = set(range(self.dataModel.getRowCount()))
            lbuf = [l for l in f] # need to create a file buffer to traverse twice through the file
            # parse ID PVNAME mappings if present
            mapping_header_found = False
            pv_to_id = dict()
            for l in lbuf:
                if not mapping_header_found:
                    if l.startswith("### Mapping ID to PV"):
                        mapping_header_found = True
                    continue
                if not l.startswith("# "):
                    continue
                els = l.split()
                idstr = els[1]
                pvstr = " ".join(els[2:]) # tango PVs may contain blanks if additional parameters were included
                pv_to_id[pvstr] = idstr
            # second run through file: fill our table with values read from the file
            for l in lbuf:
                if len(l)==0 or l.startswith('#'):
                    continue
                els = l.split()
                # default to PVNAME comparison if no PVNAME->ID mapping exists
                idstr = els[0]  
                checkcolumn = PV_COLUMN
                # check if mapping exists, and override if so
                if idstr in pv_to_id:
                    idstr = pv_to_id[idstr] # (set idstr to the mapped ID)
                    checkcolumn = ID_COLUMN # (tell the following code that ID_COLUMN has to be compared)
                for i in idxset:
                    if self.dataModel.getValueAt(i, checkcolumn)==idstr:
                        self.dataModel.setValueAt(els[1], i, SETTING_COLUMN)
                        idxset.remove(i)
                        
            # remove restore flag for PVs that were missing in the settings file
            for i in idxset:
                self.dataModel.setValueAt(False, i, RESTORE_COL_LOADMODE)
                

    def do_save(self, filepath): # creates something compatible to older set files
        now = datetime.datetime.now()
        with open(filepath, "w") as f:
            f.write("### ------------------------------------\n")
            f.write("### SETTING saved from CSS\n")
            f.write("### " + now.strftime("Date: %Y-%m-%d   Time: %H:%M") + "\n")
            f.write("### ------------------------------------\n")
            for row_index in range(self.dataModel.getRowCount()):
                IDstr = str(self.dataModel.getValueAt(row_index, ID_COLUMN))
                valstr = str(self.dataModel.getValueAt(row_index, VALUE_COLUMN))
                f.write("%s %s\n" % (IDstr, valstr))
            f.write("### Mapping ID to PV\n")
            for row_index in range(self.dataModel.getRowCount()):
                IDstr = str(self.dataModel.getValueAt(row_index, ID_COLUMN))
                PVstr = str(self.dataModel.getValueAt(row_index, PV_COLUMN))
                f.write("# %s %s\n" % (IDstr, PVstr))

    def do_save_pvtableformat(self, filepath):
        now = datetime.datetime.now()
        with open(filepath, "w") as f:
            f.write("# save/restore file generated by CSS PVTable, " + now.strftime("%Y-%m-%d %H:%M:0.0")+"\n")
            for row_index in range(self.dataModel.getRowCount()):
                PVstr = str(self.dataModel.getValueAt(row_index, PV_COLUMN))
                valstr = str(self.dataModel.getValueAt(row_index, VALUE_COLUMN))
                f.write("%s %s\n" % (PVstr, valstr))
            f.write("<END>\n")
            f.write("### ------------------------------------\n")
            f.write("### SETTING saved from CSS\n")
            f.write("### " + now.strftime("Date: %Y-%m-%d   Time: %H:%M") + "\n")
            f.write("### ------------------------------------\n")
            f.write("### Mapping ID to PV\n")
            for row_index in range(self.dataModel.getRowCount()):
                IDstr = str(self.dataModel.getValueAt(row_index, ID_COLUMN))
                PVstr = str(self.dataModel.getValueAt(row_index, PV_COLUMN))
                f.write("# %s %s\n" % (IDstr, PVstr))
            
        

    def prepare_tabledata(self):
        if self.s == None:
            self.tableData = [['', '', '', '', False]]
        else:
            self.tableData = []
            for l in self.s:
                idstr = l[0]
                pvname = l[1]
                # read PV value
                curval = "---"
                restore_flag = l[2]
                try:
                    ipv = PVUtil.createPV(pvname, self.widget)
                    curval = PVUtil.getString(ipv)
                except:
                    restore_flag = False
                if self.savemode:
                    self.tableData.append([pvname, idstr, curval, restore_flag])
                else:
                    self.tableData.append([pvname, idstr, curval, '---', restore_flag])

        if self.savemode:
            self.colNames = TABLE_HEADER_SAVEMODE
        else:
            self.colNames = TABLE_HEADER_LOADMODE

        self.dataModel = MyTableModel(self.tableData, self.colNames, savemode=self.savemode)

