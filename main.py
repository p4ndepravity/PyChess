import sys
import math
import pygame
from pygame.locals import *
from operator import itemgetter


FPS = 30
LEFTBORDER = 100
RIGHTBORDER = 100
TOPBORDER = 40
BOTTOMBORDER = 10
SQUARESIZE = 100
WINDOWWIDTH = (LEFTBORDER * 2) + (SQUARESIZE * 8)
WINDOWHEIGHT = (TOPBORDER + BOTTOMBORDER) + (SQUARESIZE * 8)
BOARDDIMENSIONS = (LEFTBORDER, TOPBORDER, WINDOWWIDTH -
                   (LEFTBORDER * 2), WINDOWHEIGHT - (TOPBORDER + BOTTOMBORDER))
assert BOARDDIMENSIONS[
    2] % SQUARESIZE == 0, "Board width must be a multiple of cell size"
assert BOARDDIMENSIONS[
    3] % SQUARESIZE == 0, "Board height must be a multiple of cell size"
SQUAREWIDTH = 100
SQUAREHEIGHT = 100
BOARDWIDTH = 8
BOARDHEIGHT = 8
assert BOARDHEIGHT == BOARDWIDTH, "Board must be square"
BOARDCOLUMNS = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
BOARDROWS = (8, 7, 6, 5, 4, 3, 2, 1)

WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
GRAY = (100, 100, 100)
LTGRAY = (150, 150, 150)
BGCOLOR = GRAY
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MOUSEOVERCOLOR = RED
SELECTCOLOR = GREEN
MOVESCOLOR = BLUE

WHITESTRING = 'white'
BLACKSTRING = 'black'
ACTIVETEAM = WHITESTRING

PAWN = 'pawn'
PAWNMOVES = ((0, 1), (0, -1), (1, 1), (-1, 1),
             (1, -1), (-1, -1), (0, 2), (0, -2))

ROOK = 'rook'
ROOKMOVES = ((1, 0), (0, 1), (-1, 0), (0, -1), (2, 0), (0, 2), (-2, 0), (0, -2), (3, 0), (0, 3), (-3, 0), (0, -3), (4, 0), (0, 4),
             (-4, 0), (0, -4), (5, 0), (0, 5), (-5, 0), (0, -5), (6, 0), (0, 6), (-6, 0), (0, -6), (7, 0), (0, 7), (-7, 0), (0, -7))
KNIGHT = 'knight'
KNIGHTMOVES = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
               (1, -2), (1, 2), (2, -1), (2, 1))
BISHOP = 'bishop'
BISHOPMOVES = ((1, 1), (1, -1), (-1, 1), (-1, -1), (2, 2), (2, -2), (-2, 2), (-2, -2), (3, 3), (3, -3), (-3, 3), (-3, -3), (4, 4), (4, -4),
               (-4, 4), (-4, -4), (5, 5), (5, -5), (-5, 5), (-5, -5), (6, 6), (6, -6), (-6, 6), (-6, -6), (7, 7), (7, -7), (-7, 7), (-7, -7))
QUEEN = 'queen'
QUEENMOVES = ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (2, 0), (0, 2), (-2, 0), (0, -2), (2, 2), (2, -2), (-2, 2), (-2, -2), (3, 0), (0, 3), (-3, 0), (0, -3), (3, 3), (3, -3), (-3, 3), (-3, -3), (4, 0), (0, 4), (-4, 0), (0, -4),
              (4, 4), (4, -4), (-4, 4), (-4, -4), (5, 0), (0, 5), (-5, 0), (0, -5), (5, 5), (5, -5), (-5, 5), (-5, -5), (6, 0), (0, 6), (-6, 0), (0, -6), (6, 6), (6, -6), (-6, 6), (-6, -6), (7, 0), (0, 7), (-7, 0), (0, -7), (7, 7), (7, -7), (-7, 7), (-7, -7))
KING = 'king'
KINGMOVES = ((-1, -1), (-1, 0), (-1, 1), (0, -1),
             (0, 1), (1, -1), (1, 0), (1, 1))
ALLPIECES = (PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING)


def main():
    global FPSCLOCK, DISPLAYSURF

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('PyChess')
    mousex = 0
    mousey = 0
    playerBlack = Player(BLACK)
    playerWhite = Player(WHITE)
    PLAYERS = (playerBlack, playerWhite)
    selectedSquare = None
    selectedPiece = None
    squareSelected = False
    gameOver = [False, WHITE]
    board = []
    for col in BOARDCOLUMNS:
        board.append([])
        for row in BOARDROWS:
            board[BOARDCOLUMNS.index(col)].append(None)
    validMoves = []

    while True:
        mouseClicked = False
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard()
        drawPieces(playerBlack, playerWhite, board)
        setTitle(PLAYERS, gameOver)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        needRestart = checkForRestart(mousex, mousey, mouseClicked)
        if needRestart:
            playerBlack = Player(BLACK)
            playerWhite = Player(WHITE)
            players = (playerBlack, playerWhite)
            board = []
            for col in BOARDCOLUMNS:
                board.append([])
                for row in BOARDROWS:
                    board[BOARDCOLUMNS.index(col)].append(None)
            continue

        squarex, squarey = getSquareAtPixel(mousex, mousey)
        activeSquare = (squarex, squarey)

        if squarex != None and squarey != None:
            for player in [playerBlack, playerWhite]:
                if player.isMyTurn:
                    for piece in player.pieces:
                        if piece.square == (BOARDCOLUMNS[squarex], BOARDROWS[squarey]):
                            left, top = leftTopCoordsOfSquare(squarex, squarey)
                            pygame.draw.rect(
                                DISPLAYSURF, MOUSEOVERCOLOR, (left, top, SQUARESIZE, SQUARESIZE), 5)
                            if mouseClicked:
                                pygame.draw.rect(
                                    DISPLAYSURF, SELECTCOLOR, (left, top, SQUARESIZE, SQUARESIZE), 5)
                                squareSelected = True
                                selectedSquare = (
                                    BOARDCOLUMNS[squarex], BOARDROWS[squarey])
                                selectedPiece = piece

        if squareSelected:
            left, top = leftTopCoordsOfSquare(
                BOARDCOLUMNS.index(selectedSquare[0]), BOARDROWS.index(selectedSquare[1]))
            pygame.draw.rect(
                DISPLAYSURF, SELECTCOLOR, (left, top, SQUARESIZE, SQUARESIZE), 5)
            validMoves = checkMoves(selectedPiece, board)
            showMoves(validMoves)
            if mouseClicked:
                for move in validMoves:
                    if move == activeSquare:
                        executeMove(activeSquare, selectedPiece,
                                    PLAYERS, board)
                        endTurn(playerBlack, playerWhite)
                        selectedSquare = None
                        selectedPiece = None
                        squareSelected = False
                        activeSquare = None
                        mouseClicked = False
                        gameOver = checkWinConditions(PLAYERS, gameOver)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawBoard():
    pygame.draw.rect(DISPLAYSURF, WHITE, BOARDDIMENSIONS)
    for col in range(len(BOARDCOLUMNS)):
        for row in range(len(BOARDROWS)):
            if (col % 2 == 0 and row % 2 != 0) or (col % 2 != 0 and row % 2 == 0):
                left, top = leftTopCoordsOfSquare(col, row)
                pygame.draw.rect(DISPLAYSURF, LTGRAY, (left,
                                                       top, SQUARESIZE, SQUARESIZE))


def leftTopCoordsOfSquare(squarex, squarey):
    left = squarex * (SQUARESIZE) + (LEFTBORDER)
    top = squarey * (SQUARESIZE) + (TOPBORDER)
    return (left, top)


def getSquareAtPixel(x, y):
    for squarex in range(BOARDWIDTH):
        for squarey in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfSquare(squarex, squarey)
            square = pygame.Rect(left, top, SQUARESIZE, SQUARESIZE)
            if square.collidepoint(x, y):
                return (squarex, squarey)
    return (None, None)


def drawPieces(playerBlack, playerWhite, board):
    for player in [playerBlack, playerWhite]:
        for piece in player.alivePieces:
            image = piece.imageSurf
            squarex, squarey = piece.square
            pieceCoords = leftTopCoordsOfSquare(
                BOARDCOLUMNS.index(squarex), BOARDROWS.index(squarey))
            pieceCoords = (pieceCoords[0] + ((SQUAREWIDTH - image.get_width()) / 2),
                           pieceCoords[1] + ((SQUAREHEIGHT -
                                              image.get_height()) / 2))
            DISPLAYSURF.blit(
                piece.imageSurf, pieceCoords)
            board[BOARDCOLUMNS.index(squarex)][
                BOARDROWS.index(squarey)] = player.color
        for piece in player.deadPieces:
            icon = piece.iconSurf
            if player.color == WHITE:
                DISPLAYSURF.blit(
                    icon, (icon.get_width(), WINDOWHEIGHT - BOTTOMBORDER - (icon.get_height() * (player.deadPieces.index(piece) + 1))))
            else:
                DISPLAYSURF.blit(icon, (WINDOWWIDTH - (icon.get_width() * 2),
                                        TOPBORDER + (icon.get_height() * player.deadPieces.index(piece))))


def checkMoves(piece, board):
    validMoves = []
    invalidSlopes = []
    for move in piece.allowedMoves:
        obstructed = False
        destination = ((BOARDCOLUMNS.index(piece.square[0]) + move[0]),
                       (BOARDROWS.index(piece.square[1]) + move[1]))
        if move[0] == 0:
            if move[1] > 0:
                moveSlope = 'N'
            elif move[1] < 0:
                moveSlope = 'S'
        elif move[0] > 0:
            if move[1] == 0:
                moveSlope = 'E'
            elif move[1] > 0:
                moveSlope = 'SE'
            elif move[1] < 0:
                moveSlope = 'NE'
        elif move[0] < 0:
            if move[1] == 0:
                moveSlope = 'W'
            elif move[1] > 0:
                moveSlope = 'SW'
            elif move[1] < 0:
                moveSlope = 'NW'

        for slope in invalidSlopes:
            if moveSlope == slope:
                obstructed = True
                break

        if not (destination[0] > -1 and destination[0] < 8):
            continue
        elif not (destination[1] > -1 and destination[1] < 8):
            continue

        occupant = board[destination[0]][destination[1]]
        if occupant == piece.color:
            invalidSlopes.append(moveSlope)
            continue

        if piece.name == KNIGHT:
            validMoves.append(destination)
            continue
        elif piece.name == PAWN:
            if piece.hasMoved:
                if abs(move[0]) > 1 or abs(move[1]) > 1:
                    continue
            if piece.color == WHITE and move[1] > 0:
                continue
            elif piece.color == BLACK and move[1] < 0:
                continue

            if move[0] != 0:
                if occupant == None or occupant == piece.color:
                    continue
                else:
                    validMoves.append(destination)
            elif move[0] == 0:
                if obstructed:
                    continue
                else:
                    if occupant != None:
                        invalidSlopes.append(moveSlope)
                    else:
                        validMoves.append(destination)
        else:
            if obstructed:
                continue
            else:
                if occupant != None:
                    validMoves.append(destination)
                    invalidSlopes.append(moveSlope)
                else:
                    validMoves.append(destination)
    return validMoves


def showMoves(validMoves):
    for destination in validMoves:
        left, top = leftTopCoordsOfSquare(destination[0], destination[1])
        pygame.draw.rect(DISPLAYSURF, MOVESCOLOR,
                         (left, top, SQUARESIZE, SQUARESIZE), 5)


def executeMove(destination, piece, players, board):
    enemyPlayer = None
    if board[destination[0]][destination[1]] != None:
        for player in players:
            if board[destination[0]][destination[1]] == player.color:
                enemyPlayer = player
        for enemyPiece in enemyPlayer.pieces:
            if enemyPiece.isAlive:
                if getSquareIndecesFrom(enemyPiece.square) == destination:
                    enemyPiece.kill()
                    enemyPlayer.alivePieces.remove(enemyPiece)
                    enemyPlayer.deadPieces.append(enemyPiece)
                    break

    board[BOARDCOLUMNS.index(piece.square[0])][
        BOARDROWS.index(piece.square[1])] = None
    piece.square = BOARDCOLUMNS[destination[0]], BOARDROWS[destination[1]]
    if piece.name == PAWN:
        piece.hasMoved = True
    board[BOARDCOLUMNS.index(piece.square[0])][
        BOARDROWS.index(piece.square[1])] = piece.color


def endTurn(playerBlack, playerWhite):
    for player in [playerBlack, playerWhite]:
        player.isMyTurn = (not player.isMyTurn)


def setTitle(players, gameOver):
    for player in players:
        if gameOver[0]:
            if gameOver[1] == player.color:
                continue
            else:
                titleFont = pygame.font.Font('freesansbold.ttf', 20)
                titleSurf = titleFont.render(
                    '{} wins! Click here to reset'.format(player.colorString), True, GREEN)
                DISPLAYSURF.blit(titleSurf, (10, 10))
        elif player.isMyTurn:
            titleFont = pygame.font.Font('freesansbold.ttf', 20)
            titleSurf = titleFont.render(
                '{}\'s turn'.format(player.colorString), True, GREEN)
            DISPLAYSURF.blit(titleSurf, (10, 10))


def getSquareIndecesFrom(square):
    squareCoords = (BOARDCOLUMNS.index(square[0]), BOARDROWS.index(square[1]))
    return squareCoords


def checkWinConditions(players, gameOver):
    knightsAlive = 0
    bishopsAlive = 0
    for player in players:
        if player.king.square == None:
            return [True, player.color]
        for pawn in player.pawns:
            if pawn.square != None:
                return (gameOver)
        if player.queen.square == None:
            for rook in player.rooks:
                if rook.square != None:
                    continue
            for knight in player.knights:
                if knight.square != None:
                    knightsAlive += 1
            for bishop in player.bishops:
                if bishop.square != None:
                    bishopsAlive += 1
            if (bishopsAlive + knightsAlive > 1):
                continue
        else:
            continue
        gameOver[0] = True
        gameOver[1] = player.color
    return (gameOver)


def checkForRestart(x, y, mouseClicked):
    if x < LEFTBORDER and y < TOPBORDER and mouseClicked:
        return True


class Piece:

    def __init__(self, name, square, moves, color):
        self.name = name
        self.square = square
        self.allowedMoves = moves
        self.color = color
        self.isAlive = True

    def kill(self):
        self.isAlive = False
        self.square = None


class Pawn(Piece):

    def __init__(self, square, color):
        self.allowedMoves = PAWNMOVES
        self.hasMoved = False
        if color == WHITE:
            self.imageSurf = pygame.image.load('assets\\pawn-wht.png')
            self.iconSurf = pygame.image.load('assets\\pawn-wht-sml.png')
        else:
            self.imageSurf = pygame.image.load('assets\\pawn-blk.png')
            self.iconSurf = pygame.image.load('assets\\pawn-blk-sml.png')
        super(Pawn, self).__init__(
            PAWN, square, self.allowedMoves, color)


class Rook(Piece):

    def __init__(self, square, color):
        self.allowedMoves = ROOKMOVES
        if color == WHITE:
            self.imageSurf = pygame.image.load('assets\\rook-wht.png')
            self.iconSurf = pygame.image.load('assets\\rook-wht-sml.png')
        else:
            self.imageSurf = pygame.image.load('assets\\rook-blk.png')
            self.iconSurf = pygame.image.load('assets\\rook-blk-sml.png')
        super(Rook, self).__init__(ROOK, square, self.allowedMoves, color)


class Knight(Piece):

    def __init__(self, square, color):
        self.allowedMoves = KNIGHTMOVES
        if color == WHITE:
            self.imageSurf = pygame.image.load('assets\\knight-wht.png')
            self.iconSurf = pygame.image.load('assets\\knight-wht-sml.png')
        else:
            self.imageSurf = pygame.image.load('assets\\knight-blk.png')
            self.iconSurf = pygame.image.load('assets\\knight-blk-sml.png')
        super(Knight, self).__init__(KNIGHT, square, self.allowedMoves, color)


class Bishop(Piece):

    def __init__(self, square, color):
        self.allowedMoves = BISHOPMOVES
        if color == WHITE:
            self.imageSurf = pygame.image.load('assets\\bishop-wht.png')
            self.iconSurf = pygame.image.load('assets\\bishop-wht-sml.png')
        else:
            self.imageSurf = pygame.image.load('assets\\bishop-blk.png')
            self.iconSurf = pygame.image.load('assets\\bishop-blk-sml.png')
        super(Bishop, self).__init__(BISHOP, square, self.allowedMoves, color)


class Queen(Piece):

    def __init__(self, square, color):
        self.allowedMoves = QUEENMOVES
        if color == WHITE:
            self.imageSurf = pygame.image.load('assets\\queen-wht.png')
            self.iconSurf = pygame.image.load('assets\\queen-wht-sml.png')
        else:
            self.imageSurf = pygame.image.load('assets\\queen-blk.png')
            self.iconSurf = pygame.image.load('assets\\queen-blk-sml.png')
        super(Queen, self).__init__(QUEEN, square, self.allowedMoves, color)


class King(Piece):

    def __init__(self, square, color):
        self.allowedMoves = KINGMOVES
        self.isMated = False
        if color == WHITE:
            self.imageSurf = pygame.image.load('assets\\king-wht.png')
            self.iconSurf = pygame.image.load('assets\\king-wht-sml.png')
        else:
            self.imageSurf = pygame.image.load('assets\\king-blk.png')
            self.iconSurf = pygame.image.load('assets\\king-blk-sml.png')
        super(King, self).__init__(KING, square, self.allowedMoves, color)


class Player:

    def __init__(self, color):
        self.color = color
        if color == WHITE:
            self.isMyTurn = True
            self.homeRow = 1
            self.pawnStartingRow = 2
            self.colorString = WHITESTRING
        else:
            self.isMyTurn = False
            self.homeRow = 8
            self.pawnStartingRow = 7
            self.colorString = BLACKSTRING
        self.pieces = []
        self.deadPieces = []
        self.alivePieces = []
        self.queen = Queen(('d', self.homeRow), color)
        self.pieces.append(self.queen)
        self.king = King(('e', self.homeRow), color)
        self.pieces.append(self.king)
        self.pawns = []
        self.rooks = []
        self.knights = []
        self.bishops = []
        for column in BOARDCOLUMNS:
            self.pawns.append(
                Pawn((column, self.pawnStartingRow), self.color))
            self.pieces.append(self.pawns[len(self.pawns) - 1])
        for column in ('a', 'h'):
            self.rooks.append(Rook((column, self.homeRow), self.color))
            self.pieces.append(self.rooks[len(self.rooks) - 1])
        for column in ('b', 'g'):
            self.knights.append(Knight((column, self.homeRow), self.color))
            self.pieces.append(self.knights[len(self.knights) - 1])
        for column in ('c', 'f'):
            self.bishops.append(Bishop((column, self.homeRow), self.color))
            self.pieces.append(self.bishops[len(self.bishops) - 1])
        self.alivePieces = self.pieces


if __name__ == '__main__':
    main()
