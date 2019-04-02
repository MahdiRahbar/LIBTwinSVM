# -*- coding: utf-8 -*-

# Developers: Mir, A. and Mahdi Rahbar
# Version: 0.1 - 2019-03-20
# License: GNU General Public License v3.0

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from libtsvm.ui import view
from libtsvm.preprocess import load_data
import sys


class LIBTwinSVMApp(view.Ui_MainWindow, QMainWindow):
    
    def __init__(self):
        
        super(LIBTwinSVMApp, self).__init__()
        
        self.setupUi(self)
        self.init_GUI()
        
    def init_GUI(self):
        """
        Initialize the GUI of application
        """
        
        self.open_btn.clicked.connect(self.get_data_path)
        self.load_btn.clicked.connect(self.load_data)
        
        
    def get_data_path(self):
        """
        gets the dataset path from a user.
        """
        
        data_filename, _ = QFileDialog.getOpenFileName(self, "Import dataset",
                                                       "", "CSV files (*.csv)")
        
        if data_filename:
            
            self.path_box.setText(data_filename)
            
    def load_data(self):
        """
        Loads a dataset
        """
        
        self.X_train, self.y_train = load_data(self.path_box.text(),
                                    self.sep_char_box.text(),
                                    True if self.header_check.isChecked() else False,
                                    True if self.shuffle_box.isChecked() else False,
                                    True if self.normalize_box.isChecked() else False)
        
        print(self.X_train)
        print(self.y_train)
     
        
def main():
    
   app = QApplication(sys.argv)
   libtsvm_app = LIBTwinSVMApp()
   libtsvm_app.show()
   sys.exit(app.exec_())
 
