
from io import UnsupportedOperation
from multiprocessing.dummy.connection import families
from os import devnull, putenv, write
from plistlib import UID
from re import A
from xml.etree.ElementTree import PI
from PyQt5 import QtCore, QtGui, QtWidgets   
from PyQt5.QtGui import QFocusEvent, QIcon, QPainter, QPalette, QPen, QBrush, QColor, QPixmap 
from PyQt5.QtCore import PYQT_VERSION, QRect, QSize, Qt, forcepoint
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QLabel, QMainWindow, QPushButton, QWidget
from PyQt5.sip import delete
from pynput import mouse
import os
import string 
import itertools
import functools
import time
import chess
import sys
import subprocess
import random

import control
import playStockfish



global enpassant_square
global checkmate_verificator 
global prev_movement
global after_movement
file = list(string.ascii_lowercase)[0:8] 
rank = list(range(1,9)) 
rank_y = rank 
enpassant_square = []
prev_movement = None 
after_movement = None




 
# file, rank, file ( in number ) - example d, 3 , 4 -> natural convention = 4 3

board_coordinates = []
for i in rank:
    board_2 = list(map(lambda x, y :[y, i, x], rank_y, file)) 
    board_coordinates += board_2 

    
class Ui_MainWindow(QMainWindow): 
    # Setting Up Dashboard UI

    boardSquare_list = []

    def __init__(self):
        super(QMainWindow, self).__init__() 
        
        global main_centralWidget

        self._centralwidget = QWidget() 
        main_centralWidget = self._centralwidget 
        self.setCentralWidget(self._centralwidget)
        self.setGeometry(0,0, 1920, 1080)  
        self.label = QtWidgets.QLabel(self._centralwidget)
        self.label.setGeometry(QtCore.QRect(0, -40, 1931, 1061)) 
        font = QtGui.QFont()
        font.setItalic(False) 
        self.label.setFont(font)
        self.label.setAutoFillBackground(False)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("bckgroundchess.png"))

        self.creatorName = QtWidgets.QLabel(self._centralwidget) 
        self.creatorName.setFont(QtGui.QFont("Niagara Engraved", 10)) 
        self.creatorName.setText("Created by : Farrel Dinarta")  
        self.creatorName.setGeometry(QtCore.QRect(910, 865, 200, 200))  
    
        self.pushButton = QtWidgets.QPushButton(self._centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(720, 790, 481, 141))
        self.pushButton.setStyleSheet("""
        QPushButton { background-color: grey; }
        QPushButton:focusressed { background-color: black; }
        QPushButton:focus { background-color: rgb(168, 168, 168); }        
        """)
        font = QtGui.QFont()
        font.setFamily("Niagara Engraved")
        font.setPointSize(40)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setIconSize(QtCore.QSize(60, 60))
        self.pushButton.clicked.connect(lambda : self.gameSettingsRoom())  
    
        self.retranslateUi_dashboard() 
    
    # Additional Dashboard UI Settings

    def retranslateUi_dashboard(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MyChess"))
        self.pushButton.setText(_translate("MainWindow", "PLAY"))  

    released = QtCore.pyqtSignal(int, int)

    def window_mouseclick_detection(window):
        window._listener = mouse.Listener(on_click=window._handle_click) 
        window._listener.start()

    def _handle_click(x, y, button, pressed, win):  
        for players in Player.player_list:
            if players.isMyTurn: 
                for pc in Pieces.pieces:
                    if pc.strcolor == players.color:
                        pc.isMoving = True 
                        for sqr2 in Ui_MainWindow.boardSquare_list:
                            if [sqr2.coordinate[2], sqr2.coordinate[1]] == prev_movement: 
                                continue                            
                            if sqr2.isOccupied and sqr2.piece_color == pc.strcolor:
                                sqr2.squares.setStyleSheet(sqr2.info_padding)
                    else:
                        pc.isMoving = False
                break   

        for sqr in Ui_MainWindow.boardSquare_list:
            if [sqr.coordinate[2], sqr.coordinate[1]] == prev_movement: 
                continue
            if not sqr.isOccupied:
                sqr.squares.setStyleSheet(sqr.info_padding) 
                sqr.squares.setIcon(QIcon("")) 

            for plyr in Player.player_list: 
                if plyr.isMyTurn:
                    if sqr.isOccupied and plyr.color != sqr.piece_color and sqr.isClicked:
                        sqr.squares.setEnabled(False) 

    # Start Game 
    color_dark = "(81, 150, 62)"
    color_light = "(200, 224, 206)"  

    def gameSettingsRoom(self): 
        global start_button
        self.label.deleteLater() 
        self.creatorName.deleteLater() 
        self.pushButton.deleteLater()     

        self.setting_background = QtWidgets.QLabel(self._centralwidget) 
        self.setting_background.setPixmap(QtGui.QPixmap('Background_GameSettings.png')) 

        self.startGame_button = QPushButton(self._centralwidget)  
        self.startGame_button.clicked.connect(lambda : self.startGame())
        self.startGame_button.setGeometry(QtCore.QRect(1320, 845, 531, 141)) 
        self.startGame_button.setFont(QtGui.QFont("League Gothic", 30))
        self.startGame_button.setText("START GAME")
        self.startGame_button.setEnabled(False)
        start_button = self.startGame_button
        self.startGame_button.setStyleSheet(""" background-color: rgb(131,145,145);
                                                border-style: outset;
                                                border-radius: 15px;
                                                border-color: black;
                                                color: rgb(252, 252, 252);
box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19);                                                
                                                padding: 4px;""")        
        self.startGame_button.show()  

        # Creating Stockfish Control Room 

        global playComputer

        # Creating Time Control Buttons 

        rapid_10 = control.GameMode("Rapid", 600, 80, 240, 250, 100)  
        rapid_10.createButton()

        rapid_15 = control.GameMode("Rapid", 900, 350, 240, 250, 100)  
        rapid_15.createButton()

        rapid_30 = control.GameMode("Rapid", 1800, 620, 240, 250, 100)  
        rapid_30.createButton() 

        blitz_3 = control.GameMode("Blitz", 180, 80, 435, 250, 100)  
        blitz_3.createButton()  

        blitz_5 = control.GameMode("Blitz", 300, 350, 435, 250, 100)  
        blitz_5.createButton()   

        blitz_3_2 = control.GameMode("Blitz", 180, 620, 435, 250, 100, 2)  
        blitz_3_2.createButton()  

        blitz_5_5 = control.GameMode("Blitz", 300, 890, 435, 250, 100, 5)  
        blitz_5_5.createButton()             

        bullet_1 = control.GameMode("Bullet", 60, 80, 630, 250, 100)  
        bullet_1.createButton()   

        bullet_2 = control.GameMode("Bullet", 120, 350, 630, 250, 100)  
        bullet_2.createButton()

        bullet_1_1 = control.GameMode("Bullet", 60, 620, 630, 250, 100, 1)  
        bullet_1_1.createButton()    

        bullet_2_1 = control.GameMode("Bullet", 120, 890, 630, 250, 100, 1)  
        bullet_2_1.createButton()                          

        hyper_bullet_15 = control.GameMode("Hyper Bullet", 15, 80, 825, 250, 100)  
        hyper_bullet_15.createButton()        

        hyper_bullet_30 = control.GameMode("Hyper Bullet", 30, 350, 825, 250, 100)  
        hyper_bullet_30.createButton()  

        self.setting_background.show()   

        playComputer = control.stockfish_controlRoom(1199,240, 101, 101)  
        playComputer.create_choosePlayBot()               

    def startGame(self): 
        ############################### 
    
        global a_file 
        global boardBorder 
        global BoardInfo
        global player1_frame, player2_frame, player1_name,player2_name,color_isMyTurn, color_isNotMyTurn, name_color_isMyTurn, name_color_isNotMyTurn

        self.setting_background.deleteLater() 
        self.startGame_button.deleteLater()   

        self.gameBackground = QtWidgets.QLabel(self._centralwidget)
        self.gameBackground.setText("") 
        self.gameBackground.setPixmap(QtGui.QPixmap('WoodenBackground.png'))
        self.gameBackground.show()  

        boardBorder = QFrame(self._centralwidget)
        boardBorder.setFrameShape(QFrame.StyledPanel)
        boardBorder.setLineWidth(100) 
        boardBorder.resize(850,850)
        boardBorder.move(525, 75)
        boardBorder.show()   

        self.border = QtWidgets.QLabel(boardBorder) 
        self.border.setText("")
        self.border.setPixmap(QPixmap('Board Border.png')) 
        self.border.resize(850, 850)
        self.border.show()
        
        boardFrame = QFrame(self._centralwidget) 
        boardFrame.setFrameShape(QFrame.StyledPanel) 
        boardFrame.setLineWidth(80) 
        boardFrame.resize(800, 800) 
        boardFrame.move(550, 100)
        boardFrame.show() 

        color_isMyTurn = '#876316'
        color_isNotMyTurn = '#45381b' 
        name_color_isMyTurn = 'white'
        name_color_isNotMyTurn = 'grey'


        player2_frame = QFrame(self._centralwidget)  
        player2_frame.setGeometry(QRect(405, 75, 120, 120))
        player2_frame.show() 

        player2_name = QtWidgets.QLabel(self._centralwidget)  
        player2_name.setGeometry(QRect(425, 200, 140, 40))  
        player2_name.setFont(QtGui.QFont("Niagara Engraved", 25))
        player2_name.show()


        player1_frame = QFrame(self._centralwidget) 
        player1_frame.setGeometry(QRect(405, 805, 120, 120))
        player1_frame.show()   

        player1_name = QtWidgets.QLabel(self._centralwidget) 
        player1_name.setGeometry(QRect(425, 755, 140, 40))  
        player1_name.setFont(QtGui.QFont("Niagara Engraved", 25))
        player1_name.show()

        v = 700
        count_startDark = 0 
        count_startLight = 0  
        sqr_coordinate_counter = 0
        rank_ctr = 1
        for verti in range(8):
            h = 0
            if verti % 2 == 0:
                for hori in range(8):
                    if count_startDark % 2 == 0:
                        if hori == 0:
                            board = Board(Ui_MainWindow.color_dark, h, v, 100, 100, boardFrame, board_coordinates[sqr_coordinate_counter],f"background-color: rgb{Ui_MainWindow.color_dark};border: none;color: rgb{Ui_MainWindow.color_light};" ,f"{str(rank_ctr)}")  
                            board.piece_color = None
                            rank_ctr += 1
                            Ui_MainWindow.boardSquare_list.append(board)
                        else: 
                            board = Board(Ui_MainWindow.color_dark, h, v, 100, 100, boardFrame, board_coordinates[sqr_coordinate_counter],f"background-color: rgb{Ui_MainWindow.color_dark};border: none;color: rgb{Ui_MainWindow.color_light};") 
                            board.piece_color = None
                            Ui_MainWindow.boardSquare_list.append(board) 
                    else:
                        board = Board(Ui_MainWindow.color_light, h, v, 100, 100, boardFrame, board_coordinates[sqr_coordinate_counter],f"background-color: rgb{Ui_MainWindow.color_light};border: none;color: rgb{Ui_MainWindow.color_dark};")  
                        board.piece_color = None
                        Ui_MainWindow.boardSquare_list.append(board) 
                    sqr_coordinate_counter += 1 
                    count_startDark += 1
                    h += 100  
                count_startDark = 0 
            else: 
                for hori in range(8):
                    if count_startLight % 2 != 0:
                        board = Board(Ui_MainWindow.color_dark, h, v, 100, 100, boardFrame, board_coordinates[sqr_coordinate_counter],f"background-color: rgb{Ui_MainWindow.color_dark};border: none;color: rgb{Ui_MainWindow.color_light};") 
                        board.piece_color = None
                        Ui_MainWindow.boardSquare_list.append(board)  
                    else:
                        if hori == 0: 
                            board = Board(Ui_MainWindow.color_light, h, v, 100, 100, boardFrame, board_coordinates[sqr_coordinate_counter] ,f"background-color: rgb{Ui_MainWindow.color_light};border: none;color: rgb{Ui_MainWindow.color_dark};",str(rank_ctr))  
                            board.piece_color = None
                            rank_ctr += 1
                            Ui_MainWindow.boardSquare_list.append(board)  
                        else:
                            board = Board(Ui_MainWindow.color_light, h, v, 100, 100, boardFrame, board_coordinates[sqr_coordinate_counter] ,f"background-color: rgb{Ui_MainWindow.color_light};border: none;color: rgb{Ui_MainWindow.color_dark};")
                            board.piece_color = None
                            Ui_MainWindow.boardSquare_list.append(board) 
                    sqr_coordinate_counter += 1                         
                    count_startLight += 1
                    h += 100  
                count_startLight = 0 
            v -= 100   


        # Square Indexing Class

        class BoardInfo:
            posx = 84 
            posy = 781 
            board_info_list = []
            def __init__(self, text, coloring):
                self.text = text  
                self.coloring = coloring
                self.labeling = QtWidgets.QLabel(boardFrame) 
                self.labeling.move(BoardInfo.posx, BoardInfo.posy) 
                self.labeling.setText(self.text) 
                self.labeling.setStyleSheet(self.coloring) 
                self.labeling.show()  

        # Create Square Indexing

        for sqr in range(0, 8):
            if sqr % 2 == 0:
                board_info = BoardInfo(list(string.ascii_lowercase)[sqr], f"color:rgb{Ui_MainWindow.color_light};")   
            else: 
                 board_info = BoardInfo(list(string.ascii_lowercase)[sqr], f"color:rgb{Ui_MainWindow.color_dark};")  
            BoardInfo.board_info_list.append(board_info) 
            BoardInfo.posx += 100              

        BoardInfo.posx = 5 
        BoardInfo.posy = 705

        for sqr in range(1, 9): 
            if sqr % 2 == 0:
                board_info = BoardInfo(str(sqr), f"color:rgb{Ui_MainWindow.color_dark};")   
            else: 
                 board_info = BoardInfo(str(sqr), f"color:rgb{Ui_MainWindow.color_light};")  
            BoardInfo.board_info_list.append(board_info) 
            BoardInfo.posy -= 100

  
        # Game Mode 
        GamePack.classic_game()
        # Create Players
        global White_Player 
        global Black_Player

        if playComputer.isClicked:
            if playComputer.playingWhite:
                White_Player = Player('White')
                Black_Player = Player('Black', True)
            else:
                White_Player = Player('White', True)
                Black_Player = Player('Black') 

                first_move_list = [
                    [['e', 2], ['e',4]],
                    [['d', 2], ['d',4]],         
                    [['c', 2], ['c',4]], 
                    [['f', 2], ['f',4]],
                    [['e', 2], ['e',3]],   
                    [['d', 2], ['d',3]],
                    [['c', 2], ['c',3]], 
                    [['f', 2], ['f',3]], 
                    [['b', 1], ['c', 3]],
                    [['g', 1], ['f', 3]]                                                                                                             
                ]

                bot_chooseFirstMove = random.choice(first_move_list)

                for sqr in Ui_MainWindow.boardSquare_list:
                    if [sqr.coordinate[0], sqr.coordinate[1]] == bot_chooseFirstMove[0]: 
                        for pc in Pieces.pieces:
                            if pc.strcolor == sqr.piece_color: 
                                pc.isMoving = True 
                            else: 
                                pc.isMoving = False
                        sqr.squareClicked()                          
                
                for sqr in Ui_MainWindow.boardSquare_list:
                    if [sqr.coordinate[0], sqr.coordinate[1]] == bot_chooseFirstMove[1]: 
                        for pc in Pieces.pieces:
                            if pc.strcolor == sqr.piece_color: 
                                pc.isMoving = True 
                            else: 
                                pc.isMoving = False             
                        sqr.squareClicked()                 

        else:
            White_Player = Player('White')
            Black_Player = Player('Black')               


        for plyr in Player.player_list: 
            if plyr.isMyTurn: 
                player1_name.setText(plyr.name)  
            else: 
                player2_name.setText(plyr.name)

        Player.launch_turn() 
        Ui_MainWindow.window_mouseclick_detection(self)  


    
# Board Systemation 

class GamePack:
    bot_allowMovement = False    
    

    def classic_game(): 

        temp_pieceholder = []
        # WHITE POINT OF VIEW
        pw1 = Pawn(Qt.white, "White", "Pawn", 2,  'a')
        pw2 = Pawn(Qt.white, "White", "Pawn", 2,  'b')
        pw3 = Pawn(Qt.white, "White", "Pawn", 2,  'c')
        pw4 = Pawn(Qt.white, "White", "Pawn", 2,  'd')
        pw5 = Pawn(Qt.white, "White", "Pawn", 2,  'e')
        pw6 = Pawn(Qt.white, "White", "Pawn", 2,  'f')
        pw7 = Pawn(Qt.white, "White", "Pawn", 2,  'g')
        pw8 = Pawn(Qt.white, "White", "Pawn", 2,  'h')        

        w_rook_1 = Rook(Qt.white, "White", "Rook", 1, 'a')
        w_rook_2 = Rook(Qt.white, "White", "Rook", 1, 'h')
        w_bishop_1 = Bishop(Qt.white, "White", "Bishop", 1, 'c')
        w_bishop_2 =  Bishop(Qt.white, "White", "Bishop", 1, 'f') 
        w_knight_1 = Knight(Qt.white, "White", "Knight", 1, 'b')
        w_knight_2 = Knight(Qt.white, "White", "Knight", 1, 'g')
        w_queen = Queen(Qt.white, "White", "Queen", 1, "d")
        w_king =  King(Qt.white, "White", "King", 1, 'e')          

        temp_pieceholder.append(pw1)        
        temp_pieceholder.append(pw2)        
        temp_pieceholder.append(pw3)       
        temp_pieceholder.append(pw4)          
        temp_pieceholder.append(pw5)         
        temp_pieceholder.append(pw6)         
        temp_pieceholder.append(pw7)         
        temp_pieceholder.append(pw8) 

        temp_pieceholder.append(w_rook_1)         
        temp_pieceholder.append(w_rook_2)         
        temp_pieceholder.append(w_bishop_1)
        temp_pieceholder.append(w_bishop_2)     
        temp_pieceholder.append(w_knight_1)         
        temp_pieceholder.append(w_knight_2)         
        temp_pieceholder.append(w_queen)         
        temp_pieceholder.append(w_king)         



        ########################

        pb1 = Pawn(Qt.black, "Black", "Pawn", 7, 'a')
        pb2 = Pawn(Qt.black, "Black", "Pawn", 7, 'b')
        pb3 = Pawn(Qt.black, "Black", "Pawn", 7, 'c')
        pb4 = Pawn(Qt.black, "Black", "Pawn", 7, 'd')
        pb5 = Pawn(Qt.black, "Black", "Pawn", 7, 'e')
        pb6 = Pawn(Qt.black, "Black", "Pawn", 7, 'f')
        pb7 = Pawn(Qt.black, "Black", "Pawn", 7, 'g')
        pb8 = Pawn(Qt.black, "Black", "Pawn", 7, 'h')

        b_rook_1 = Rook(Qt.black, "Black", "Rook", 8, 'a')
        b_rook_2 = Rook(Qt.black, "Black", "Rook", 8, 'h')
        b_bishop_1 = Bishop(Qt.black, "Black", "Bishop", 8, 'c')
        b_bishop_2 =  Bishop(Qt.black, "Black", "Bishop", 8, 'f') 
        b_knight_1 = Knight(Qt.black, "Black", "Knight", 8, 'b')
        b_knight_2 = Knight(Qt.black, "Black", "Knight", 8, 'g')
        b_queen = Queen(Qt.black, "Black", "Queen", 8, "d")
        b_king =  King(Qt.black, "Black", "King", 8, 'e')   

        temp_pieceholder.append(pb1)        
        temp_pieceholder.append(pb2)        
        temp_pieceholder.append(pb3)       
        temp_pieceholder.append(pb4)          
        temp_pieceholder.append(pb5)         
        temp_pieceholder.append(pb6)         
        temp_pieceholder.append(pb7)         
        temp_pieceholder.append(pb8) 

        temp_pieceholder.append(b_rook_1)         
        temp_pieceholder.append(b_rook_2)         
        temp_pieceholder.append(b_bishop_1)
        temp_pieceholder.append(b_bishop_2)     
        temp_pieceholder.append(b_knight_1)         
        temp_pieceholder.append(b_knight_2)         
        temp_pieceholder.append(b_queen)         
        temp_pieceholder.append(b_king)  
      

        for pc in temp_pieceholder:
            for sqr in Ui_MainWindow.boardSquare_list: 
                if sqr.coordinate[0] == pc.file and sqr.coordinate[1] == pc.rank: 
                    sqr.squares.setIcon(pc.image)  
                    sqr.squares.setIconSize(QSize(80,80))
                    sqr.isOccupied = True             



    def test_stalemate(): 
        white_king = King(Qt.white, "White", "King", 8, "a")         
        black_king = King(Qt.black, "Black", "King", 1, "a") 
        black_queen = Queen(Qt.white, "White", "Queen", 4, "c")   

        
        for sqr in Ui_MainWindow.boardSquare_list: 
            if sqr.coordinate[0] == black_king.file and sqr.coordinate[1] == black_king.rank: 
                sqr.squares.setIcon(black_king.image)  
                sqr.squares.setIconSize(QSize(80,80))
                sqr.isOccupied = True        

        for sqr in Ui_MainWindow.boardSquare_list: 
            if sqr.coordinate[0] == white_king.file and sqr.coordinate[1] == white_king.rank: 
                sqr.squares.setIcon(white_king.image)  
                sqr.squares.setIconSize(QSize(80,80))
                sqr.isOccupied = True

        for sqr in Ui_MainWindow.boardSquare_list: 
            if sqr.coordinate[0] == black_queen.file and sqr.coordinate[1] == black_queen.rank: 
                sqr.squares.setIcon(black_queen.image)  
                sqr.squares.setIconSize(QSize(80,80))
                sqr.isOccupied = True                

    def test_1(): 
        # TESTING AND DEBUGGING SET 1
        global lol
        white_king = Queen(Qt.black, "Black", "Queen", 1, "a")  
        white_knig = Bishop(Qt.black, "Black", "Bishop", 6, "d")  
        white_knigs = Pawn(Qt.white, "White", "Pawn", 6, "g")  
        rook = Queen(Qt.white, "White", "Queen", 1, "b") 
        pawn = King(Qt.black, "Black", "King", 6, 'c') 
        pawn2 = Pawn(Qt.white, "White", "Pawn", 4, 'd') 
        king2 = King(Qt.white, "White", "King", 2, 'c') 
        prook = Rook(Qt.white, "White", "Rook", 5, 'h')
        lol = Knight(Qt.black, "Black", "Knight", 3, 'f') 

        temp_pieceholder = []        
        temp_pieceholder.append(white_king)
        temp_pieceholder.append(white_knig)
        temp_pieceholder.append(white_knigs)        
        temp_pieceholder.append(rook) 
        temp_pieceholder.append(pawn)                
        temp_pieceholder.append(pawn2)    
        temp_pieceholder.append(king2)
        temp_pieceholder.append(prook)        
        temp_pieceholder.append(lol)        

        for pc in temp_pieceholder: 

            for sqr in Ui_MainWindow.boardSquare_list: 
                if sqr.coordinate[0] == pc.file and sqr.coordinate[1] == pc.rank: 
                    sqr.squares.setIcon(pc.image)  
                    sqr.squares.setIconSize(QSize(80,80))
                    sqr.isOccupied = True            

    def test_promotion(): 
        temp_piece_holder = [Pawn(Qt.white, "White", "Pawn", 7, "g"),
        Pawn(Qt.white, "White", "Pawn", 6, "f"), 
        King(Qt.black, "Black", "King", 5, "c"), 
        King(Qt.white, "White", "King", 4, "f"), 
        Pawn(Qt.black, "Black", "Pawn", 2, 'c'), 
        Pawn(Qt.black, "Black", "Pawn", 2, 'h')]    

        for pieces in temp_piece_holder: 
            for sqr in Ui_MainWindow.boardSquare_list: 
                if sqr.coordinate[0] == pieces.file and sqr.coordinate[1] == pieces.rank: 
                    sqr.squares.setIcon(pieces.image)  
                    sqr.squares.setIconSize(QSize(80,80))
                    sqr.isOccupied = True
                    break 


class Board(Ui_MainWindow):  
    pgn_string = '' 
    move_number = 0 
    move_num_changer = 0    
    enable_pgn_writeCheck = 0
    enable_findBotMovement = True
    push_botMovement = False

    def __init__(self, color, posx, posy, size_x, size_y, frame, coordinate, info_padding, info=''):
        self.color = color 
        self.posx = posx
        self.posy = posy
        self.size_x = size_x
        self.size_y = size_y 
        self.coordinate = coordinate
        self.info_padding = info_padding
        self.info = info
        self.isOccupied = False  
        self.isClicked = False

        self.squares = QtWidgets.QPushButton(frame)
        self.squares.setText("")
        self.squares.setStyleSheet(info_padding) 
        self.squares.setGeometry(QRect(self.posx, self.posy, self.size_x, self.size_y)) 
        self.squares.clicked.connect(lambda : self.squareClicked(False)) 
        self.squares.show()   

    attacker = None 
    prev = None
    first_move = True
    first_move_bugKiller = 0


    def squareClicked(self, isBot=False):
        next_sequence = True
        global prev_movement
        global after_movement
        global switch_clock
        switch_clock = False
        print("I just clicked : ", [self.coordinate[2], self.coordinate[1]])
        global enpassant_square
        global king_temp  

        
        # king_temp = None

        isClicked_color = "(188, 191, 107)"   
        

        if Board.attacker is not None: 
            if  [self.coordinate[2], self.coordinate[1]] in Board.attacker.area_covered: 
                prev_movement = Board.attacker.position_numeric
                after_movement = [self.coordinate[2], self.coordinate[1]]                           
                next_sequence = True
                if isBot:
                    playStockfish.BOT_Stockfish.disable_clockSwitch += 1
                # Part of Stockfish adaptation
                try: 
                    if not Board.push_botMovement: 
                        Board.push_botMovement = True 
                except: 
                    pass

                # PGN Writer
                Board.enable_pgn_writeCheck += 1
                Board.move_num_changer += 1 
                if Board.move_num_changer % 2 != 0: 
                    Board.move_number += 1 
                    Board.pgn_string += f"{str(Board.move_number)}. " 
                if not self.isOccupied:
                    if Board.attacker.ptype == "Pawn": 
                        if Board.attacker.position_numeric[0] != self.coordinate[2]:
                            Board.pgn_string += f"{list(string.ascii_lowercase)[Board.attacker.position_numeric[0]-1]}x{self.coordinate[0]}{self.coordinate[1]} e.p. "                            
                        else:
                            Board.pgn_string += f"{self.coordinate[0]}{self.coordinate[1]} "
                    elif Board.attacker.ptype == "Knight": 
                        Board.pgn_string += f"N{self.coordinate[0]}{self.coordinate[1]} "
                    else:
                        if Board.attacker.ptype == "King": 
                            if self.coordinate[2]-Board.attacker.position_numeric[0] == 2: 
                                Board.pgn_string += "O-O " 
                            elif self.coordinate[2]-Board.attacker.position_numeric[0] == -2: 
                                Board.pgn_string += "O-O-O "
                            else:
                                Board.pgn_string += f"{Board.attacker.ptype[0]}{self.coordinate[0]}{self.coordinate[1]} "                                 
                        else:
                            Board.pgn_string += f"{Board.attacker.ptype[0]}{self.coordinate[0]}{self.coordinate[1]} " 
                else: 
                    if Board.attacker.ptype == "Pawn": 
                        Board.pgn_string += f"{list(string.ascii_lowercase)[Board.attacker.position_numeric[0]-1]}x{self.coordinate[0]}{self.coordinate[1]} "
                    elif Board.attacker.ptype == "Knight": 
                        Board.pgn_string += f"Nx{self.coordinate[0]}{self.coordinate[1]} "
                    else:
                        Board.pgn_string += f"{Board.attacker.ptype[0]}x{self.coordinate[0]}{self.coordinate[1]} "                                        
                for plyr in Player.player_list:
                    if plyr.isMyTurn: 
                        for kg in Pieces.pieces:
                            if kg.strcolor == plyr.color and kg.ptype == "King": 
                                king_temp = kg

                # for pc in Pieces.pieces: 
                #     pc.areaCovered()   

                switch_clock = True                     

                try:
                    if self.piece_color != Board.attacker.strcolor and self.isOccupied:
                        for victim in Pieces.pieces: 
                            if victim.position_numeric == [self.coordinate[2], self.coordinate[1]]:
                                if victim.strcolor == 'Black':
                                    for victim_black in Pieces.black_pieces:
                                        if victim_black == victim: 
                                            Pieces.black_pieces.remove(victim_black)
                                            del victim_black
                                            break
                                else: 
                                    for victim_white in Pieces.white_pieces:
                                        if victim_white == victim:
                                            Pieces.white_pieces.remove(victim_white)
                                            del victim_white 
                                            break 
                                Pieces.pieces.remove(victim)
                                del victim 
                                break 
                    else:
                        if Board.attacker.ptype == "Pawn": 
                            for pc in Pieces.pieces:
                                if pc == Board.attacker:  
                                    pc.en_passantable += 1 
                except:
                    pass 

                for check_occupy in Ui_MainWindow.boardSquare_list:
                    if [check_occupy.coordinate[2], check_occupy.coordinate[1]] == Board.attacker.position_numeric and check_occupy.isOccupied:
                        check_occupy.isOccupied = False
                self.isOccupied = True 
                for pc in Pieces.pieces:
                    if pc == Board.attacker: 
                        for sqr in Ui_MainWindow.boardSquare_list:
                            if [sqr.coordinate[2], sqr.coordinate[1]] == pc.position_numeric:
                                sqr.squares.setIcon(QIcon(""))   
                            if not sqr.isOccupied:
                                sqr.squares.setIcon(QIcon(""))    
                if [self.coordinate[2], self.coordinate[1]] in Board.attacker.area_covered: 
                    for pc in Pieces.pieces:
                        if pc == Board.attacker and not (pc.position_numeric == prev_movement):
                            self.squares.setIcon(QIcon("")) 
                            # self.squares.setStyleSheet(sqr.info_padding)        

                self.squares.setIcon(Board.attacker.image) 
                self.squares.setIconSize(QSize(80,80))   
                for pc_moved in Pieces.pieces:
                    if pc_moved == Board.attacker: 
                        if pc_moved.ptype == 'Pawn':
                            pc_moved.firstmove = False 
                            try:
                                if pc_moved.strcolor == 'White':
                                    pc_moved.area_covered.remove([pc_moved.position_numeric[0], pc_moved.position_numeric[1]+2])
                                else:
                                    pc_moved.area_covered.remove([pc_moved.position_numeric[0], pc_moved.position_numeric[1]-2])            
                            except:
                                pass
                        if pc_moved.ptype == "King" or pc_moved.ptype == "Rook": 
                            prev_king_sqr = pc_moved.position_numeric[0]
                            pc_moved.firstMove = True 
                        pc_moved.position_numeric = [self.coordinate[2], self.coordinate[1]]   

                        # Logic to Implement Castling
                        if pc_moved.ptype == "King": 
                            if abs(pc_moved.position_numeric[0] - prev_king_sqr) == 2: 
                                for rook in Pieces.pieces:
                                    if rook.ptype == "Rook" and rook.strcolor == pc_moved.strcolor and abs(pc_moved.position_numeric[0] - rook.position_numeric[0]) == 1: 
                                        pass
                                        prev_rook_pos = rook.position_numeric
                                        rook.position_numeric = [rook.position_numeric[0]-2, rook.position_numeric[1]] 
                                        rook.position_convention = [list(string.ascii_lowercase)[rook.position_numeric[0]-1], rook.position_numeric[1]] 
                                        rook.isMoving = False 
                                        rook.rank = rook.position_numeric[1]
                                        rook.file = rook.position_numeric[0] 
                                        for sqr in Ui_MainWindow.boardSquare_list:
                                            if [sqr.coordinate[2], sqr.coordinate[1]] == rook.position_numeric: 
                                                sqr.isOccupied = True 
                                                sqr.piece_color = rook.strcolor 
                                                sqr.squares.setIcon(rook.image) 
                                                sqr.squares.setIconSize(QSize(80, 80)) 
                                            if [sqr.coordinate[2], sqr.coordinate[1]] == prev_rook_pos: 
                                                sqr.isOccupied = False 
                                                sqr.piece_color = None 
                                                sqr.squares.setIcon(QIcon(""))
                                    elif rook.ptype == "Rook" and rook.strcolor == pc_moved.strcolor and abs(pc_moved.position_numeric[0] - rook.position_numeric[0]) == 2: 
                                        pass 
                                        prev_rook_pos = rook.position_numeric
                                        rook.position_numeric = [rook.position_numeric[0]+3, rook.position_numeric[1]] 
                                        rook.position_convention = [list(string.ascii_lowercase)[rook.position_numeric[0]-1], rook.position_numeric[1]] 
                                        rook.isMoving = False 
                                        rook.rank = rook.position_numeric[1]
                                        rook.file = rook.position_numeric[0] 
                                        for sqr in Ui_MainWindow.boardSquare_list:
                                            if [sqr.coordinate[2], sqr.coordinate[1]] == rook.position_numeric: 
                                                sqr.isOccupied = True 
                                                sqr.piece_color = rook.strcolor 
                                                sqr.squares.setIcon(rook.image) 
                                                sqr.squares.setIconSize(QSize(80, 80)) 
                                            if [sqr.coordinate[2], sqr.coordinate[1]] == prev_rook_pos: 
                                                sqr.isOccupied = False 
                                                sqr.piece_color = None 
                                                sqr.squares.setIcon(QIcon(""))                                    

                        pc_moved.position_convention = [list(string.ascii_lowercase)[self.coordinate[2]-1], self.coordinate[1]] 
                        pc_moved.isMoving = False 
                        pc_moved.rank = self.coordinate[1] 
                        pc_moved.file = self.coordinate[2]  
                        self.piece_color = pc_moved.strcolor 
                    if pc_moved.strcolor == Board.attacker.strcolor:
                        pc_moved.isMoving = False  
                for plyr in Player.player_list:
                    if plyr.isMyTurn:
                        plyr.isMyTurn = False 
                    else:
                        plyr.isMyTurn = True  
                try:                               
                    if Board.attacker.position_numeric == enpassant_square and Board.attacker.ptype == "Pawn":
                        for enemy_pawn in Pieces.pieces:
                            if enemy_pawn.strcolor != Board.attacker.strcolor and enemy_pawn.ptype == "Pawn" and (enemy_pawn.position_numeric == [enpassant_square[0], enpassant_square[1]-1] or enemy_pawn.position_numeric == [enpassant_square[0], enpassant_square[1]+1]):
                                for sqr in Ui_MainWindow.boardSquare_list:
                                    if [sqr.coordinate[2], sqr.coordinate[1]] == enemy_pawn.position_numeric: 
                                        sqr.squares.setIcon(QIcon(""))
                                        sqr.piece_color = None 
                                        sqr.isOccupied = False
                                Pieces.pieces.remove(enemy_pawn)
                                del enemy_pawn
                except:
                    pass                         
                enpassant_square = []                
                
                # Part of En Passant Logic
                for pc in Pieces.pieces:
                    try: 
                        if pc.en_passantable == 1: 
                            pc.reject_enpassant += 1
                    except: 
                        pass        
            try:
                for sqr in Ui_MainWindow.boardSquare_list:
                    if sqr.isOccupied and sqr.piece_color != Board.attacker.strcolor:
                        sqr.squares.setEnabled(True)                         
            except:
                pass         
          
               

        Player.launch_turn()   

        for sqr in Ui_MainWindow.boardSquare_list:
            if sqr.isClicked:
                sqr.isClicked = False 
                for sq in Ui_MainWindow.boardSquare_list:
                    try:
                        if not sq.isClicked and not sq.isOccupied and not ([sq.coordinate[2], sq.coordinate[1]] == prev_movement):
                            sq.squares.setIcon(QIcon("")) 
                            # sq.squares.setStyleSheet(sq.info_padding)  
                            for player in Player.player_list:
                                if player.isMyTurn: 
                                    for sqr in Ui_MainWindow.boardSquare_list: 
                                        if sqr.isOccupied and sqr.piece_color != player.color:
                                            sqr.squares.setEnabled(False)                 
                    except:
                        pass

                    

        Board.prev = Board.attacker       

        Board.attacker = None 
           
        self.isClicked = True  
        
        ### COPY THIS FOR LATER

        for pc in Pieces.pieces:
            if pc.ptype == 'King': 
                continue 
            else:  
                try:
                    pc.second_checker = False
                    pc.areaCovered()  
                except AttributeError: 
                    pass
            pc.tester2 += 1       

        ####### 


        
        for kg in Pieces.pieces:
            if kg.ptype == 'King':  
                king_temp = kg 
                kg.areaCovered()
                if kg.inCheck():
                    for pc in Pieces.pieces:
                        if pc.ptype == "Queen" or pc.ptype == "Rook" or pc.ptype == "Bishop":
                            pc.second_checker = True 
                            pc.areaCovered() 
                else:
                    for pc in Pieces.pieces:
                        if pc.ptype == "Queen" or pc.ptype == "Rook" or pc.ptype == "Bishop":
                            pc.second_checker = False 

        
        # Pin System
        global king_clicked_mode
        global checkmate_verificator 
        global temp_def
        global test_sqr
        for sqr in Ui_MainWindow.boardSquare_list:
            # break 
            if sqr.isClicked:
                checkmate_verificator = False                 
                temp_def = None  
                test_sqr = sqr
                for plyr in Player.player_list:
                    if plyr.isMyTurn: 
                        turn_color = plyr.color
                for pc in Pieces.pieces:  
                        if pc.ptype == "King":  
                            king_clicked_mode = True # Switch to False to back to normal setting 
                            continue
                        else:
                            king_clicked_mode = False
                        if pc.position_numeric == [sqr.coordinate[2], sqr.coordinate[1]] and pc.strcolor == turn_color:

                            pc.allowMovement = 0 
                            current_pieces = pc  

                            for kings in Pieces.pieces:
                                if kings.ptype == "King" and current_pieces.strcolor == kings.strcolor:
                                    temp_king = kings
                                    break
                        

                            proto_ac = pc.area_covered
                            for area in proto_ac:                            
                                for sqr in Ui_MainWindow.boardSquare_list:
                                    if [sqr.coordinate[2], sqr.coordinate[1]] == pc.position_numeric: 
                                        sqr.isOccupied = False  
                                
                                for sqr in Ui_MainWindow.boardSquare_list: 
                                    if sqr.isOccupied and sqr.piece_color != pc.strcolor and [sqr.coordinate[2], sqr.coordinate[1]] == area: 
                                        sqr.isOccupied = True  
                                        for s in Pieces.pieces:
                                            if [sqr.coordinate[2], sqr.coordinate[1]] == s.position_numeric: 
                                                s.area_covered = [] 
                                                temp_def = s
                                    if [sqr.coordinate[2], sqr.coordinate[1]] == area and (not sqr.isOccupied):                                         
                                        sqr.isOccupied = True   
                                        sqr.piece_color = None

                                for x in Pieces.pieces:
                                    if x.ptype == 'King' or x == temp_def: 
                                        continue
                                    else: 
                                        if x == pc or x == temp_def:
                                            continue 
                                        try:  
                                            if x.strcolor == pc.strcolor: 
                                                continue
                                            x.second_checker = False
                                            x.areaCovered()  
                                        except: 
                                            pass
                                    x.tester2 += 1     

                                for kg in Pieces.pieces:
                                    if kg.ptype == 'King': 
                                        king_temp = kg 
                                        kg.areaCovered()
                                        if kg.inCheck():
                                            for a in Pieces.pieces: 
                                                if a == pc or a.strcolor == pc.strcolor or a == temp_def:
                                                    continue
                                                if a.ptype == "Queen" or a.ptype == "Rook" or a.ptype == "Bishop":
                                                    a.second_checker = True 
                                                    a.areaCovered() 
                                        else:
                                            for a in Pieces.pieces:
                                                if a == pc or a.strcolor == pc.strcolor or a == temp_def:
                                                    continue
                                                if a.ptype == "Queen" or a.ptype == "Rook" or a.ptype == "Bishop":
                                                    a.second_checker = False  

                                temp_area = area  
                                if temp_king.inCheck(): 
                                        new_ac = [a for a in pc.area_covered if not a == temp_area] 
                                        pc.area_covered = new_ac  
                                else: 
                                    pc.allowMovement += 1
                                    checkmate_verificator = True 
                                temp_def = None 

                                #######
                                for sqr in Ui_MainWindow.boardSquare_list: 
                                    try:
                                        if [sqr.coordinate[2], sqr.coordinate[1]] == temp_area and (sqr.piece_color is None):
                                            sqr.isOccupied = False                                               
                                    except:
                                        pass                     

                                for sqr in Ui_MainWindow.boardSquare_list:
                                    if [sqr.coordinate[2], sqr.coordinate[1]] == pc.position_numeric:  
                                        sqr.isOccupied = True   
                                enable_sqr = pc   

                            
                            for x in Pieces.pieces: 
                                if x.ptype == "King" or x == temp_def:
                                    continue
                                try: 
                                    if x.strcolor == enable_sqr.strcolor: 
                                        continue
                                    x.second_checker = False
                                    x.areaCovered()
                                except: 
                                    pass
                                x.tester2 += 1     


                            for kg in Pieces.pieces:
                                            if kg.ptype == 'King':  
                                                king_temp = kg 
                                                kg.areaCovered()  
                                                if kg.inCheck():
                                                    for a in Pieces.pieces:
                                                        try:
                                                            if a.strcolor == enable_sqr.strcolor or a == temp_def: 
                                                                continue 
                                                        except:
                                                            pass                     
                                                        if a.ptype == "Queen" or a.ptype == "Rook" or a.ptype == "Bishop":
                                                            a.second_checker = True
                                                            a.areaCovered()
                                                else: 
                                                    for a in Pieces.pieces:
                                                        try:
                                                            if a.strcolor == enable_sqr.strcolor or a == temp_def: 
                                                                continue                     
                                                        except:
                                                            pass
                                                        if a.ptype == "Queen" or a.ptype == "Rook" or a.ptype == "Bishop":
                                                            a.second_checker = False       
                                                            # a.areaCovered() 
                        else:
                            pc.allowMovement = 0                                      
                                                                                    
        temp_def = None    

        # Part of piece protecting each other in case of King is clicked.
        for sqr in Ui_MainWindow.boardSquare_list: 
            if sqr.isClicked:   
                for pc in Pieces.pieces: 
                    if [sqr.coordinate[2], sqr.coordinate[1]] == pc.position_numeric: 
                        for area in pc.area_covered: 
                            for king_area in Ui_MainWindow.boardSquare_list:
                                if [king_area.coordinate[2], king_area.coordinate[1]] == area and king_area.isOccupied and king_area.piece_color == pc.strcolor: 
                                    pc.area_covered.remove(area)  


        # Blocking King vs King collision. 
        for sqr in Ui_MainWindow.boardSquare_list: 
            if sqr.isClicked: 
                for pc in Pieces.pieces:
                    if [sqr.coordinate[2], sqr.coordinate[1]] == pc.position_numeric and pc.ptype == "King": 
                        for enemy_king in Pieces.pieces: 
                            if enemy_king.ptype == "King" and enemy_king.strcolor != pc.strcolor: 
                                enemy_king.areaCovered()  
                                for area in pc.area_covered: 
                                    if area in enemy_king.area_covered:
                                        pc.area_covered.remove(area)  


        #####
        #####
        #####

        for plyr in Player.player_list: 
            for kg in Pieces.pieces:
                if kg.ptype == "King" and kg.strcolor == plyr.color: 
                    for area in kg.area_covered: 
                        for sqr in Ui_MainWindow.boardSquare_list:
                            if [sqr.coordinate[2], sqr.coordinate[1]] == area and sqr.isOccupied and sqr.piece_color == kg.strcolor: 
                                kg.area_covered.remove(area) 


        # CLEAN UP PART (Logic to avoid king killing protected piece)
        for plyr in Player.player_list:
            king_clicked_mode = True
            if not plyr.isMyTurn:  
                for pc in Pieces.pieces:
                    if pc.strcolor == plyr.color and pc.ptype != "Queen" and pc.ptype != "Rook" and pc.ptype != "Bishop": 
                        pc.areaCovered() 
        king_clicked_mode = False

        # Deleting area covered within allies.
        for plyr in Player.player_list:
            if plyr.isMyTurn:
                for pc in Pieces.pieces:
                    if pc.strcolor == plyr.color:   
                        for area in pc.area_covered:
                            for sqr in Ui_MainWindow.boardSquare_list:
                                if [sqr.coordinate[2], sqr.coordinate[1]] == area and sqr.isOccupied and sqr.piece_color == pc.strcolor:
                                    pc.area_covered.remove(area) 



        Pieces.open_defender_access()

        Pieces.detect_enpassant()        

        Pieces.detect_castle()

          
        # Set logic for promotion
        is_promoting = False

        global promotionBorder
        for pawn in Pieces.pieces:
            if pawn.ptype == "Pawn" and (pawn.position_numeric[1] == 8 or pawn.position_numeric[1] == 1):
                is_promoting = True
                bot_promotion = False                
                for plyr in Player.player_list: 
                    try:
                        Pieces.after_promotion = True                

                        for plyr in Player.player_list:
                            if plyr.isMyTurn: 
                                plyr.isMyTurn = False 
                            else: 
                                plyr.isMyTurn = True
                        Player.launch_turn()                           
                        if plyr.color == pawn.strcolor and plyr.isBot:
                            if plyr.bot.promotion_move == 'q' or plyr.bot.promotion_move == 'Q': 
                                Pieces.promotion(pawn, "Queen") 
                            elif plyr.bot.promotion_move == 'b' or plyr.bot.promotion_move == 'B':
                                Pieces.promotion(pawn, "Bishop")
                            elif plyr.bot.promotion_move == 'r' or plyr.bot.promotion_move == 'R':
                                Pieces.promotion(pawn, "Rook")
                            elif plyr.bot.promotion_move == 'n' or plyr.bot.promotion_move == 'N':
                                Pieces.promotion(pawn, "Knight") 
                            bot_promotion = True 
                    except:
                        pass
                
                if not bot_promotion:
                    if [self.coordinate[2], self.coordinate[1]] == pawn.position_numeric:
                        Pieces.after_promotion = True
                        for sqr in Ui_MainWindow.boardSquare_list:
                            sqr.squares.setEnabled(False)                   

                        for plyr in Player.player_list:
                            if plyr.isMyTurn: 
                                plyr.isMyTurn = False 
                            else: 
                                plyr.isMyTurn = True
                        Player.launch_turn()   

                        promotionBorder = QFrame(main_centralWidget) 
                        promotionBorder.setFrameShape(QFrame.StyledPanel) 
                        promotionBorder.setLineWidth(100) 
                        promotionBorder.resize(120, 400)  

                        x_start = 540
                        for border_loc in range(1, 9): 
                            if pawn.position_numeric[0] == border_loc and pawn.strcolor == "Black": 
                                promotionBorder.move(x_start, 400)
                                break
                            elif pawn.position_numeric[0] == border_loc and pawn.strcolor == "White": 
                                promotionBorder.move(x_start, 200) 
                                break
                            x_start += 100

                        queen_button = QPushButton(promotionBorder) 
                        queen_button.setGeometry(QtCore.QRect(0, 0, 120, 110)) 
                        if pawn.strcolor == "Black": 
                            queen_button.setIcon(QIcon("Black_Queen-removebg-preview.png")) 
                        else: 
                            queen_button.setIcon(QIcon("White_Queen-removebg-preview.png")) 
                        queen_button.setIconSize(QSize(70, 70))
                        queen_button.setStyleSheet("background-color: rgb(255, 255, 255);border: none;color: rgb(255,255,255);")
                        queen_button.clicked.connect(lambda : Pieces.promotion(pawn, "Queen"))
                        queen_button.show()

                        rook_button = QPushButton(promotionBorder) 
                        rook_button.setGeometry(QtCore.QRect(0, 100, 120, 110)) 
                        if pawn.strcolor == "Black": 
                            rook_button.setIcon(QIcon("Black_Rook-removebg-preview.png")) 
                        else: 
                            rook_button.setIcon(QIcon("White_Rook-removebg-preview.png")) 
                        rook_button.setIconSize(QSize(70, 70))                        
                        rook_button.setStyleSheet("background-color: rgb(255, 255, 255);border: none;color: rgb(255,255,255);")                    
                        rook_button.clicked.connect(lambda : Pieces.promotion(pawn, "Rook"))                    
                        rook_button.show()      

                        bishop_button = QPushButton(promotionBorder) 
                        bishop_button.setGeometry(QtCore.QRect(0, 200, 120, 110)) 
                        if pawn.strcolor == "Black": 
                            bishop_button.setIcon(QIcon("Black_Bishop-removebg-preview.png")) 
                        else: 
                            bishop_button.setIcon(QIcon("White_Bishop-removebg-preview.png")) 
                        bishop_button.setIconSize(QSize(70, 70))                        
                        bishop_button.setStyleSheet("background-color: rgb(255, 255, 255);border: none;color: rgb(255,255,255);")                    
                        bishop_button.clicked.connect(lambda : Pieces.promotion(pawn, "Bishop"))                    
                        bishop_button.show()  

                        knight_button = QPushButton(promotionBorder) 
                        knight_button.setGeometry(QtCore.QRect(0, 300, 120, 110)) 
                        if pawn.strcolor == "Black": 
                            knight_button.setIcon(QIcon("Black_Knight-removebg-preview.png")) 
                        else: 
                            knight_button.setIcon(QIcon("White_Knight-removebg-preview.png")) 
                        knight_button.setIconSize(QSize(70, 70))                        
                        knight_button.setStyleSheet("background-color: rgb(255, 255, 255);border: none;color: rgb(255,255,255);")                    
                        knight_button.clicked.connect(lambda : Pieces.promotion(pawn, "Knight"))                    
                        knight_button.show()                                                  

                        promotionBorder.show() 
                        break

        if Pieces.after_promotion: 
            Pieces.write_fen()
            
        # Clean Up, avoiding eating ally.

        for plyr in Player.player_list:
            if plyr.isMyTurn:
                for pc in Pieces.pieces:
                    if pc.strcolor == plyr.color:   
                        for area in pc.area_covered:
                            for sqr in Ui_MainWindow.boardSquare_list:
                                if [sqr.coordinate[2], sqr.coordinate[1]] == area and sqr.isOccupied and sqr.piece_color == pc.strcolor:
                                    pc.area_covered.remove(area)   

                # The logic to make king can't take enemy PROTECTED by enemy king. 

                for kg in Pieces.pieces:
                    if kg.ptype == "King" and kg.strcolor != plyr.color: 
                        king_clicked_mode = True
                        kg.areaCovered()
                        enemy_king = kg
                        

                for kg in Pieces.pieces:
                    if kg.ptype == "King" and kg.strcolor == plyr.color:  
                        for enemy in Pieces.pieces:
                            if enemy.strcolor != kg.strcolor and enemy.position_numeric in enemy_king.area_covered: 
                                try:
                                    kg.area_covered.remove(enemy.position_numeric)
                                except: 
                                    pass



        # Pawn area_covered clean up
        for plyr in Player.player_list:
            if plyr.isMyTurn: 
                for pc in Pieces.pieces:
                    if pc.ptype == "Pawn" and pc.strcolor == plyr.color: 
                        for area in pc.area_covered: 
                            for sqr in Ui_MainWindow.boardSquare_list:
                                if [sqr.coordinate[2], sqr.coordinate[1]] == area: 
                                    try:
                                        if (area == [pc.position_numeric[0], pc.position_numeric[1]+1] or area == [pc.position_numeric[0], pc.position_numeric[1]-1]) and sqr.isOccupied: 
                                            pc.area_covered.remove(area) 
                                    except: 
                                        pass

        if Board.first_move_bugKiller == 0: 
            for pc in Pieces.pieces:
                if pc.ptype == "Queen" or pc.ptype == "Bishop" or pc.ptype == "Rook": 
                    pc.area_covered = []

        Board.first_move_bugKiller += 1  

        # CLEAN UP

        opposite_bugChecker = False
        for pieces in Pieces.pieces:  
            try:
                for plyr in Player.player_list:
                    if not plyr.isMyTurn: 
                        for pc in Pieces.pieces: 
                            if pc.strcolor == plyr.color and [self.coordinate[2], self.coordinate[1]] == pc.position_numeric: 
                                pc.area_covered = []
                                opposite_bugChecker = True 
                                for sqr in Ui_MainWindow.boardSquare_list:
                                    if not sqr.isOccupied: 
                                        sqr.squares.setIcon(QIcon("")) 
                                break               
                if self.coordinate[2] == pieces.position_numeric[0] and self.coordinate[1] == pieces.position_numeric[1] and self.isOccupied and pieces.isMoving and not opposite_bugChecker:
                    pieces.show_area_covered() 
                    Board.attacker = pieces   
                    pieces.isMoving = True 
                    break    
                else: 
                    pieces.isMoving = False 
            except: 
                pass
    
        for plyr in Player.player_list:
            if plyr.isMyTurn: 
                for pc in Pieces.pieces:
                    if pc.ptype == "King" and pc.strcolor == plyr.color and pc.inCheck() and Board.enable_pgn_writeCheck > 0:
                        Board.pgn_string = Board.pgn_string.rstrip() 
                        Board.pgn_string += "+ " 
                        Board.enable_pgn_writeCheck = 0

        Pieces.detect_checkmate_stalemate()  

        if switch_clock and not Pieces.after_promotion:
            Player.playerClock_transition() 
        Pieces.after_promotion = False
            
        switch_clock = False      

                                 
        
        # if not [sqr.coordinate[2], sqr.coordinate[1]] == after_movement:


        if next_sequence:
                        for sqr in Ui_MainWindow.boardSquare_list:
                            if [sqr.coordinate[2], sqr.coordinate[1]] == prev_movement:
                                sqr.squares.setStyleSheet(f"background-color: rgb(255,98,97);border: none;")
                                continue
                            if [sqr.coordinate[2], sqr.coordinate[1]] == after_movement:
                                sqr.squares.setStyleSheet(f"background-color: rgb(230,47, 34);border: none;")                      
                                continue 
                            sqr.squares.setStyleSheet(sqr.info_padding)  
                                
        # for sqr in Ui_MainWindow.boardSquare_list:
        #                     try:
        #                         if not (sqr == self or [sqr.coordinate[2], sqr.coordinate[1]] == prev_movement or [sqr.coordinate[2], sqr.coordinate[1]] == after_movement): 
        #                             sqr.squares.setStyleSheet(sqr.info_padding)
        #                     except:
        #                         pass             

        self.squares.setStyleSheet(f"background-color: rgb{isClicked_color};border: none;")                            

        for sqr in Ui_MainWindow.boardSquare_list:
            if [sqr.coordinate[2], sqr.coordinate[1]] == after_movement:
                sqr.squares.setStyleSheet(f"background-color: rgb(230,47, 34);border: none;") 

                
            
        try: 
            if switch_session_afterPromotion: 
                return
        except: 
            pass

        if playStockfish.checkmate_verificate: 
            return



        for plyr in Player.player_list:
                if not isBot and Board.push_botMovement and plyr.isMyTurn:
                    try:
                        plyr.bot.execute_movement()
                    except:
                        pass
                

    

        print("|-----------------------------------------------------------------------------------------------------------------------|")
    

# Pieces and Gameplay Construction 


class Player(Board): 
    player_list = []
    prevent_doubleTimerSwitch = False

    def __init__(self, color, isBot = False): 
        self.score = 0 

        self.isBot = isBot
        self.color = color 

        if self.isBot:  
            self.bot = playStockfish.BOT_Stockfish(playComputer.rating_slider.value(), self.color)

        self.time_int = control.GameMode.choosen_timeControl 
        self.abs_time_int = self.time_int
        self.time_increment = 0
        for incrm in control.GameMode.button_list: 
            if incrm.increment != 0 and incrm.isClicked: 
                self.time_increment = incrm.increment 
                break 
            else: 
                self.time_increment = 0
        self.fixed_timeControl = self.time_int
        self.minute, self.second = divmod(self.time_int, 60)
        self.disableClock = False

        self.clock_frame = QFrame(main_centralWidget) 
        self.clock_frame.setFrameShape(QFrame.StyledPanel) 
        self.clock_frame.resize(250, 120)   
        self.clock_frame.setLineWidth(100) 

        self.clock_bg = QtWidgets.QLabel(self.clock_frame) 
        self.clock_bg.setPixmap(QtGui.QPixmap("Clock Frame.png"))
    

        self.timer = QtWidgets.QLabel(self.clock_frame)  
        self.timer.setFont(QtGui.QFont("Montserrat", 30))        
        self.timer.setGeometry(QtCore.QRect(30, 27, 140, 60))  

        self.timer.setText("{:02d}:{:02d}".format(self.minute, self.second))       
        self.timer.show()  

        if self.color == 'Black':            
            self.name = "Player 1"
            self.isMyTurn = False 
            self.player_icon = player2_frame
            self.player_name_color  = player2_name
            self.clock_frame.move(275, 250)            
        else:
            self.name = "Player 2"
            self.isMyTurn = True  
            self.player_icon = player1_frame
            self.player_name_color = player1_name
            self.clock_frame.move(275, 625)

        if self.isMyTurn: 
            self.disableClock = False 
        else:
            self.disableClock = True

        self.clock_frame.show()  

        self.starting_timer()
        self.clock_switch()

        self.score_text = QtWidgets.QLabel(main_centralWidget) 
        self.score_text.setText(str(self.score)) 
        if not self.isMyTurn: 
            self.score_text.setGeometry(QtCore.QRect(330, 90, 150, 80))  
        else: 
            self.score_text.setGeometry(QtCore.QRect(330, 820, 150, 80))               
        self.score_text.setFont(QtGui.QFont("Montserrat", 30))
        self.score_text.setStyleSheet("color : rgb(255, 255, 255);")        
        self.score_text.show()        

        Player.player_list.append(self) 

    def starting_timer(self): 
        self.backend_timer = QtCore.QTimer(self.clock_frame) 
        self.backend_timer.timeout.connect(lambda : self.timeout())
        self.backend_timer.start(1000)        

        self.clock_switch()

    def timeout(self): 
        if self.disableClock or self.time_int == 0: 
            if self.time_int == 0: 
                Pieces.timeoutWin()
            return 
        self.time_int -= 1  

        self.minute, self.second = divmod(self.time_int, 60) 

        self.clock_switch() 

    def clock_switch(self): 
        self.timer.setText("{:02d}:{:02d}".format(self.minute, self.second))   
        self.timer.show()

    def playerClock_transition(): 
        if not Pieces.after_promotion:
            for plyr in Player.player_list:
                if not plyr.isMyTurn: 
                    plyr.disableClock = True 
                    plyr.time_int += plyr.time_increment
                    plyr.minute, plyr.second = divmod(plyr.time_int, 60) 
                    plyr.clock_switch()
                else:
                    plyr.disableClock = False   
        else:
            for plyr in Player.player_list:
                if plyr.isMyTurn: 
                    plyr.disableClock = True 
                    plyr.time_int += plyr.time_increment
                    plyr.minute, plyr.second = divmod(plyr.time_int, 60) 
                    plyr.clock_switch()
                else:
                    plyr.disableClock = False             
                                       
    def launch_turn():
        for player in Player.player_list:
            if player.isMyTurn: 
                for sqr in Ui_MainWindow.boardSquare_list:
                    if sqr.isOccupied and sqr.piece_color != player.color:
                        sqr.squares.setEnabled(False)  
                    else:
                        sqr.squares.setEnabled(True)
                player.player_icon.setStyleSheet(f"background-image:url(profile_picture.jpg);border-style:outset;border-width:10px;border-color:{color_isMyTurn}; display: block;") 
                player.player_name_color.setStyleSheet(f"color:{name_color_isMyTurn};")  
                # player.isMyTurn = False
            else:
                player.player_icon.setStyleSheet(f"background-image:url(profile_picture.jpg);border-style:outset;border-width:10px;border-color:{color_isNotMyTurn}; display: block;") 
                player.player_name_color.setStyleSheet(f"color:{name_color_isNotMyTurn};")
                # player.isMyTurn = True  
        
class Pieces(Board):
    after_promotion = False
    execute_checkmateScanner = 0
    fen_notation = ""
    pgn_fileNumber = 1
    black_pieces = []
    white_pieces = [] 
    pieces = []
    def __init__(self, color,strcolor, piece_object):
        self.color = color 
        self.strcolor = strcolor
        self.piece_object = piece_object 
        if self.strcolor == 'Black':
            Pieces.black_pieces.append(self.piece_object) 
        else:
            Pieces.white_pieces.append(self.piece_object)  
        Pieces.pieces.append(self.piece_object)  

    def giveCheck(attacker): 
        for plyr in Player.player_list: 
            if plyr.isMyTurn:
                for pc in Pieces.pieces:  
                    if pc.ptype != "King":
                        continue
                    if attacker.strcolor != plyr.color and pc.ptype == "King" and pc.strcolor != attacker.strcolor and pc.inCheck():
                        for sqr in Ui_MainWindow.boardSquare_list:
                            if [sqr.coordinate[2], sqr.coordinate[1]] != pc.position_numeric and sqr.isOccupied: 
                                sqr.squares.setEnabled(False)  
                        return True
        
        return False 

    def open_defender_access():
        # Opening access to save king from check.
        try:
            for p in Pieces.pieces: 
                Pieces.giveCheck(p)  
                if p.allowMovement > 0:  
                            for sqr in Ui_MainWindow.boardSquare_list:
                                if [sqr.coordinate[2], sqr.coordinate[1]] == p.position_numeric: 
                                    sqr.squares.setEnabled(True)  
        except: 
            pass                        

    
    def detect_enpassant():
        global enpassant_square
        # En Passant Set Up               
        for pawn in Pieces.pieces:
            if pawn.ptype == "Pawn": 
                if pawn.strcolor == "White" and pawn.position_numeric[1] == 5: 
                    for enemy_pawn in Pieces.pieces: 
                        if enemy_pawn.ptype == "Pawn" and enemy_pawn.strcolor != pawn.strcolor and abs(pawn.position_numeric[0]-enemy_pawn.position_numeric[0]) == 1 and pawn.position_numeric[1] == enemy_pawn.position_numeric[1] and enemy_pawn.en_passantable == 1 and enemy_pawn.reject_enpassant == 1:  
                            pawn.area_covered.append([enemy_pawn.position_numeric[0], enemy_pawn.position_numeric[1]+1]) 
                            enpassant_square = [enemy_pawn.position_numeric[0], enemy_pawn.position_numeric[1]+1]
                if pawn.strcolor == "Black" and pawn.position_numeric[1] == 4: 
                    for enemy_pawn in Pieces.pieces: 
                        if enemy_pawn.ptype == "Pawn" and enemy_pawn.strcolor != pawn.strcolor and abs(pawn.position_numeric[0]-enemy_pawn.position_numeric[0]) == 1 and pawn.position_numeric[1] == enemy_pawn.position_numeric[1] and enemy_pawn.en_passantable == 1 and enemy_pawn.reject_enpassant == 1:  
                            pawn.area_covered.append([enemy_pawn.position_numeric[0], enemy_pawn.position_numeric[1]-1])  
                            enpassant_square = [enemy_pawn.position_numeric[0], enemy_pawn.position_numeric[1]-1]                            

    
    def detect_castle():
        for plyr in Player.player_list:
            if plyr.isMyTurn:
                for pc in Pieces.pieces:
                    if pc.strcolor == plyr.color:
                        for sqr in Ui_MainWindow.boardSquare_list:
                            if [sqr.coordinate[2], sqr.coordinate[1]]  == pc.position_numeric:
                                sqr.squares.setEnabled(True) 

                # Block castle upon checks.
                for kg in Pieces.pieces: 
                    if kg.ptype == "King" and kg.inCheck() and kg.strcolor == plyr.color: 
                        for area in kg.area_covered: 
                            if abs(area[0]-kg.position_numeric[0]) == 2 or abs(area[0]-kg.position_numeric[0]) == 3: 
                                kg.area_covered.remove(area) 
                    # Block castle upon interrupting pieces.
                    if kg.ptype == "King" and plyr.color == kg.strcolor: 
                        if [kg.position_numeric[0]+2, kg.position_numeric[1]] in kg.area_covered or [kg.position_numeric[0]-2, kg.position_numeric[1]] in kg.area_covered:
                            allow_castle_long = 0
                            for sqr in Ui_MainWindow.boardSquare_list: 
                                try:
                                    if ([sqr.coordinate[2], sqr.coordinate[1]] == [kg.position_numeric[0]+1, kg.position_numeric[1]] and sqr.isOccupied): 
                                                kg.area_covered.remove([kg.position_numeric[0]+2, kg.position_numeric[1]])
                                    if ([sqr.coordinate[2], sqr.coordinate[1]] == [kg.position_numeric[0]-1, kg.position_numeric[1]] or [sqr.coordinate[2], sqr.coordinate[1]] == [kg.position_numeric[0]-3, kg.position_numeric[1]]) and sqr.isOccupied:     
                                        kg.area_covered.remove([kg.position_numeric[0]-2, kg.position_numeric[1]])                                      
                                except:
                                    pass
                        # Block castle upon enemy attacks (excluding checks) 
                        for rooks in Pieces.pieces:
                            if rooks.ptype == "Rook" and rooks.strcolor == kg.strcolor and not rooks.firstMove and not kg.firstMove and abs(rooks.starting_position[0]-kg.starting_position[0]) == 3: # Short Castle 
                                for x_axis in range(kg.starting_position[0]+1, rooks.starting_position[0]): 
                                    for enemy in Pieces.pieces:
                                        if enemy.strcolor != kg.strcolor: 
                                            if [x_axis, kg.starting_position[1]] in enemy.area_covered:                            
                                                try: 
                                                    for area in kg.area_covered:
                                                        if abs(area[0]-kg.starting_position[0]) == 2:
                                                            kg.area_covered.remove([area[0], kg.starting_position[1]]) 
                                                except: 
                                                    pass

                            if rooks.ptype == "Rook" and rooks.strcolor == kg.strcolor and not rooks.firstMove and not kg.firstMove and abs(rooks.starting_position[0]-kg.starting_position[0]) == 4: # Long Castle
                                for x_axis in range(rooks.starting_position[0]+1, kg.starting_position[0]): 
                                    for enemy in Pieces.pieces:
                                        if enemy.strcolor != kg.strcolor: 
                                            if [x_axis, kg.starting_position[1]] in enemy.area_covered:  
                                                try:
                                                    for area in kg.area_covered:
                                                        if abs(area[0]-kg.starting_position[0]) == 2:
                                                            kg.area_covered.remove([area[0], kg.starting_position[1]]) 
                                                except: 
                                                    pass                  

    def detect_checkmate_stalemate(): 
        if Pieces.execute_checkmateScanner > 0: 
            return 
        # Mate Checker Logic
        # Using FEN Notation and input it to chess module. Writing the FEN Notation of the latest position 

        Pieces.write_fen()                      

        fen_viewer = chess.Board(Pieces.fen_notation)         

        if fen_viewer.is_checkmate():
            Pieces.execute_checkmateScanner += 1
            winner_widget = QFrame(main_centralWidget)
            winner_widget.setFrameShape(QFrame.StyledPanel) 
            winner_widget.setLineWidth(100) 
            winner_widget.resize(600, 250)
            winner_widget.move(650, 375)  
            winner_label = QtWidgets.QLabel(winner_widget)

            for plyr in Player.player_list:
                if not plyr.isMyTurn: 
                    winner_label.setPixmap(QtGui.QPixmap(f"{plyr.color}_WinNotification.png"))
                    winner_name = QtWidgets.QLabel(winner_widget) 
                    winner_name.setText(plyr.name) 
                    winner_name.setFont(QtGui.QFont("Montserrat", 15)) 
                    winner_name.setGeometry(QtCore.QRect(60, 180, 150, 80)) 
                    winner_name.show() 


            winner_widget.show()

            Pieces.endGame()
            Pieces.incrementScore()

            newGame_text_confirmation = QtWidgets.QLabel(winner_widget) 
            newGame_text_confirmation.setText("Start new game?") 
            newGame_text_confirmation.setFont(QtGui.QFont("Arial", 10))
            newGame_text_confirmation.setGeometry(QtCore.QRect(30, 30, 200, 200)) 
            newGame_text_confirmation.move(300, 130) 
            newGame_text_confirmation.show()            

            newGame_button_yes = QPushButton(winner_widget) 
            newGame_button_yes.setGeometry(QtCore.QRect(20, 20, 30, 30)) 
            newGame_button_yes.move(425, 215) 
            newGame_button_yes.clicked.connect(lambda : Pieces.start_newGame(winner_widget))
            newGame_button_yes.setIcon(QIcon("Yes_Button"))            
            newGame_button_yes.setStyleSheet("border-radius: 15px;border-style: outset;")                        
            newGame_button_yes.show()

            newGame_button_no = QPushButton(winner_widget) 
            newGame_button_no.setGeometry(QtCore.QRect(20, 20, 30, 30)) 
            newGame_button_no.move(455, 215) 
            newGame_button_no.clicked.connect(lambda : sys.exit())
            newGame_button_no.setIcon(QIcon("No_Button"))
            newGame_button_no.setStyleSheet("border-radius: 15px;border-style: outset;")            
            newGame_button_no.show()       

            Board.pgn_string = Board.pgn_string.rstrip("+ ") 
            Board.pgn_string += "#" 

            if Board.move_num_changer % 2 != 0: 
                Board.pgn_string += " 1-0" 
            else:
                Board.pgn_string += " 0-1"

            Pieces.exportPGN_button(winner_widget)                     
            Board.move_number = 0

        elif fen_viewer.is_stalemate(): 
            Pieces.execute_checkmateScanner += 1
            winner_widget = QFrame(main_centralWidget)
            winner_widget.setFrameShape(QFrame.StyledPanel) 
            winner_widget.setLineWidth(100) 
            winner_widget.resize(600, 250)
            winner_widget.move(650, 375)  

            winner_label = QtWidgets.QLabel(winner_widget) 
            winner_label.setPixmap(QtGui.QPixmap("Stalemate Notification.png"))

            winner_widget.show()

            Pieces.endGame()    
            Pieces.draw_incrementHalf() 

            newGame_text_confirmation = QtWidgets.QLabel(winner_widget) 
            newGame_text_confirmation.setText("Start new game?") 
            newGame_text_confirmation.setFont(QtGui.QFont("Arial", 10))
            newGame_text_confirmation.setGeometry(QtCore.QRect(30, 30, 200, 200)) 
            newGame_text_confirmation.move(220, 130) 
            newGame_text_confirmation.show()            

            newGame_button_yes = QPushButton(winner_widget) 
            newGame_button_yes.setGeometry(QtCore.QRect(20, 20, 30, 30)) 
            newGame_button_yes.move(345, 215) 
            newGame_button_yes.clicked.connect(lambda : Pieces.start_newGame(winner_widget))
            newGame_button_yes.setIcon(QIcon("Yes_Button"))
            newGame_button_yes.setStyleSheet("border-radius: 15px;border-style: outset;")            
            newGame_button_yes.show()

            newGame_button_no = QPushButton(winner_widget) 
            newGame_button_no.setGeometry(QtCore.QRect(20, 20, 30, 30)) 
            newGame_button_no.move(375, 215) 
            newGame_button_no.clicked.connect(lambda : sys.exit())
            newGame_button_no.setIcon(QIcon("No_Button"))
            newGame_button_no.setStyleSheet("border-radius: 15px;border-style: outset;")
            newGame_button_no.show() 

            Board.pgn_string = Board.pgn_string.rstrip("+ ") 
            Board.pgn_string += "== 1/2-1/2"    

            Pieces.exportPGN_button(winner_widget)  
            Board.move_number = 0 
        elif fen_viewer.is_insufficient_material():
            Pieces.execute_checkmateScanner += 1
            winner_widget = QFrame(main_centralWidget)
            winner_widget.setFrameShape(QFrame.StyledPanel) 
            winner_widget.setLineWidth(100) 
            winner_widget.resize(600, 250)
            winner_widget.move(650, 375)  

            winner_label = QtWidgets.QLabel(winner_widget) 
            winner_label.setPixmap(QtGui.QPixmap("Draw Notification.png"))

            winner_widget.show()

            Pieces.endGame()    
            Pieces.draw_incrementHalf() 

            newGame_text_confirmation = QtWidgets.QLabel(winner_widget) 
            newGame_text_confirmation.setText("Start new game?") 
            newGame_text_confirmation.setFont(QtGui.QFont("Arial", 10))
            newGame_text_confirmation.setGeometry(QtCore.QRect(30, 30, 200, 200)) 
            newGame_text_confirmation.move(220, 130) 
            newGame_text_confirmation.show()            

            newGame_button_yes = QPushButton(winner_widget) 
            newGame_button_yes.setGeometry(QtCore.QRect(20, 20, 30, 30)) 
            newGame_button_yes.move(345, 215) 
            newGame_button_yes.clicked.connect(lambda : Pieces.start_newGame(winner_widget))
            newGame_button_yes.setIcon(QIcon("Yes_Button"))
            newGame_button_yes.setStyleSheet("border-radius: 15px;border-style: outset;")            
            newGame_button_yes.show()

            newGame_button_no = QPushButton(winner_widget) 
            newGame_button_no.setGeometry(QtCore.QRect(20, 20, 30, 30)) 
            newGame_button_no.move(375, 215) 
            newGame_button_no.clicked.connect(lambda : sys.exit())
            newGame_button_no.setIcon(QIcon("No_Button"))
            newGame_button_no.setStyleSheet("border-radius: 15px;border-style: outset;")
            newGame_button_no.show() 

            Board.pgn_string = Board.pgn_string.rstrip("+ ") 
            Board.pgn_string += "== 1/2-1/2"    

            Pieces.exportPGN_button(winner_widget)  
            Board.move_number = 0 

        if playStockfish.checkmate_verificate:
            return
        # Find best move according to Stockfish (If playing against Bot)              
        for plyr in Player.player_list:
            if plyr.isMyTurn and plyr.isBot and Board.enable_findBotMovement: 
                plyr.bot.make_movement()
                    
        Pieces.fen_notation = ''

        

    def start_newGame(delete_winnerWidget):
        global prev_movement 
        global after_movement
        for sqr in Ui_MainWindow.boardSquare_list:
            sqr.squares.setStyleSheet(sqr.info_padding)
        prev_movement = None 
        after_movement = None
        playStockfish.BOT_Stockfish.disable_clockSwitch = 0
        Pieces.after_promotion = False
        Pieces.execute_checkmateScanner = 0
        playStockfish.checkmate_verificate = False
        GamePack.bot_allowMovement = False
        Board.enable_findBotMovement = True
        Board.push_botMovement = False
        Board.pgn_string = ''  
        Board.move_number = 0 
        Board.move_num_changer = 0 
        Board.enable_pgn_writeCheck = 0                      
        Pieces.pgn_fileNumber += 1
        for pc in Pieces.pieces:
            for sqr in Ui_MainWindow.boardSquare_list:
                if [sqr.coordinate[2], sqr.coordinate[1]] == pc.position_numeric: 
                    sqr.piece_color = None 
                    sqr.isOccupied = False 
                    sqr.squares.setIcon(QIcon(""))
            Pieces.pieces = []                    
            del pc

        for plyr in Player.player_list:
            if plyr.color == "White":
                plyr.isMyTurn = True
                plyr.disableClock = False
            else: 
                plyr.isMyTurn = False
                plyr.disableClock = True  
            plyr.time_int = plyr.abs_time_int
            plyr.minute, plyr.second = divmod(plyr.time_int, 60)
            plyr.clock_switch()

        GamePack.classic_game()

        delete_winnerWidget.deleteLater()

        for plyr in Player.player_list:
            if plyr.isMyTurn: 
                for sqr in Ui_MainWindow.boardSquare_list:
                    if sqr.piece_color == plyr.color or sqr.piece_color == None: 
                        sqr.squares.setEnabled(True)


    def timeoutWin(): 
        winner_widget = QFrame(main_centralWidget)
        winner_widget.setFrameShape(QFrame.StyledPanel) 
        winner_widget.setLineWidth(100) 
        winner_widget.resize(600, 250)
        winner_widget.move(650, 375)  
        winner_label = QtWidgets.QLabel(winner_widget)

        for plyr in Player.player_list:
            if not plyr.isMyTurn: 
                winner_label.setPixmap(QtGui.QPixmap(f"{plyr.color}_WinNotification_Time.png"))
                winner_name = QtWidgets.QLabel(winner_widget) 
                winner_name.setText(plyr.name) 
                winner_name.setFont(QtGui.QFont("Montserrat", 15)) 
                winner_name.setGeometry(QtCore.QRect(60, 180, 150, 80)) 
                winner_name.show()

        winner_widget.show()

        Pieces.endGame()
    
    def write_fen():
        board_file_x = 1 
        board_rank_y = 8 
        empty_ctr = 0 
        Pieces.fen_notation = ""

        for y in range(8):
            if board_rank_y < 1: 
                break
            for x in range(1, 9): 
                for sqr in Ui_MainWindow.boardSquare_list:
                    if [sqr.coordinate[2], sqr.coordinate[1]] == [x, board_rank_y]: 
                        if not sqr.isOccupied: 
                            empty_ctr += 1
                        else: 
                            if not empty_ctr == 0:
                                Pieces.fen_notation += str(empty_ctr)
                                empty_ctr = 0
                        for pc in Pieces.pieces: 
                            if pc.position_numeric == [sqr.coordinate[2], sqr.coordinate[1]]: 
                                if pc.strcolor == "White": 
                                    if pc.ptype == "Knight": 
                                        Pieces.fen_notation += "N"
                                    else:
                                        Pieces.fen_notation += pc.ptype[0]                                                       
                                else: 
                                    if pc.ptype == "Knight": 
                                        Pieces.fen_notation += "n"
                                    else:
                                        Pieces.fen_notation += str(pc.ptype[0].lower()) 
                if x == 8 and not empty_ctr == 0: 
                    Pieces.fen_notation += str(empty_ctr) 
                    empty_ctr = 0  
                
                        
            if not y == 7:               
                Pieces.fen_notation += "/"                     
            board_rank_y -= 1  
    
        for plyr in Player.player_list:
            if plyr.isMyTurn: 
                Pieces.fen_notation += f" {plyr.color[0].lower()}" 
                break 

        return Pieces.fen_notation        
        



    def endGame(): 
        for sqr in Ui_MainWindow.boardSquare_list:
            sqr.squares.setEnabled(False)          

        for plyr in Player.player_list:
            plyr.disableClock = True  

    def incrementScore(): 
        for plyr in Player.player_list: 
            if not plyr.isMyTurn: 
                plyr.score += 1 
                plyr.score_text.setText(str(plyr.score))
        plyr.score_text.show()

    def draw_incrementHalf(): 
        for plyr in Player.player_list:
            plyr.score += 0.5 
            plyr.score_text.setText(str(plyr.score))           
            plyr.score_text.show()            


    def promotion(pawn, target):
        global switch_session_afterPromotion
        Board.push_botMovement = True
        for pc in Pieces.pieces:
            if pc == pawn and pc.ptype == "Pawn": 
                temp_pawn = pc 
                if temp_pawn.strcolor == "White": 
                    temp_color = Qt.white 
                else:
                    temp_color = Qt.black
                Pieces.pieces.remove(pc) 
                del pc 
                if target == "Queen": 
                    promoted_pawn = Queen(temp_color, temp_pawn.strcolor, "Queen", temp_pawn.rank, list(string.ascii_lowercase)[temp_pawn.file-1]) 
                    Board.pgn_string = Board.pgn_string.rstrip() 
                    Board.pgn_string += "=Q "
                elif target == "Rook": 
                    promoted_pawn = Rook(temp_color, temp_pawn.strcolor, "Rook", temp_pawn.rank, list(string.ascii_lowercase)[temp_pawn.file-1])                    
                    Board.pgn_string = Board.pgn_string.rstrip() 
                    Board.pgn_string += "=R "                    
                elif target == "Bishop": 
                    promoted_pawn = Bishop(temp_color, temp_pawn.strcolor, "Bishop", temp_pawn.rank, list(string.ascii_lowercase)[temp_pawn.file-1])                    
                    Board.pgn_string = Board.pgn_string.rstrip() 
                    Board.pgn_string += "=B "                    
                elif target == "Knight":
                    promoted_pawn = Knight(temp_color, temp_pawn.strcolor, "Knight", temp_pawn.rank, list(string.ascii_lowercase)[temp_pawn.file-1])                     
                    Board.pgn_string = Board.pgn_string.rstrip() 
                    Board.pgn_string += "=N "
                Pieces.after_promotion = True
                Player.playerClock_transition() 


                for plyr in Player.player_list: 
                    if plyr.isMyTurn: 
                        plyr.isMyTurn = False 
                    else: 
                        plyr.isMyTurn = True 

                Pieces.detect_checkmate_stalemate()                           

                Board.push_botMovement = True
                switch_session_afterPromotion = False

                for plyr in Player.player_list:
                    try:
                        switch_session_afterPromotion = True                        
                        plyr.bot.execute_movement() 
                        switch_session_afterPromotion = False

                        for plyr in Player.player_list:  
                            if plyr.isMyTurn: 
                                plyr.isMyTurn = False 
                            else: 
                                plyr.isMyTurn = True 
                    except: 
                        pass
            
                    
                                 
                # for plyr in Player.player_list:
                #     if plyr.isMyTurn and plyr.isBot: 
                #         plyr.time_int += plyr.time_increment
                #         plyr.minute, plyr.second = divmod(plyr.time_int, 60)                         


            
                # Pieces.pieces.append(promoted_pawn) 

                for sqr in Ui_MainWindow.boardSquare_list: 
                    if sqr.coordinate[0] == promoted_pawn.file and sqr.coordinate[1] == promoted_pawn.rank: 
                        sqr.squares.setIcon(promoted_pawn.image)  
                        sqr.squares.setIconSize(QSize(80,80))
                        sqr.isOccupied = True
                        break


        for plyr in Player.player_list:
            if plyr.isMyTurn and not plyr.isBot:
                            for sqr in Ui_MainWindow.boardSquare_list:
                                if sqr.isOccupied and sqr.piece_color == plyr.color: 
                                    sqr.squares.setEnabled(True)
                                else:
                                    sqr.squares.setEnabled(False)
                            Player.launch_turn()
                            try: 
                                promotionBorder.deleteLater()
                            except:
                                pass                                     
                            return          
                  
        for plyr in Player.player_list:
            if plyr.isMyTurn: 
                plyr.isMyTurn = False 
            else: 
                plyr.isMyTurn = True        
        Player.launch_turn() 
    


        for plyr in Player.player_list:
            if plyr.isMyTurn: 
                    print(plyr.color)
                    for sqr in Ui_MainWindow.boardSquare_list:
                        if sqr.isOccupied and sqr.piece_color == plyr.color:
                            print(sqr.coordinate)
                            sqr.squares.setEnabled(True) 
                        else:
                            sqr.squares.setEnabled(False)
         
        try: 
            promotionBorder.deleteLater()
        except:
            pass 

    def exportPGN_button(winner_widget): 
        exportPGN = QtWidgets.QPushButton(winner_widget) 
        exportPGN.setGeometry(QtCore.QRect(525, 180, 60, 60)) 
        exportPGN.setIcon(QIcon("ExportPGN_Button.png"))
        exportPGN.setIconSize(QSize(60, 60))
        exportPGN.clicked.connect(lambda : Pieces.exportPGN_command())
        exportPGN.show()

    def exportPGN_command(): 
        subprocess.Popen('explorer')        
        if os.path.exists(f'pgn_{str(Pieces.pgn_fileNumber)}.txt'): 
            os.remove(f"pgn_{str(Pieces.pgn_fileNumber)}.txt")      

        with open(f"pgn_{str(Pieces.pgn_fileNumber)}.txt", 'w') as pgn_file: 
            pgn_file.write(Board.pgn_string) 
        
    def LimitDown_Movement(piece_object): 
        # Check Down Movement Limit 
        down = 1
        for i in range(8):
            check = [piece_object.position_numeric[0], piece_object.position_numeric[1]-down]   
            for sqr in Ui_MainWindow.boardSquare_list: 
                try:
                    if sqr.coordinate[2] == check[0] and sqr.coordinate[1] == check[1]: 
                        if (sqr.isOccupied and sqr.piece_color == piece_object.strcolor):  
                            try: 
                                dlt = 0
                                # for plyr in Player.player_list:
                                #     if not plyr.isMyTurn: 
                                #         dlt = 1                                
                                if king_clicked_mode:
                                    dlt = 1                                
                                for ahead in piece_object.area_covered: 
                                    piece_object.area_covered.remove([check[0], check[1]-dlt])
                                    dlt += 1
                                break 
                            except:
                                pass  
                        elif sqr.isOccupied and sqr.piece_color != piece_object.strcolor:
                            if piece_object.second_checker and (piece_object.ptype == "King" or piece_object.ptype == "Rook" or piece_object.ptype == "Bishop" or piece_object.ptype == "Queen"): 
                                for pc in Pieces.pieces: 
                                    if pc.position_numeric == [sqr.coordinate[2], sqr.coordinate[1]] and pc.ptype != "King": 
                                        try:
                                            dlt = 1
                                            for ahead in piece_object.area_covered: 
                                                piece_object.area_covered.remove([check[0], check[1]-dlt])  
                                                dlt += 1
                                            break 
                                        except:
                                            pass  
                                break
                            try:
                                dlt = 1
                                for ahead in piece_object.area_covered: 
                                    piece_object.area_covered.remove([check[0], check[1]-dlt])  
                                    dlt += 1
                                break 
                            except:
                                pass 
                      
                except: 
                    pass
            down += 1  
        return piece_object.area_covered

    def LimitUp_Movement(piece_object):
        # Check Up Movement Limit 
        up = 1
        for i in range(8):
            check = [piece_object.position_numeric[0], piece_object.position_numeric[1]+up]   
            for sqr in Ui_MainWindow.boardSquare_list: 
                try:
                    if sqr.coordinate[2] == check[0] and sqr.coordinate[1] == check[1]:
                        if (sqr.isOccupied and sqr.piece_color == piece_object.strcolor):  
                            try: 
                                dlt = 0
                                # for plyr in Player.player_list:
                                #     if not plyr.isMyTurn: 
                                #         dlt = 1                                
                                if king_clicked_mode:
                                    dlt = 1                                
                                for ahead in piece_object.area_covered:
                                    piece_object.area_covered.remove([check[0], check[1]+dlt])  
                                    dlt += 1
                                break 
                            except:
                                pass  
                        elif sqr.isOccupied and sqr.piece_color != piece_object.strcolor:                  
                            if piece_object.second_checker and (piece_object.ptype == "King" or piece_object.ptype == "Rook" or piece_object.ptype == "Bishop" or piece_object.ptype == "Queen"): 
                                for pc in Pieces.pieces: 
                                    if pc.position_numeric == [sqr.coordinate[2], sqr.coordinate[1]] and pc.ptype != "King":                                                                                  
                                        try: 
                                            dlt = 1
                                            for ahead in piece_object.area_covered: 
                                                piece_object.area_covered.remove([check[0], check[1]+dlt])  
                                                dlt += 1
                                            break 
                                        except:
                                            pass   
                                break                                        
                            try: 
                                dlt = 1
                                for ahead in piece_object.area_covered: 
                                    piece_object.area_covered.remove([check[0], check[1]+dlt])  
                                    dlt += 1
                                break 
                            except:
                                pass   
                except:
                    pass

            up += 1  
        return piece_object.area_covered

    def LimitRight_Movement(piece_object):
        # Check Right Movement Limit  
        right = 1
        for i in range(8):
            check = [piece_object.position_numeric[0]+right, piece_object.position_numeric[1]]   
            for sqr in Ui_MainWindow.boardSquare_list: 
                try:
                    if sqr.coordinate[2] == check[0] and sqr.coordinate[1] == check[1]:
                        if (sqr.isOccupied and sqr.piece_color == piece_object.strcolor): 
                            try: 
                                dlt = 0
                                # for plyr in Player.player_list:
                                #     if not plyr.isMyTurn: 
                                #         dlt = 1                                
                                if king_clicked_mode:
                                    dlt = 1                                 
                                for ahead in piece_object.area_covered:
                                    piece_object.area_covered.remove([check[0]+dlt, check[1]]) 
                                    dlt += 1
                                break 
                            except:
                                pass  
                        elif sqr.isOccupied and sqr.piece_color != piece_object.strcolor:                    
                            if piece_object.second_checker and (piece_object.ptype == "King" or piece_object.ptype == "Rook" or piece_object.ptype == "Bishop" or piece_object.ptype == "Queen"):  
                                for pc in Pieces.pieces: 
                                    if pc.position_numeric == [sqr.coordinate[2], sqr.coordinate[1]] and pc.ptype != "King": 
                                        try:                          
                                            dlt = 1
                                            for ahead in piece_object.area_covered: 
                                                piece_object.area_covered.remove([check[0]+dlt, check[1]])  
                                                dlt += 1
                                            break 
                                        except:
                                            pass
                                break
                            try:                          
                                dlt = 1
                                for ahead in piece_object.area_covered: 
                                    piece_object.area_covered.remove([check[0]+dlt, check[1]])  
                                    dlt += 1
                                break 
                            except:
                                pass   
                except: 
                    pass
            right += 1   
        return piece_object.area_covered

    def LimitLeft_Movement(piece_object):
        # Check Left Movement Limit  
        left = 1 
        for i in range(8):
            check = [piece_object.position_numeric[0]-left, piece_object.position_numeric[1]]   
            for sqr in Ui_MainWindow.boardSquare_list: 
                try:    
                    if sqr.coordinate[2] == check[0] and sqr.coordinate[1] == check[1]: 
                        if (sqr.isOccupied and sqr.piece_color == piece_object.strcolor):  
                            try: 
                                dlt = 0
                                # for plyr in Player.player_list:
                                #     if not plyr.isMyTurn: 
                                #         dlt = 1                                
                                if king_clicked_mode:
                                    dlt = 1                                
                                for ahead in piece_object.area_covered:
                                    piece_object.area_covered.remove([check[0]-dlt, check[1]]) 
                                    dlt += 1
                                break 
                            except:
                                pass  
                        elif sqr.isOccupied and sqr.piece_color != piece_object.strcolor:                   
                            if piece_object.second_checker and (piece_object.ptype == "King" or piece_object.ptype == "Rook" or piece_object.ptype == "Bishop" or piece_object.ptype == "Queen"):  
                                for pc in Pieces.pieces: 
                                    if pc.position_numeric == [sqr.coordinate[2], sqr.coordinate[1]] and pc.ptype != "King":                                        
                                        try:                      
                                            dlt = 1
                                            for ahead in piece_object.area_covered: 
                                                piece_object.area_covered.remove([check[0]-dlt, check[1]])  
                                                dlt += 1
                                            break 
                                        except:
                                            pass 
                                break                                     
                            try:                      
                                dlt = 1
                                for ahead in piece_object.area_covered: 
                                    piece_object.area_covered.remove([check[0]-dlt, check[1]])  
                                    dlt += 1
                                break 
                            except:
                                pass   
                except: 
                    pass
            left += 1   
        return piece_object.area_covered

    def LimitRightUp_Movement(piece_object):
        # Check Right-Up Movement Limit  
        right = 1
        up = 1
        for i in range(8):
            check = [piece_object.position_numeric[0]+right, piece_object.position_numeric[1]+up]   
            for sqr in Ui_MainWindow.boardSquare_list: 
                try:
                    if (sqr.coordinate[2] == check[0] and sqr.coordinate[1] == check[1]):
                        if sqr.isOccupied and sqr.piece_color == piece_object.strcolor: 
                            try: 
                                dlt = 0 
                                # for plyr in Player.player_list:
                                #     if not plyr.isMyTurn: 
                                #         dlt = 1
                                if king_clicked_mode:
                                    dlt = 1
                                for ahead in piece_object.area_covered:
                                    piece_object.area_covered.remove([check[0]+dlt, check[1]+dlt])  
                                    dlt += 1
                                break 
                            except:
                                pass  
                        elif sqr.isOccupied and sqr.piece_color != piece_object.strcolor:                       
                            if piece_object.second_checker and (piece_object.ptype == "King" or piece_object.ptype == "Rook" or piece_object.ptype == "Bishop" or piece_object.ptype == "Queen"):  
                                for pc in Pieces.pieces: 
                                    if pc.position_numeric == [sqr.coordinate[2], sqr.coordinate[1]] and pc.ptype != "King":                                   
                                        try:                         
                                            dlt = 1
                                            for ahead in piece_object.area_covered: 
                                                piece_object.area_covered.remove([check[0]+dlt, check[1]+dlt])  
                                                dlt += 1
                                            break 
                                        except:
                                            pass   
                                    break                                      
                            try:                         
                                dlt = 1
                                for ahead in piece_object.area_covered: 
                                    piece_object.area_covered.remove([check[0]+dlt, check[1]+dlt])  
                                    dlt += 1
                                break 
                            except:
                                pass   
                except: 
                    pass
            right += 1 
            up += 1 
        return piece_object.area_covered
    def LimitRightDown_Movement(piece_object):
        # Check Right-Down Movement Limit 
        right = 1
        down = 1
        for i in range(8):
            check = [piece_object.position_numeric[0]+right, piece_object.position_numeric[1]-down]   
            for sqr in Ui_MainWindow.boardSquare_list: 
                try:
                    if (sqr.coordinate[2] == check[0] and sqr.coordinate[1] == check[1]):
                        if sqr.isOccupied and sqr.piece_color == piece_object.strcolor: 
                            try: 
                                dlt = 0
                                # for plyr in Player.player_list:
                                #     if not plyr.isMyTurn: 
                                #         dlt = 1                                
                                if king_clicked_mode:
                                    dlt = 1                                
                                for ahead in piece_object.area_covered:
                                    piece_object.area_covered.remove([check[0]+dlt, check[1]-dlt]) 
                                    dlt += 1
                                break 
                            except:
                                pass  
                        elif sqr.isOccupied and sqr.piece_color != piece_object.strcolor:        
                            if piece_object.second_checker and (piece_object.ptype == "King" or piece_object.ptype == "Rook" or piece_object.ptype == "Bishop" or piece_object.ptype == "Queen"):  
                                for pc in Pieces.pieces: 
                                    if pc.position_numeric == [sqr.coordinate[2], sqr.coordinate[1]] and pc.ptype != "King":                                                    
                                        try:                           
                                            dlt = 1
                                            for ahead in piece_object.area_covered: 
                                                piece_object.area_covered.remove([check[0]+dlt, check[1]-dlt])  
                                                dlt += 1
                                            break 
                                        except:
                                            pass 
                                break                                       
                            try:                           
                                dlt = 1
                                for ahead in piece_object.area_covered: 
                                    piece_object.area_covered.remove([check[0]+dlt, check[1]-dlt])  
                                    dlt += 1
                                break 
                            except:
                                pass   
                except: 
                    pass
            right += 1  
            down += 1 
        return piece_object.area_covered

    def LimitLeftUp_Movement(piece_object):
        # Check Left-Up Movement Limit 
        left = 1 
        up = 1
        for i in range(8):
            check = [piece_object.position_numeric[0]-left, piece_object.position_numeric[1]+up]   
            for sqr in Ui_MainWindow.boardSquare_list: 
                try:
                    if sqr.coordinate[2] == check[0] and sqr.coordinate[1] == check[1]:
                        if (sqr.isOccupied and sqr.piece_color == piece_object.strcolor):  
                            try: 
                                dlt = 0
                                # for plyr in Player.player_list:
                                #     if not plyr.isMyTurn: 
                                #         dlt = 1                                
                                if king_clicked_mode:
                                    dlt = 1                                
                                for ahead in piece_object.area_covered:
                                    piece_object.area_covered.remove([check[0]-dlt, check[1]+dlt]) 
                                    dlt += 1
                                break 
                            except:
                                pass  
                        elif sqr.isOccupied and sqr.piece_color != piece_object.strcolor:                      
                            if piece_object.second_checker and (piece_object.ptype == "King" or piece_object.ptype == "Rook" or piece_object.ptype == "Bishop" or piece_object.ptype == "Queen"):
                                for pc in Pieces.pieces: 
                                    if pc.position_numeric == [sqr.coordinate[2], sqr.coordinate[1]] and pc.ptype != "King":                                     
                                        try:                         
                                            dlt = 1
                                            for ahead in piece_object.area_covered: 
                                                piece_object.area_covered.remove([check[0]-dlt, check[1]+dlt])  
                                                dlt += 1
                                            break 
                                        except:
                                            pass   
                                break                                        
                            try:                         
                                dlt = 1
                                for ahead in piece_object.area_covered: 
                                    piece_object.area_covered.remove([check[0]-dlt, check[1]+dlt])  
                                    dlt += 1
                                break 
                            except:
                                pass   
                except: 
                    pass
            left += 1 
            up += 1 
        return piece_object.area_covered 

    def LimitLeftDown_Movement(piece_object):
        # Check Left-Down Movement Limit  
        left = 1 
        down = 1
        for i in range(8): 
            check = [piece_object.position_numeric[0]-left, piece_object.position_numeric[1]-down]   
            for sqr in Ui_MainWindow.boardSquare_list: 
                try:
                    if sqr.coordinate[2] == check[0] and sqr.coordinate[1] == check[1]:
                        if (sqr.isOccupied and sqr.piece_color == piece_object.strcolor):  
                            try: 
                                dlt = 0
                                # for plyr in Player.player_list:
                                #     if not plyr.isMyTurn: 
                                #         dlt = 1                                
                                if king_clicked_mode:
                                    dlt = 1                            
                                for ahead in piece_object.area_covered:
                                    piece_object.area_covered.remove([check[0]-dlt, check[1]-dlt])  
                                    dlt += 1
                                break 
                            except:
                                pass  
                        elif sqr.isOccupied and sqr.piece_color != piece_object.strcolor:                    
                            if piece_object.second_checker and (piece_object.ptype == "King" or piece_object.ptype == "Rook" or piece_object.ptype == "Bishop" or piece_object.ptype == "Queen"):  
                                for pc in Pieces.pieces: 
                                    if pc.position_numeric == [sqr.coordinate[2], sqr.coordinate[1]] and pc.ptype != "King":                                                       
                                        try:                         
                                            dlt = 1
                                            for ahead in piece_object.area_covered: 
                                                piece_object.area_covered.remove([check[0]-dlt, check[1]-dlt])  
                                                dlt += 1
                                            break 
                                        except:
                                            pass 
                                break                                             
                            try:                         
                                dlt = 1
                                for ahead in piece_object.area_covered: 
                                    piece_object.area_covered.remove([check[0]-dlt, check[1]-dlt])  
                                    dlt += 1
                                break 
                            except:
                                pass    
                except: 
                    pass
            left += 1 
            down += 1 
        return piece_object.area_covered

# Setting Up Pieces 

class King(Board):
    def __init__(self, color, strcolor,ptype, rank, file): 
        self.color = color
        self.ptype = ptype 
        self.strcolor = strcolor
        self.rank = rank 
        self.file = file    
        self.isMoving = False 
        self.isAlive = True

        self.image = QIcon(f'{self.strcolor}_{self.ptype}-removebg-preview.png')  
        self.position_convention = [self.file, self.rank]  
        self.position_numeric = [(list(string.ascii_lowercase).index(self.file)+1), self.rank]         

        self.allowMovement = 0
    

        for sqr in Ui_MainWindow.boardSquare_list:
            if self.position_convention[0] == sqr.coordinate[0] and self.position_convention[1] == sqr.coordinate[1]:
                sqr.piece_color = self.strcolor

        global add_piece
        add_piece = Pieces(self.color, self.strcolor, self) 

        if type(self).__name__ == "King" or type(self).__name__ == "Rook": 
            self.firstMove = False  
            self.starting_position = self.position_numeric


    def areaCovered(self):  
        self.area_covered = [
            [self.position_numeric[0]+1, self.position_numeric[1]],
            [self.position_numeric[0]-1, self.position_numeric[1]], 
            [self.position_numeric[0], self.position_numeric[1]+1],
            [self.position_numeric[0], self.position_numeric[1]-1], 
            [self.position_numeric[0]+1, self.position_numeric[1]+1], 
            [self.position_numeric[0]+1, self.position_numeric[1]-1], 
            [self.position_numeric[0]-1, self.position_numeric[1]+1], 
            [self.position_numeric[0]- 1, self.position_numeric[1]-1]
        ]  

        # Castle setup 
        if not self.firstMove and self.position_numeric == self.starting_position and not self.inCheck(): 
            self.area_covered.append([self.position_numeric[0]+2, self.position_numeric[1]]) 
            self.area_covered.append([self.position_numeric[0]-2, self.position_numeric[1]])

            for rook in Pieces.pieces:
                if rook.ptype == "Rook" and rook.strcolor == self.strcolor and rook.firstMove: 
                    if abs(self.position_numeric[0]-rook.starting_position[0]) == 3: 
                        self.area_covered.remove([self.position_numeric[0]-2, self.position_numeric[1]])
                    if abs(self.position_numeric[0]-rook.starting_position[0]) == 2: 
                        self.area_covered.append([self.position_numeric[0]+2, self.position_numeric[1]])                        
 
        for plyr in Player.player_list:
            if not plyr.isMyTurn: 
                try:   
                    if self.strcolor == plyr.color and not king_clicked_mode:
                        for sqr in Ui_MainWindow.boardSquare_list:
                            for area in self.area_covered: 
                                try:
                                    if area == [sqr.coordinate[2], sqr.coordinate[1]] and sqr.isOccupied and sqr.piece_color == self.strcolor:
                                        self.area_covered.remove(area)  
                                except: 
                                    pass
                except:
                    pass
        self.area_covered = list(filter(lambda x : x[0] <= 8 and x[0] >= 1 and x[1] <= 8 and x[1] >= 1, self.area_covered))                      

        return self.area_covered 

    def show_area_covered(self):
        for sqr in Ui_MainWindow.boardSquare_list:
            for occupied in self.area_covered:
                if occupied[0] ==  sqr.coordinate[2] and occupied[1] == sqr.coordinate[1]:
                    if sqr.isOccupied:
                        sqr.squares.setEnabled(True)
                        continue                    
                    sqr.squares.setIcon(QIcon("area_cover.png")) 
                    sqr.squares.setIconSize(QSize(40, 40))  


    def inCheck(self):
        if self.ptype != "King":
            return
        checking = 0
        try:
            for attacker in Pieces.pieces:
                if attacker.strcolor != self.strcolor and attacker != self: 
                    for invaded in attacker.area_covered: 
                        if self.position_numeric == invaded: 
                            self.is_inCheck = True 
                            checking += 1  
                        else:
                            continue 
        except: 
            pass

        if checking < 1:
            self.is_inCheck = False 

     
        backup = [x for x in self.area_covered]  
        try:
            for atkr in Pieces.pieces:  
                atk_backup = [y for y in atkr.area_covered]
                if atkr.strcolor != self.strcolor: 
                    for escape in backup: 
                        if escape in atk_backup:
                            self.area_covered.remove(escape)      
        except:
            pass

        return self.is_inCheck  


class Queen(King): 
    def __init__(self, color, strcolor,ptype, rank, file):
        King.__init__(self, color, strcolor,ptype, rank, file)     
        self.second_checker = False
        self.tester2 = 0 
        self.pinned = False 
        self.allowMovement = 0

    def restriction(self): 
        self.direction_list = [] 

        try:
            Pieces.LimitDown_Movement(self)
            Pieces.LimitUp_Movement(self)
            Pieces.LimitLeft_Movement(self)
            Pieces.LimitRight_Movement(self)
            Pieces.LimitRightUp_Movement(self)
            Pieces.LimitRightDown_Movement(self)
            Pieces.LimitLeftUp_Movement(self)
            Pieces.LimitLeftDown_Movement(self)     
        except: 
            pass

        self.direction_list.append(Pieces.LimitDown_Movement(self))
        self.direction_list.append(Pieces.LimitLeft_Movement(self))
        self.direction_list.append(Pieces.LimitRight_Movement(self))
        self.direction_list.append(Pieces.LimitUp_Movement(self)) 
        self.direction_list.append(Pieces.LimitRightDown_Movement(self))
        self.direction_list.append(Pieces.LimitRightUp_Movement(self))
        self.direction_list.append(Pieces.LimitLeftUp_Movement(self))
        self.direction_list.append(Pieces.LimitLeftDown_Movement(self))

        return self.area_covered

    def areaCovered(self):  
        self.area_covered = [
        ]   

        up, down, left, right = 1,1,1,1
        for atk in range(8):
            self.area_covered.append([self.position_numeric[0]+up, self.position_numeric[1]]) 
            self.area_covered.append([self.position_numeric[0]-down, self.position_numeric[1]]) 
            self.area_covered.append([self.position_numeric[0], self.position_numeric[1]+right])
            self.area_covered.append([self.position_numeric[0], self.position_numeric[1]-left]) 
            self.area_covered.append([self.position_numeric[0]+up, self.position_numeric[1]+right])
            self.area_covered.append([self.position_numeric[0]+up, self.position_numeric[1]-left])
            self.area_covered.append([self.position_numeric[0]-down, self.position_numeric[1]+right]) 
            self.area_covered.append([self.position_numeric[0]-down, self.position_numeric[1]-left])
 
        

            up += 1
            down += 1 
            right += 1
            left += 1   


        self.restriction()  
        
        self.area_covered = list(filter(lambda x : x[0] <= 8 and x[0] >= 1 and x[1] <= 8 and x[1] >= 1, self.area_covered))    

        return self.area_covered  

           
class Rook(King):
    def __init__(self, color, strcolor, ptype, rank, file):
        King.__init__(self, color, strcolor,ptype, rank, file)   
        self.second_checker = False 
        self.tester2 = 0  
        self.pin = False
        self.allowMovement = 0

    def restriction(self): 
        self.direction_list = []

        try:
            Pieces.LimitDown_Movement(self)
            Pieces.LimitLeft_Movement(self)
            Pieces.LimitRight_Movement(self)
            Pieces.LimitUp_Movement(self)    
        except: 
            pass

        self.direction_list.append(Pieces.LimitDown_Movement(self))
        self.direction_list.append(Pieces.LimitLeft_Movement(self))
        self.direction_list.append(Pieces.LimitRight_Movement(self))
        self.direction_list.append(Pieces.LimitUp_Movement(self))


    def areaCovered(self):
        self.area_covered = [] 

        up, down, left, right = 1,1,1,1
        for atk in range(8):
            self.area_covered.append([self.position_numeric[0]+up, self.position_numeric[1]]) 
            self.area_covered.append([self.position_numeric[0]-down, self.position_numeric[1]]) 
            self.area_covered.append([self.position_numeric[0], self.position_numeric[1]+right])
            self.area_covered.append([self.position_numeric[0], self.position_numeric[1]-left]) 

            up += 1
            down += 1 
            right += 1
            left += 1   

        self.restriction()

        self.area_covered = list(filter(lambda x : x[0] <= 8 and x[0] >= 1 and x[1] <= 8 and x[1] >= 1, self.area_covered)) 

        return self.area_covered  



            


class Bishop(King):
    def __init__(self, color, strcolor, ptype, rank, file): 
        King.__init__(self, color, strcolor,ptype, rank, file)   
        self.second_checker = False
        self.tester2 = 0 
        self.pin = False
        self.allowMovement = 0

    def restriction(self):  
        self.direction_list = [] 

        try:
            Pieces.LimitRightDown_Movement(self)
            Pieces.LimitRightUp_Movement(self)
            Pieces.LimitLeftUp_Movement(self)
            Pieces.LimitLeftDown_Movement(self)   
        except: 
            pass

        self.direction_list.append(Pieces.LimitRightDown_Movement(self))
        self.direction_list.append(Pieces.LimitRightUp_Movement(self))
        self.direction_list.append(Pieces.LimitLeftUp_Movement(self))
        self.direction_list.append(Pieces.LimitLeftDown_Movement(self))


    def areaCovered(self):  
        self.area_covered = [] 

        up, down, left, right = 1,1,1,1
        for atk in range(8):
            self.area_covered.append([self.position_numeric[0]+up, self.position_numeric[1]+right])
            self.area_covered.append([self.position_numeric[0]+up, self.position_numeric[1]-left])
            self.area_covered.append([self.position_numeric[0]-down, self.position_numeric[1]+right]) 
            self.area_covered.append([self.position_numeric[0]-down, self.position_numeric[1]-left])

            up += 1
            down += 1 
            right += 1  
            left += 1

        self.restriction()

        self.area_covered = list(filter(lambda x : x[0] <= 8 and x[0] >= 1 and x[1] <= 8 and x[1] >= 1, self.area_covered))

        return self.area_covered



class Knight(King):
    def __init__(self, color, strcolor, ptype, rank, file):
        King.__init__(self, color, strcolor,ptype, rank, file)    
        self.second_checker = False
        self.tester2 = 0 
        self.pin = False
        self.allowMovement = 0

    def areaCovered(self):  

        self.area_covered = [
            [self.position_numeric[0]+2, self.position_numeric[1]+1], 
            [self.position_numeric[0]+2, self.position_numeric[1]-1],
            [self.position_numeric[0]-2, self.position_numeric[1]+1],
            [self.position_numeric[0]-2, self.position_numeric[1]-1], 
            [self.position_numeric[0]+1, self.position_numeric[1]+2], 
            [self.position_numeric[0]-1, self.position_numeric[1]+2],
            [self.position_numeric[0]+1, self.position_numeric[1]-2], 
            [self.position_numeric[0]-1, self.position_numeric[1]-2]
        ]  
    
        for check_sqr in Ui_MainWindow.boardSquare_list: 
            try:
                if check_sqr.isOccupied and not king_clicked_mode: 
                        for glob_pieces in Pieces.pieces: 
                            if glob_pieces == self:
                                continue 
                            if glob_pieces.strcolor == self.strcolor:
                                self.area_covered.remove(glob_pieces.position_numeric)
            except:
                pass   

        self.area_covered = list(filter(lambda x : x[0] <= 8 and x[0] >= 1 and x[1] <= 8 and x[1] >= 1, self.area_covered))
 
 
        return self.area_covered 


class Pawn(King):
    def __init__(self, color, strcolor, ptype, rank, file):
        King.__init__(self, color, strcolor,ptype, rank, file) 
        self.firstmove = True   
        self.tester2 = 0 
        self.pin = False 
        self.allowMovement = 0 
        self.en_passantable = 0 
        self.reject_enpassant = 0
        self.starting_position = self.position_numeric


    def areaCovered(self):  
        if self.strcolor == 'White':
            self.area_covered = [
                [self.position_numeric[0], self.position_numeric[1]+1]
            ]   
            if self.firstmove: 
                for sqr in Ui_MainWindow.boardSquare_list:
                    try:
                        if [sqr.coordinate[2], sqr.coordinate[1]] == [self.position_numeric[0], self.position_numeric[1]+1]:
                            if sqr.isOccupied:
                                break
                            self.area_covered.append([self.position_numeric[0], self.position_numeric[1]+2]) 
                            break
                    except: 
                        pass 
            
            try:
                for atk in Ui_MainWindow.boardSquare_list:
                    if atk.isOccupied and atk.piece_color != self.strcolor:
                        if [atk.coordinate[2], atk.coordinate[1]] == [self.position_numeric[0]+1, self.position_numeric[1]+1]:
                            self.area_covered.append([atk.coordinate[2], atk.coordinate[1]]) 
                        if [atk.coordinate[2], atk.coordinate[1]] == [self.position_numeric[0]-1, self.position_numeric[1]+1]: 
                            self.area_covered.append([atk.coordinate[2], atk.coordinate[1]])   
            except: 
                pass

            try:
                if not self.isMoving:
                    self.area_covered.append([self.position_numeric[0]+1, self.position_numeric[1]+1])  
                    self.area_covered.append([self.position_numeric[0]-1, self.position_numeric[1]+1]) 
                    self.area_covered.remove([self.position_numeric[0], self.position_numeric[1]+1])   
                    self.area_covered.remove([self.position_numeric[0], self.position_numeric[1]+2])  
                else:
                    for atk in Ui_MainWindow.boardSquare_list:
                        if not atk.isOccupied and atk.piece_color != self.strcolor:
                            if [atk.coordinate[2], atk.coordinate[1]] == [self.position_numeric[0]+1, self.position_numeric[1]+1]:
                                self.area_covered.remove([atk.coordinate[2], atk.coordinate[1]]) 
                            if [atk.coordinate[2], atk.coordinate[1]] == [self.position_numeric[0]-1, self.position_numeric[1]+1]: 
                                self.area_covered.remove([atk.coordinate[2], atk.coordinate[1]]) 
            except:
                pass

            try:
                for sqr in Ui_MainWindow.boardSquare_list:
                    if sqr.isOccupied:
                        if [self.position_numeric[0], self.position_numeric[1]+1] == [sqr.coordinate[2], sqr.coordinate[1]]:
                            self.area_covered.remove([self.position_numeric[0], self.position_numeric[1]+1])
                        if [self.position_numeric[0], self.position_numeric[1]+2] == [sqr.coordinate[2], sqr.coordinate[1]]:
                            self.area_covered.remove([self.position_numeric[0], self.position_numeric[1]+2])       
            except:
                pass   


        else: 
            self.area_covered = [
                [self.position_numeric[0], self.position_numeric[1]-1]
            ]  

            if self.firstmove: 
                for sqr in Ui_MainWindow.boardSquare_list: 
                    try:
                        if [sqr.coordinate[2], sqr.coordinate[1]] == [self.position_numeric[0], self.position_numeric[1]-1]:
                            if sqr.isOccupied:
                                break
                            self.area_covered.append([self.position_numeric[0], self.position_numeric[1]-2]) 
                            break
                    except: 
                        pass 

            try:
                for atk in Ui_MainWindow.boardSquare_list:
                    if atk.isOccupied and atk.piece_color != self.strcolor:
                        if [atk.coordinate[2], atk.coordinate[1]] == [self.position_numeric[0]+1, self.position_numeric[1]-1]:
                            self.area_covered.append([atk.coordinate[2], atk.coordinate[1]]) 
                        if [atk.coordinate[2], atk.coordinate[1]] == [self.position_numeric[0]-1, self.position_numeric[1]-1]: 
                            self.area_covered.append([atk.coordinate[2], atk.coordinate[1]])  
            except: 
                pass 

            try:    
                if not self.isMoving:
                    self.area_covered.append([self.position_numeric[0]+1, self.position_numeric[1]-1])  
                    self.area_covered.append([self.position_numeric[0]-1, self.position_numeric[1]-1])                      
                    self.area_covered.remove([self.position_numeric[0], self.position_numeric[1]-1])   
                    self.area_covered.remove([self.position_numeric[0], self.position_numeric[1]-2])   
                else:
                    for atk in Ui_MainWindow.boardSquare_list:
                        if not atk.isOccupied and atk.piece_color != self.strcolor:
                            if [atk.coordinate[2], atk.coordinate[1]] == [self.position_numeric[0]+1, self.position_numeric[1]-1]:
                                self.area_covered.remove([atk.coordinate[2], atk.coordinate[1]]) 
                            if [atk.coordinate[2], atk.coordinate[1]] == [self.position_numeric[0]-1, self.position_numeric[1]-1]: 
                                self.area_covered.remove([atk.coordinate[2], atk.coordinate[1]])                     
            except:
                pass
 
            try:
                for sqr in Ui_MainWindow.boardSquare_list:
                    if sqr.isOccupied:
                        if [self.position_numeric[0], self.position_numeric[1]-1] == [sqr.coordinate[2], sqr.coordinate[1]]:
                            self.area_covered.remove([self.position_numeric[0], self.position_numeric[1]-1])
                        if [self.position_numeric[0], self.position_numeric[1]-2] == [sqr.coordinate[2], sqr.coordinate[1]]:
                            self.area_covered.remove([self.position_numeric[0], self.position_numeric[1]-2])    
            except:
                pass     
        
    
        for check_sqr in Ui_MainWindow.boardSquare_list: 
            if check_sqr.isOccupied: 
                try:
                    for glob_pieces in Pieces.pieces: 
                        if glob_pieces == self:
                            continue 
                        if glob_pieces.strcolor == self.strcolor:
                            self.area_covered.remove(glob_pieces.position_numeric)
                except:
                    pass 
        self.area_covered = list(filter(lambda x : x[0] <= 8 and x[0] >= 1 and x[1] <= 8 and x[1] >= 1, self.area_covered))  

    
        return self.area_covered 


