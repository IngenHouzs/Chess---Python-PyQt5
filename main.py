
import PyQt5.QtWidgets as qtw   
import sys  


import setupUI

# Main Module

if __name__ == '__main__': 
    app = qtw.QApplication(sys.argv)  
    main_window = setupUI.Ui_MainWindow()
    main_window.show()
    sys.exit(app.exec())
    