import pygame as p
import ChessEngine, ChessIA
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512  # ou 400

MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT

DIMENSION = 8  # dimension 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15  # pour animations
IMAGES = {}

global colors


# Charger les images
def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Note: on peut acceder à une image en faisant 'IMAGES["wP"]'


# Le programme principal
def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    movelogFont = p.font.SysFont("Helvitca", 20, False, False)

    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # variable quand un coups est fait
    animate = False
    loadImages()
    running = True
    sqSelected = ()  # tuple (row, col), dernier click de l'utilisateur
    playerClicks = []  # garde les click du joueur
    gameOver = False

    player1 = True  # si Humain joue les blans alors True, si c'est IA c'est False / False pour que les deux IA jouent
    player2 = False  # si humain joue les noirs alors False, si c'est IA c'est True

    IAThinking = False
    moveFinderProcess = None
    moveUndo = False

    while running:
        humanTurn = (gs.whiteToMove and player1) or (not gs.whiteToMove and player2)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # souris
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # (x,y) location de la souris
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >= 8:  # click 2 fois sur la mm case ou click la partie droite
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 2 and humanTurn:  # apres le 2eme click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()  # réinitialiser les click du joueur
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            # bouton
            elif e.type == p.KEYDOWN:
                if e.key == p.K_SPACE:  # annule quand la touche espace est pressé
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if IAThinking:
                        moveFinderProcess.terminate()
                        IAThinking = False
                    moveUndo = True
                if e.key == p.K_r:  # recommence la partie quand r est pressé
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if IAThinking:
                        moveFinderProcess.terminate()
                        IAThinking = False
                    moveUndo = True

        # IA trouvé les coups
        if not gameOver and not humanTurn and not moveUndo:
            if not IAThinking:
                IAThinking = True
                returnQueue = Queue()  # utilisée pour passer les data entre les fils
                moveFinderProcess = Process(target=ChessIA.findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start()  # exécute findBestMove()

            if not moveFinderProcess.is_alive():
                IAMove = returnQueue.get()
                if IAMove is None:
                    IAMove = ChessIA.findRandomMove(validMoves)
                gs.makeMove(IAMove)
                moveMade = True
                animate = True
                IAThinking = False

        if moveMade:
            if animate:
                animateMoves(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndo = False

        drawGameState(screen, gs, validMoves, sqSelected, movelogFont)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawEndGameText(screen, 'Échec et mat, victoire des noirs')
            else:
                drawEndGameText(screen, 'Échec et mat, victoire des blancs')
        elif gs.stalemate:
            gameOver = True
            drawEndGameText(screen, 'Pat, égalité')

        clock.tick(MAX_FPS)
        p.display.flip()


# Responsable des graphiques
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)  # Dessine les cases
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # Dessine les pièces
    drawMoveLog(screen, gs, moveLogFont)


# Dessine les cases
def drawBoard(screen):
    global colors
    colors = [p.Color("antiquewhite1"), p.Color("tan4")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# Surligne la case séléctionnée et les cases possibles
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # la pièce séléctionnée peut être bougée
            # surligne la case séléctionnée
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # valeur de transparence -> 0 = transparant 255 = opaque
            s.fill(p.Color('red'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # surligne les coups possibles
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


# Dessine les pièces
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # pas les cases vides
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# écrit les coups joués
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("indianred4"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []

    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):  # on s'assure que les noirs ont fait un coup
            moveString += str(moveLog[i + 1]) + "  "
        moveTexts.append(moveString)

    movesPerRow = 3  # peut être changé
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]

        textObject = font.render(text, False, p.Color('cornsilk'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


# Animation
def animateMoves(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquares = 10  # les frame per seconde de chaque case
    frameCount = (abs(dR) + abs(dC)) * framesPerSquares
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # efface la pièce de sa case d'arrivée
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # dessine la pièce capturée dans un rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # dessine la pièce qui bouge
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)  # vitesse


# Ce qui va être affiché en fin de partie
def drawEndGameText(screen, text):
    font = p.font.SysFont("arial", 32, True, False)
    textObject = font.render(text, False, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
