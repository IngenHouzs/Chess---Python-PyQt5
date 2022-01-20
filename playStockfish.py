from sys import set_coroutine_origin_tracking_depth
from chess import Piece
from setuptools import setup
import stockfish
import setupUI

# Special file to implement bot (Stockfish to the function)

checkmate_verificate = False
class BOT_Stockfish:
    disable_clockSwitch = 0
    def __init__(self, elo_rating, play_as):
        self.stockfish_engine = stockfish.Stockfish(path=r'D:\Programming\Projects\PYTHON\Chess PyQt5 Project\stockfish_14.1_win_x64_avx2\stockfish_14.1_win_x64_avx2.exe')
        self.elo_rating = elo_rating 
        self.play_as = play_as 

        self.stockfish_engine.set_elo_rating(self.elo_rating)

    def make_movement(self): 
        self.stockfish_engine.set_fen_position(setupUI.Pieces.fen_notation)
        best_move = self.stockfish_engine.get_best_move() 
        try:
            self.pre_move = [best_move[0], int(best_move[1])]
            self.post_move = [best_move[2], int(best_move[3])]
            try:
                self.promotion_move = str(best_move[4])
            except: 
                pass
        except: 
            checkmate_verificate = True




    def execute_movement(self): 
        if not setupUI.Board.push_botMovement:
            return
        setupUI.Board.enable_findBotMovement = False

        for sqr in setupUI.Ui_MainWindow.boardSquare_list:
            if [sqr.coordinate[0], sqr.coordinate[1]] == self.pre_move: 
                for pc in setupUI.Pieces.pieces:
                    if pc.strcolor == self.play_as: 
                        pc.isMoving = True 
                    else: 
                        pc.isMoving = False
                sqr.squareClicked(True)           
                              
        for sqr in setupUI.Ui_MainWindow.boardSquare_list:
            if [sqr.coordinate[0], sqr.coordinate[1]] == self.post_move: 
                for pc in setupUI.Pieces.pieces:
                    if pc.strcolor == self.play_as: 
                        pc.isMoving = True 
                    else: 
                        pc.isMoving = False             
                sqr.squareClicked(True) 
            
        setupUI.Board.enable_findBotMovement = True
        setupUI.Board.push_botMovement = False

