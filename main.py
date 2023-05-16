import sys
from typing import NamedTuple
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QPushButton, QSizePolicy, QVBoxLayout,QHBoxLayout,QSpacerItem, QLabel,QMenu,QSplitter,QGroupBox,QLineEdit
from PyQt6.QtCore import Qt
import random
#main code for the game
class Vector(NamedTuple):
    row: int
    col: int



class MoveOption():
    def __init__(self, name):
        self.name = name
        self.PossibleMoves = []
    def AddToPossibleMoves(self, move: Vector):
        self.PossibleMoves.append(move)
    def GetName(self):
        return self.name
    def CheckIfThereIsAMoveToSquare(self, startSquareReference : Vector, FisnishSquareReference: Vector) -> bool:
        
        for move in self.PossibleMoves:
            if ( (startSquareReference.row + move.row) == FisnishSquareReference.row and (startSquareReference.col + move.col) == FisnishSquareReference.col):
                return True
            
        return False
        

class MoveOptionQueue():
    def __init__(self):
        self.queue = []
    def GetQueueAsString(self) -> str:
        queue = ""
        for move in self.queue:
            queue += move.GetName() + ", "
        return queue
    def Add(self, move: MoveOption):
        self.queue.append(move)
    def Replace( self, move: MoveOption, index: int):
        self.queue[index] = move
    def MoveItemToBack(self, index: int):
        self.queue.append(self.queue.pop(index))
    def GetMoveOptionInPosition(self, index: int) -> MoveOption:
        return self.queue[index]
        

class Player():
    def __init__(self, name,direction):
        self.score = 100
        self.name = name
        self.direction = direction
        self.moveOptionsQueue = MoveOptionQueue()

    def SameAs(self, otherPlayer: 'Player'):
        if otherPlayer == None:
            return False
        
        return self.name == otherPlayer.name
    def GetPlayerQueueAsString(self) -> str:
        return self.moveOptionsQueue.GetQueueAsString()
    def AddMoveOptionToQueue(self, moveOption: MoveOption):
        self.moveOptionsQueue.Add(moveOption)
    def UpdatePlayerMoveQueue(self, moveOption: MoveOption, index: int):
        self.moveOptionsQueue.MoveItemToBack(moveOption, index)
    def UpdateQueueAfterMove(self, index: int):
        self.moveOptionsQueue.MoveItemToBack(index-1)
    def UpdateMoveOptionQueueWithOffer(self, index: int, moveOption: MoveOption):
        self.moveOptionsQueue.Replace(moveOption,index)
    def ChangeScore(self, change: int):
        self.score += change
    def CheckPlayerMove(self,pos:int, startSquareReference : Vector, FisnishSquareReference: Vector) -> bool:
        temp = self.moveOptionsQueue.GetMoveOptionInPosition(pos-1)
        return temp.CheckIfThereIsAMoveToSquare(startSquareReference, FisnishSquareReference)
    

class Piece():
    def __init__(self, typeOfPiece: str, players: Player, points: int, Symbol: str):
        self.TypeOfPiece = typeOfPiece
        self.BelongsTo = players
        self.PointsIfCaptured = points
        self.Symbol = Symbol

class Square():
    def __init__(self):
        self.Symbol = " "
        self.PieceInSquare = None
        self.BelongsTo = None
    def SetPiece(self, piece: Piece):
        self.PieceInSquare = piece
    def RemovePiece(self) -> Piece:
        PieceToReturn = self.PieceInSquare
        self.PieceInSquare = None
        return PieceToReturn
    def GetPiontsForOccupancy(self,player:Player):
        return 0
    def ContainsKotla(self):
        if (self.Symbol == "K" or self.Symbol == "k"):
            return True
        return False
    
class Kotla(Square):
    def __init__(self,player:Player, symbol:str):        
        self.Symbol = symbol
        self.PieceInSquare = None
        self.BelongsTo = player
    def GetPiontsForOccupancy(self,currentPlayer:Player):
        if (self.PieceInSquare == None):
            return 0
        if (self.PieceInSquare.BelongsTo.SameAs(currentPlayer)):
            if currentPlayer.SameAs(self.PieceInSquare.BelongsTo) and self.PieceInSquare.TypeOfPiece  in ["piece","mirza"]:
                return 5
            else:
                return 0
        else:
            if currentPlayer.SameAs(self.PieceInSquare.BelongsTo) and self.PieceInSquare.TypeOfPiece  in ["piece","mirza"]:
                return 1
            else:
                return 0

                




class GridButtons(QWidget):
    def __init__(self, grid,noOfPieces):
        super().__init__()
        self.width = 1200
        self.height = 1600
        self.grid = grid
        self.initUI()
        self.Dastan(noOfPieces)
        self.PlayGame()


    def initUI(self):
        self.resize(self.width, self.height)
        # Create the grid layout
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setSpacing(10)
        for row in range(len(self.grid)):
            for col in range(len(self.grid[0])):
                button = QPushButton(str(self.grid[row][col]))
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                button.clicked.connect(lambda state, row=row, col=col: self.on_button_clicked(row, col))
                self.gridLayout.addWidget(button, row, col)

        # Create the right menu
        rightMenu = QVBoxLayout()
        # Create the score
        scoreMenu =QHBoxLayout()
        scoreLableOne = QLabel('Player one score:', self)
        self.scorePlayerOne = QLineEdit(self, readOnly=True)
        scoreLableTwo = QLabel('Player two score:', self)
        self.scorePlayerTwo = QLineEdit(self, readOnly=True)
        scoreMenu.addWidget(scoreLableOne)
        scoreMenu.addWidget(self.scorePlayerOne)
        scoreMenu.addWidget(scoreLableTwo)
        scoreMenu.addWidget(self.scorePlayerTwo)
        rightMenu.addLayout(scoreMenu)
        #output textbox
        self.mainOutput = QLineEdit(self, readOnly=True)
        rightMenu.addWidget(self.mainOutput)
        
        
        #move options
        moveMenu = QVBoxLayout()    
        #offer move button 
        self.offerMove = QPushButton('Offer move', self)
        self.offerMove.setToolTip('take offered move and repace with a move in your queue')
        self.offerMove.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Create the menu
        self.index_menu = QMenu()
        for i in range (1,6):
            self.index_menu.addAction("Add At Position: "+str(i))
            self.index_menu.actions()[i-1].triggered.connect(lambda idk, x=i: self.computerOfferMove(x))         
        # Connect the main button to the menu
        self.offerMove.setMenu(self.index_menu)
        #other buttons    
        self.MoveOneButton = QPushButton('Move 1', self)
        self.MoveOneButton.setToolTip('take first move from queue (-1 points)')
        self.MoveOneButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.MoveOneButton.clicked.connect(self.computerMoveOne)
        self.MoveTwoButton = QPushButton('Move 2', self)
        self.MoveTwoButton.setToolTip('take second move from queue (-4 points)')
        self.MoveTwoButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.MoveTwoButton.clicked.connect(self.computerMoveTwo)
        self.MoveThreeButton = QPushButton('Move 3', self)
        self.MoveThreeButton.setToolTip('take third move from queue (-7 points)')
        self.MoveThreeButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.MoveThreeButton.clicked.connect(self.computerMoveThree)
        moveMenu.addWidget(self.offerMove)
        moveMenu.addWidget(self.MoveOneButton)
        moveMenu.addWidget(self.MoveTwoButton)
        moveMenu.addWidget(self.MoveThreeButton)
        rightMenu.addLayout(moveMenu)
        # add the queue of moves
        queueMenu = QHBoxLayout()
        queueLable = QLabel('Queue:', self)
        self.queue = QLineEdit(self, readOnly=True)
        queueMenu.addWidget(queueLable)
        queueMenu.addWidget(self.queue)
        rightMenu.addLayout(queueMenu)


        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        rightMenu.addSpacerItem(spacer)

        # Create Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.addWidget(QGroupBox("Board", self))
        self.splitter.addWidget(QGroupBox("Controls", self))
        self.splitter.setSizes([int(self.width * 2/3), int(self.width * 1/3)])
        self.splitter.widget(0).setLayout(self.gridLayout)
        self.splitter.widget(1).setLayout(rightMenu)


        # Set main layout to the splitter
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.splitter)

        self.setLayout(vbox)

    def on_button_clicked(self, row, col):
        if self.gameStep == "start square":
            self.StartSquare = Vector(row,col)
            #check if valid start square
            if self.CheckSquareIsValid(self.StartSquare,True):
                self.UpdateGameState("end square")
        elif self.gameStep == "end square":
            self.EndSquare = Vector(row,col)
            #finish computing the move
            if self.CheckSquareIsValid(self.EndSquare,False):
                self.ComputeTurn()

    def computerOfferMove(self,index: int):
        
        if self.gameStep == "choose move":
            #update queue
            self.CurrentPlayer.UpdateMoveOptionQueueWithOffer(index-1,self.CreateMoveOption(self.MoveOptionOffer[self.MoveOptionOfferPosition],self.CurrentPlayer.direction))
            #remove score
            self.CurrentPlayer.ChangeScore(-(10 - (index * 2)))    
            self.scorePlayerOne.setText(str(self.Players[0].score))
            self.scorePlayerTwo.setText(str(self.Players[1].score))
            #refresh index
            self.MoveOptionOfferPosition = random.randint(0,4)
            self.offerMove.setText("Offer Move: "+self.MoveOptionOffer[self.MoveOptionOfferPosition])
            self.queue.setText(self.CurrentPlayer.GetPlayerQueueAsString())
            self.MoveOneButton.setText(self.CurrentPlayer.moveOptionsQueue.GetMoveOptionInPosition(0).GetName())
            self.MoveTwoButton.setText(self.CurrentPlayer.moveOptionsQueue.GetMoveOptionInPosition(1).GetName())
            self.MoveThreeButton.setText(self.CurrentPlayer.moveOptionsQueue.GetMoveOptionInPosition(2).GetName())
    def computerMoveOne(self):
        if self.gameStep == "choose move":
            self.Choice = 1
            self.UpdateGameState("start square")
    def computerMoveTwo(self):
        if self.gameStep == "choose move":
            self.Choice = 2
            self.UpdateGameState("start square")
    def computerMoveThree(self):
        if self.gameStep == "choose move":
            self.Choice = 3
            self.UpdateGameState("start square")

    def Dastan(self, noOfPieces):
        self.Players = [Player('Player One', 1), Player('Player Two', -1)]
        self.CreateMoveOptions()
        self.CreateMoveOptionOffer()
        self.MoveOptionOfferPosition = random.randint(0,4)
        self.offerMove.setText("Offer Move: "+self.MoveOptionOffer[self.MoveOptionOfferPosition])
        self.CreateBoard()
        self.CreatePieces(noOfPieces)
        self.CurrentPlayer = self.Players[0]

    def PlayGame(self):
        self.gameOver = False
        #update score value in GUI
        self.scorePlayerOne.setText(str(self.Players[0].score))
        self.scorePlayerTwo.setText(str(self.Players[1].score))

        
        self.UpdateGameState("choose move")
        
        self.DisplayState()
    def UpdateGameState(self,newState):
        match newState:
            case "choose move":
                self.gameStep = "choose move"
                self.mainOutput.setText(self.CurrentPlayer.name +": Choose a move")
                #update move options in GUI
                self.queue.setText(self.CurrentPlayer.GetPlayerQueueAsString())
                self.MoveOneButton.setText(self.CurrentPlayer.moveOptionsQueue.GetMoveOptionInPosition(0).GetName())
                self.MoveTwoButton.setText(self.CurrentPlayer.moveOptionsQueue.GetMoveOptionInPosition(1).GetName())
                self.MoveThreeButton.setText(self.CurrentPlayer.moveOptionsQueue.GetMoveOptionInPosition(2).GetName())
                self.MoveOneButton.setEnabled(True)
                self.MoveTwoButton.setEnabled(True)
                self.MoveThreeButton.setEnabled(True)
                self.offerMove.setEnabled(True)
            case "start square":                
                self.gameStep = "start square"
                self.mainOutput.setText(self.CurrentPlayer.name +": Choose a start square")
                self.MoveOneButton.setEnabled(False)
                self.MoveTwoButton.setEnabled(False)
                self.MoveThreeButton.setEnabled(False)
                self.offerMove.setEnabled(False)
            case "end square":
                self.gameStep = "end square"
                self.mainOutput.setText(self.CurrentPlayer.name +": Choose an end square")
                self.DisplayStateWithMoves(self.StartSquare, self.Choice, self.CurrentPlayer)
            case "done":
                self.gameStep = "done"
                self.DisplayFinalScore()

    def ComputeTurn(self):
            moveLegal = self.CurrentPlayer.CheckPlayerMove(self.Choice, self.StartSquare, self.EndSquare)
            if moveLegal == True:
                pointsForCapture = self.CalculatePieceCapturePoints(self.EndSquare)
                self.CurrentPlayer.ChangeScore(-(self.Choice +(2 * (self.Choice -1))))
                self.CurrentPlayer.UpdateQueueAfterMove(self.Choice)
                self.UpdateBoard(self.StartSquare, self.EndSquare)
                self.UpdatePlayerScore(pointsForCapture)
                #update score value in GUI
                self.scorePlayerOne.setText(str(self.Players[0].score))
                self.scorePlayerTwo.setText(str(self.Players[1].score))



            
            #swich players
            if self.CurrentPlayer == self.Players[0]:
                self.CurrentPlayer = self.Players[1]
            else:
                self.CurrentPlayer = self.Players[0]
            #start next turn if game is not over
            self.UpdateGameState("choose move")
            self.DisplayState()
            #check if game is over
            self.gameOver = self.CheckForGameOver()
            if self.gameOver == True:
                self.UpdateGameState("done")

    def UpdateBoard(self, startSquare: Vector, endSquare: Vector):
        startSquareIndex = self.GetIndexOfSquareVec(startSquare)
        endSquareIndex = self.GetIndexOfSquareVec(endSquare)
        self.Board[endSquareIndex].SetPiece(self.Board[startSquareIndex].RemovePiece())

        

    def UpdatePlayerScore(self, pointsForCapture: int):
        self.CurrentPlayer.ChangeScore(pointsForCapture)
        self.CurrentPlayer.ChangeScore(self.GetPointsForOccupancyByPlayer(self.CurrentPlayer))
    
    def GetPointsForOccupancyByPlayer(self, player: Player) -> int:
        points = 0
        for square in self.Board:
            points += square.GetPiontsForOccupancy(player)
        return points
        
    def CheckSquareIsValid(self, squareReference: Vector, isStartSquare: bool) -> bool:
        #would check if in bounds

        piece = self.Board[self.GetIndexOfSquareVec(squareReference)].PieceInSquare
        if piece == None:
            if (isStartSquare):
                return False
            else:
                return True
        elif piece.BelongsTo.SameAs(self.CurrentPlayer):
            if (isStartSquare):
                return True
            else:
                return False
        else:
            if (isStartSquare):
                return False
            else:
                return True
    def CalculatePieceCapturePoints(self, endSquareReference: Vector) -> int:
        endSquare = self.Board[self.GetIndexOfSquareVec(endSquareReference)]
        if endSquare.PieceInSquare == None:
            return 0
        else:
            return endSquare.PieceInSquare.PointsIfCaptured
    def CheckForGameOver(self):
        playerOneHasMirza = False
        playerTwoHasMirza = False
        for square in self.Board:
            if square.PieceInSquare != None:
                if square.ContainsKotla() and square.PieceInSquare.TypeOfPiece == "mirza" and not(square.PieceInSquare.BelongsTo.SameAs(square.BelongsTo)):
                    return True
                elif square.PieceInSquare.TypeOfPiece == "mirza" and square.PieceInSquare.BelongsTo.SameAs(self.Players[0]):
                    playerOneHasMirza = True
                elif square.PieceInSquare.TypeOfPiece == "mirza" and square.PieceInSquare.BelongsTo.SameAs(self.Players[1]):
                    playerTwoHasMirza = True
        return not ( playerOneHasMirza and playerTwoHasMirza)

    def DisplayFinalScore(self):
        if self.Players[0].score == self.Players[1].score:
            self.mainOutput.setText("Draw!")
        elif self.Players[0].score > self.Players[1].score:
            self.mainOutput.setText(self.Players[0].name + " is the winner!")
        else:
            self.mainOutput.setText(self.Players[1].name + " is the winner!")

    
    def DisplayState(self):
        boardIndex = 0
        for row in range(len(self.grid)):
            for col in range(len(self.grid[0])):                
                button = self.gridLayout.itemAtPosition(row, col).widget()
                text = self.Board[boardIndex].Symbol
                if self.Board[boardIndex].PieceInSquare != None:
                    text += self.Board[boardIndex].PieceInSquare.Symbol
                    
                button.setText(text)
                boardIndex += 1
    def DisplayStateWithMoves(self, startSquare: Vector, Choice: int,CurrentPlayer: Player):
        boardIndex = 0
        for row in range(len(self.grid)):
            for col in range(len(self.grid[0])):                
                button = self.gridLayout.itemAtPosition(row, col).widget()
                text = self.Board[boardIndex].Symbol
                if self.Board[boardIndex].PieceInSquare != None:
                    text += self.Board[boardIndex].PieceInSquare.Symbol
                if CurrentPlayer.CheckPlayerMove(Choice, startSquare, Vector(row,col)) and self.CheckSquareIsValid(Vector(row,col),False):
                    text += "X"
                    
                button.setText(text)
                boardIndex += 1


    def GetIndexOfSquare(self, squareReference) -> int:
        row = squareReference // 10
        col = squareReference % 10
        
        return int((row - 1) * len(self.grid) + col - 1)
    def GetIndexOfSquareVec(self, squareReference:Vector) -> int:
        row = squareReference.row
        col = squareReference.col
        return int((row) * len(self.grid) + col)
        

    def CreatePieces(self, noOfPieces):
        for count in range(0,noOfPieces):
            currentPiece = Piece("piece",self.Players[0],1, "!")
            self.Board[self.GetIndexOfSquare(2 *10 + count + 2)].SetPiece(currentPiece)            
        currentPiece = Piece("mirza",self.Players[0], 5, "1")
        self.Board[self.GetIndexOfSquare(10 + len(self.grid) / 2)].SetPiece(currentPiece)
        for count in range(0,noOfPieces):
            currentPiece = Piece("piece",self.Players[1],1, "\"")
            self.Board[self.GetIndexOfSquare((len(self.grid[0]) - 1) * 10 + count+2)].SetPiece(currentPiece)
        currentPiece = Piece("mirza",self.Players[1], 5, "2")
        self.Board[self.GetIndexOfSquare(len(self.grid[0]) * 10 + (len(self.grid) / 2 + 1))].SetPiece(currentPiece)
        
    def CreateBoard(self):
        self.Board = []
        NoOfRows =len(self.grid)
        NoOfCols = len(self.grid[0])
        
        for row in range(0,NoOfRows):
            for colomb in range(0,NoOfCols):
                if row == 0 and colomb == NoOfCols/2-1:
                    S = Kotla(self.Players[0], "K")
                elif row == NoOfRows-1 and colomb == NoOfCols/2 :
                    S = Kotla(self.Players[1], "k")
                else:
                    S = Square()
                self.Board.append(S)

    def CreateMoveOptionOffer(self):
        self.MoveOptionOffer = []
        self.MoveOptionOffer.append("ryott")
        self.MoveOptionOffer.append("faujdar")
        self.MoveOptionOffer.append("jazair")
        self.MoveOptionOffer.append("cuirassier")
        self.MoveOptionOffer.append("chowkidar")
    def CreateRyottMoveOption(self, direction) ->MoveOption:
        NewMoveOption = MoveOption("ryott")
        NewMoveOption.AddToPossibleMoves(Vector(0, 1 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(0, -1 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(1 * direction, 0))
        NewMoveOption.AddToPossibleMoves(Vector(-1 * direction, 0))
        return NewMoveOption
    def CreateFaujdarMoveOption(self, direction) ->MoveOption:
        NewMoveOption = MoveOption("faujdar")
        NewMoveOption.AddToPossibleMoves(Vector(0, 1 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(0, -1 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(0, 2 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(0, -2 * direction))
        return NewMoveOption
    def CreateJazairMoveOption(self, direction) -> MoveOption:
        NewMoveOption = MoveOption("jazair")
        NewMoveOption.AddToPossibleMoves(Vector(2 * direction, 0))
        NewMoveOption.AddToPossibleMoves(Vector(2 * direction, -2 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(2 * direction, 2 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(0, -2 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(0, 2 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(-1 * direction, -1 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(-1 * direction, 1 * direction))
        return NewMoveOption
    
    def CreateCuirassierMoveOption(self, direction) -> MoveOption:
        NewMoveOption = MoveOption("cuirassier")
        NewMoveOption.AddToPossibleMoves(Vector(1 * direction, 0))
        NewMoveOption.AddToPossibleMoves(Vector(2 * direction, 0))
        NewMoveOption.AddToPossibleMoves(Vector(1 * direction, -2 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(1 * direction, 2 * direction))
        
        return NewMoveOption
    def CreateChowkidarMoveOption(self, direction) -> MoveOption:
        NewMoveOption = MoveOption("chowkidar")
        NewMoveOption.AddToPossibleMoves(Vector(1 * direction, 1 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(1 * direction, -1 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(-1 * direction, 1 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(-1 * direction, -1 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(0, 2 * direction))
        NewMoveOption.AddToPossibleMoves(Vector(0, -2 * direction))        
        
        return NewMoveOption
    
   

    def CreateMoveOption(self, name,direction):
        match name:
            case "ryott":
                return self.CreateRyottMoveOption(direction)
            case "faujdar":
                return self.CreateFaujdarMoveOption(direction)
            case "jazair":
                return self.CreateJazairMoveOption(direction)
            case "cuirassier":
                return self.CreateCuirassierMoveOption(direction)
            case "chowkidar":
                return self.CreateChowkidarMoveOption(direction)
            case _:
                return self.CreateRyottMoveOption(direction)

    def CreateMoveOptions(self):
        self.Players[0].AddMoveOptionToQueue(self.CreateMoveOption("ryott",1))
        self.Players[0].AddMoveOptionToQueue(self.CreateMoveOption("faujdar",1))
        self.Players[0].AddMoveOptionToQueue(self.CreateMoveOption("jazair",1))
        self.Players[0].AddMoveOptionToQueue(self.CreateMoveOption("cuirassier",1))
        self.Players[0].AddMoveOptionToQueue(self.CreateMoveOption("chowkidar",1))
        self.Players[1].AddMoveOptionToQueue(self.CreateMoveOption("ryott",-1))
        self.Players[1].AddMoveOptionToQueue(self.CreateMoveOption("faujdar",-1))
        self.Players[1].AddMoveOptionToQueue(self.CreateMoveOption("jazair",-1))
        self.Players[1].AddMoveOptionToQueue(self.CreateMoveOption("cuirassier",-1))
        self.Players[1].AddMoveOptionToQueue(self.CreateMoveOption("chowkidar",-1))


class MainWindow(QMainWindow):
    def __init__(self, grid):
        super().__init__()
        self.gridButtons = GridButtons(grid,4)
        self.setCentralWidget(self.gridButtons)
        self.setWindowTitle("Dastan")
        self.width = 1200
        self.height = 800
        self.resize(self.width, self.height)



def generate_grid(rows, cols):
    grid = []
    for row in range(rows):
        grid.append([0] * cols)
    return grid

def update_grid(grid_buttons, new_grid):
    grid = grid_buttons.grid
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            grid[row][col] = new_grid[row][col]
            button = grid_buttons.layout().itemAtPosition(row, col).widget()
            button.setText(str(grid[row][col]))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    grid = generate_grid(6,6)
    window = MainWindow(grid)
    window.show()

    sys.exit(app.exec())
