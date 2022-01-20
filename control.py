from io import UnsupportedOperation
from statistics import median_grouped
from turtle import setundobuffer
from PyQt5 import QtCore, QtGui, QtWidgets   
from PyQt5.QtGui import QFocusEvent, QIcon, QPainter, QPalette, QPen, QBrush, QColor, QPixmap 
from PyQt5.QtCore import PYQT_VERSION, QRect, QSize, Qt, forcepoint
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QLabel, QMainWindow, QPushButton, QWidget
from pynput import mouse
import string 
import itertools
import functools
import time
import chess
from setuptools import setup

import setupUI

class stockfish_controlRoom: 
    color_listing = []
    def __init__(self, posx, posy, spanx, spany): 
        self.posx = posx 
        self.posy = posy 
        self.spanx = spanx 
        self.spany = spany 

        self.playingWhite = False 
        self.playingBlack = False

    def create_choosePlayBot(self):
        for buttons in GameMode.button_list: 
            buttons.button.setEnabled(True)         
        self.isClicked = False
        self.play_bot_button = QtWidgets.QPushButton(setupUI.main_centralWidget) 
        self.play_bot_button.setGeometry(QtCore.QRect(self.posx, self.posy, self.spanx, self.spany))
        self.play_bot_button.setStyleSheet("""  height: 80px;
                                                line-height: 80px;  
                                                width: 80px;  
                                                font-size: 2em;
                                                font-weight: bold;
                                                border-radius: 50%;
                                                background-color: #FFFFFF;
                                                color: white;
                                                text-align: center;
                                                cursor: pointer;y
                                          """)
        self.play_bot_button.clicked.connect(lambda: self.choosePlayBot_command())
        self.play_bot_button.show() 

    def choosePlayBot_command(self):
        for buttons in GameMode.button_list: 
            buttons.button.setEnabled(True)    
        if self.isClicked:
            self.isClicked = False
            self.play_bot_button.setStyleSheet("""  height: 80px;
                                                    line-height: 80px;  
                                                    width: 80px;  
                                                    font-size: 2em;
                                                    font-weight: bold;
                                                    border-radius: 50%;
                                                    background-color: #FFFFFF;
                                                    color: white;
                                                    text-align: center;
                                                    cursor: pointer;y
                                            """)
            self.play_bot_button.setIcon(QIcon(""))      
            self.widget.deleteLater() 
            if GameMode.choosen_timeControl is not None:
                setupUI.start_button.setEnabled(True)
                setupUI.start_button.setStyleSheet(""" background-color: rgb(37, 217, 79);
                                                        border-style: outset;
                                                        border-radius: 15px;
                                                        border-color: black;
                                                        color: rgb(0,0,0);                                        
                                                        padding: 4px;""")                  
        else: 
            self.isClicked = True
            self.play_bot_button.setIcon(QIcon("Cropped Toggle Animation.png"))
            self.play_bot_button.setIconSize(QtCore.QSize(101, 101)) 
            self.create_BotSettingsWidget()


    def create_BotSettingsWidget(self): 
        setupUI.start_button.setEnabled(False)
        setupUI.start_button.setStyleSheet(""" background-color: rgb(131,145,145);
                                                border-style: outset;
                                                border-radius: 15px;
                                                border-color: black;
                                                color: rgb(252, 252, 252);
box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19);                                                
                                                padding: 4px;""")         
        self.widget = QFrame(setupUI.main_centralWidget) 
        self.widget.setFrameShape(QFrame.StyledPanel) 
        self.widget.resize(500, 600) 
        self.widget.move(1327, 200)

        self.background_widget = QtWidgets.QLabel(self.widget)           
        self.background_widget.setPixmap(QtGui.QPixmap("Bot Control Widget.png"))
        self.background_widget.setGeometry(QtCore.QRect(0,0,500,600))

        self.play_white = QtWidgets.QPushButton(self.widget)
        self.play_white.setStyleSheet("""
                                    background-color: white;
                                    border-style: outset;
                                    border-width: 2px;
                                    border-radius: 10px;
                                    border-color: beige;
                                    font: bold 14px;
                                    padding: 6px
        """)    
        self.play_white.setGeometry(QtCore.QRect(150, 50, 80, 80))
        self.play_white.clicked.connect(lambda : self.BotSettingsWidget_command_white())


        self.play_black = QtWidgets.QPushButton(self.widget)
        self.play_black.setStyleSheet("""
                                    background-color: black;
                                    border-style: outset;

                                    border-radius: 10px;
                                    border-color: beige;
                                    font: bold 14px;
                                    padding: 6px;
        """)    
        self.play_black.setGeometry(QtCore.QRect(270, 50, 80, 80))
        self.play_black.clicked.connect(lambda : self.BotSettingsWidget_command_black())

        self.create_BotRatingSlider()


        self.widget.show() 
    
    def BotSettingsWidget_command_white(self):
        if GameMode.choosen_timeControl is None:
            setupUI.start_button.setEnabled(False)
            setupUI.start_button.setStyleSheet(""" background-color: rgb(131,145,145);
                                                    border-style: outset;
                                                    border-radius: 15px;
                                                    border-color: black;
                                                    color: rgb(252, 252, 252);
    box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19);                                                
                                                    padding: 4px;""")            
        else:
            setupUI.start_button.setEnabled(True)  
            setupUI.start_button.setStyleSheet(""" background-color: rgb(37, 217, 79);
                                                    border-style: outset;
                                                    border-radius: 15px;
                                                    border-color: black;
                                                    color: rgb(0,0,0);                                        
                                                    padding: 4px;""")               
        self.playingWhite = True 
        self.playingBlack = False 

        self.play_white.setIcon(QIcon("Checklist-White.png"))
        self.play_white.setIconSize(QtCore.QSize(50, 50))
        self.play_black.setIcon(QIcon(""))

        return self.playingWhite

    def BotSettingsWidget_command_black(self):
        if GameMode.choosen_timeControl is None:
            setupUI.start_button.setEnabled(False)
            setupUI.start_button.setStyleSheet(""" background-color: rgb(131,145,145);
                                                    border-style: outset;
                                                    border-radius: 15px;
                                                    border-color: black;
                                                    color: rgb(252, 252, 252);
    box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19);                                                
                                                    padding: 4px;""")     
        else:         
            setupUI.start_button.setEnabled(True)
            setupUI.start_button.setStyleSheet(""" background-color: rgb(37, 217, 79);
                                                    border-style: outset;
                                                    border-radius: 15px;
                                                    border-color: black;
                                                    color: rgb(0,0,0);                                        
                                                    padding: 4px;""")                 
        self.playingWhite = False 
        self.playingBlack = True

        self.play_white.setIcon(QIcon(""))
        self.play_black.setIcon(QIcon("Checklist-Black.png"))        
        self.play_black.setIconSize(QtCore.QSize(50, 50))

        return self.playingBlack

    def createLine(self, posx, posy, spanx, spany):
        self.line = QFrame(self.widget)
        self.line.setGeometry(QRect(posx,posy,spanx,spany));
        self.line.setFrameShape(QFrame.HLine);
        self.line.setFrameShadow(QFrame.Sunken);  
        self.line.setStyleSheet('border : 1px solid rgb(30, 31, 31);background-color:rgb(30, 31, 31);')        

    def create_BotRatingSlider(self): 
        self.rating_text = QLabel(self.widget) 

        self.createLine(102,150, 300, 3)
        self.createLine(102,300, 300, 3)        
        
        self.rating_slider = QtWidgets.QSlider(Qt.Horizontal,self.widget)
        self.rating_slider.setGeometry(QtCore.QRect(50, 200, 400, 80))
        self.rating_slider.setMinimum(200)
        self.rating_slider.setMaximum(3200)
        self.rating_slider.setSingleStep(10)
        self.rating_slider.setValue(200)
        self.rating_slider.setStyleSheet("""

                                        QSlider::groove:horizontal {
                                        border: 1px solid #bbb;
                                        background: #3a5e21;
                                        height: 10px;
                                        border-radius: 4px;
                                        }

                                        QSlider::sub-page:horizontal {
                                        background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
                                            stop: 0 #3a5e21, stop: 1 #3a5e21);
                                        background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
                                            stop: 0 #3a5e21, stop: 1 #3a5e21);
                                        border: 1px solid #777;
                                        height: 10px;
                                        border-radius: 4px;
                                        }

                                        QSlider::add-page:horizontal {
                                        background: #3a5e21;
                                        border: 1px solid #777;
                                        height: 10px;
                                        border-radius: 4px;
                                        }

                                        QSlider::handle:horizontal {
                                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #eee, stop:1 #ccc);
                                        border: 1px solid #777;
                                        width: 13px;
                                        margin-top: -2px;
                                        margin-bottom: -2px;
                                        border-radius: 4px;
                                        }

                                        QSlider::handle:horizontal:hover {
                                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #fff, stop:1 #ddd);
                                        border: 1px solid #444;
                                        border-radius: 4px;
                                        }

                                        QSlider::sub-page:horizontal:disabled {
                                        background: #3a5e21;
                                        border-color: #999;
                                        }

                                        QSlider::add-page:horizontal:disabled {
                                        background: #3a5e21;
                                        border-color: #999;
                                        }

                                        QSlider::handle:horizontal:disabled {
                                        background: #eee;
                                        border: 1px solid #aaa;
                                        border-radius: 4px;
                                        } 
        """)
        self.rating_slider.valueChanged.connect(lambda : self.change_sliderValue())

        self.rating_text.setFont(QtGui.QFont("Arial", 15))
        self.rating_text.setGeometry(QtCore.QRect(227, 160, 1000, 100))
        self.rating_text.setStyleSheet("color : #d1d1d1;")
        self.rating_text.setText(str(self.rating_slider.value()))

    def change_sliderValue(self): 
        if self.rating_slider.value() < 1000: 
            self.rating_text.setGeometry(QtCore.QRect(227, 160, 1000, 100))
        else:
            self.rating_text.setGeometry(QtCore.QRect(217, 160, 1000, 100))            
        self.rating_text.setText(str(self.rating_slider.value()))



        
class GameMode:
    button_list = []
    choosen_timeControl = None
    time_increment = 0
    def __init__(self, mode, time_control, posx, posy, spanx, spany, increment=0): 
        self.mode = mode 
        self.time_control = time_control 
        self.posx = posx 
        self.posy = posy
        self.spanx = spanx 
        self.spany = spany 
        self.isClicked = False
        self.increment = increment

    def createButton(self): 
        self.button = QPushButton(setupUI.main_centralWidget) 
        self.button.setEnabled(True)        
        self.button.setGeometry(QtCore.QRect(self.posx, self.posy, self.spanx, self.spany)) 
        self.button.setFont(QtGui.QFont("League Gothic", 20))
        if self.time_control < 60:
            self.button.setText(f"{str(self.time_control)} secs")
        else:
            self.button.setText(f"{str(round(self.time_control / 60))} min")
        self.button.setStyleSheet(""" background-color: rgb(41,41,41);
                                                border-style: outset;
                                                border-width: 2px;
                                                border-radius: 15px;
                                                border-color: black;
                                                color: rgb(252, 252, 252);                                                
                                                padding: 4px;""")        
        if self.increment != 0: 
            self.button.setText(f"{str(round(self.time_control/60))}|{self.increment}") 
        self.button.clicked.connect(lambda : self.button_command())
        self.button.show()        

        GameMode.button_list.append(self)

    def button_command(self):  
        if not (setupUI.playComputer.isClicked and (not setupUI.playComputer.playingWhite or not setupUI.playComputer.playingBlack)):
            self.isClicked = True
            setupUI.start_button.setEnabled(True)
            setupUI.start_button.setStyleSheet(""" background-color: rgb(37, 217, 79);
                                                    border-style: outset;
                                                    border-radius: 15px;
                                                    border-color: black;
                                                    color: rgb(0,0,0);                                        
                                                    padding: 4px;""")         
            GameMode.choosen_timeControl = self.time_control
            self.button.setStyleSheet(""" background-color: rgb(16,163,11);
                                                    border-style: outset;
                                                    border-width: 2px;
                                                    border-radius: 15px;
                                                    border-color: black;
                                                    color: rgb(252, 252, 252);
                                                    padding: 4px;""")  

            for btn in GameMode.button_list: 
                if not btn == self: 
                    btn.button.setStyleSheet(""" background-color: rgb(41,41,41);
                                                            border-style: outset;
                                                            border-width: 2px;
                                                            border-radius: 15px;
                                                            border-color: black;
                                                            color: rgb(252, 252, 252);
                                                            padding: 4px;""") 
                    btn.isClicked = False  
           



        

