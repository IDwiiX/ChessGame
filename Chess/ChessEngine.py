class GameState:
    def __init__(self):
        # Échiquier 8x8
        # b pour black et w pour white
        # initial de chaque pièce ex: N pour knight

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.moveLog = []
        self.whiteToMove = True
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()  # coordonnée de la case où en passant est possible
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    """
    Prend un coup en paramètre et l'éxécute
    """

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # enregistrer le mouvement afin que nous puissions le défaire plus tard
        self.whiteToMove = not self.whiteToMove  # changement de joueur
        # enregiste la nouvelle position du roi si il est bougé
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Promotion du pion
        if move.isPawnPromotion:
            promotionPiece = input("Proumouvoir en Q, R, B, N")
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotionPiece

        # En passant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'  # capture du pion

        # mette à jour la variable enpassantPossible
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:  # seuleent dans un avance de 2 cases
            self.enpassantPossible = ((move.endRow + move.startRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # Roque
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # roque coté roi
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # bouge la tour
                self.board[move.endRow][move.endCol + 1] = '--'  # supprime l'ancienne tour
            else:  # roque coté dame
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # bouge la tour
                self.board[move.endRow][move.endCol - 2] = '--'  # supprime l'ancienne tour

        # Mettre à jour les droits du roque
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    """
    Annule le dernier coup fait undo == annuler
    """

    def undoMove(self):
        if len(self.moveLog) != 0:  # vérifie si il y'a un coup à annuler
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # changement de tour
            # enregiste la nouvelle position du roi si besoin
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # annuler en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'  # laisse la case vide
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)

            # annuler l'avancé de deux cases du pion
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # annuler le droit du roque
            self.castleRightsLog.pop()  # se débarasser des droits du roque du coup qu'on est entrain d'annuler
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            # annuler le coup du roque
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # coté roi
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # coté dame
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

    '''
    Mettre à jour les droits du roque de chaque coup
    '''

    def updateCastleRights(self, move):
        if move.pieceCaptured == 'wR':
            if move.endCol == 0:
                self.currentCastlingRight.wqs = False
            elif move.endCol == 7:
                self.currentCastlingRight.wks = False
        if move.pieceCaptured == 'bR':
            if move.endCol == 0:
                self.currentCastlingRight.wqs = False
            elif move.endCol == 7:
                self.currentCastlingRight.wks = False

        elif move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False

        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # tour de gauche
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # tour de droite
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # tour de gauche
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # tour de droite
                    self.currentCastlingRight.bks = False

    """
    Tout les coups avec les échecs
    """

    def getValidMoves(self):
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # seulement 1 échec, soit on peut bloqué, soit on bouge le roi
                moves = self.getAllPossibleMoves()
                # Pour bloquer un échec, il faut bouger la pièce entre la pièce qui attaque et le roi
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]  # pièce ennemie qui cause l'échec
                validSquares = []  # cases où les pièces peuvent bouger en cas d'échec
                # si c'est un cavalier, soit capturer le cavalier soit bouger le roi
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # check[2]=direction de l'échec
                        validSquares.append(validSquare)
                        if validSquares[0] == checkRow and validSquares[1] == checkCol:
                            break
                # Se débarasser de n'imorte quel coup qui ne bloque pas l'échec ou bouger le roi
                for i in range(len(moves) - 1, -1, -1):  # vaut mieux commencer la comparaison de la fin de la liste
                    if moves[i].pieceMoved[1] != 'K':  # ne peut pas bouger le roi, donc soit capturer soit bloquer
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:  # tu ne peux ni captuer ni bloquer
                            moves.remove(moves[i])
            else:  # un double échec, le roi est obligé de bougé
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # pas d'échec, donc tout les coups sont permis
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.currentCastlingRight = tempCastleRights
        return moves

    """
    Determine si le joueur est en échec
    """

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    """
    Determine si l'ennemie peut attaquer la case r,c 
    """

    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove  # switch to opponent's point of view
        opponents_moves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opponents_moves:
            if move.endRow == row and move.endCol == col:  # square is under attack
                return True
        return False

    """
    Tout les coups sans les échecs
    """

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # nombre de ligne + len(board) = 8, c'est juste une manière plus rigoureuse
            for c in range(len(self.board[r])):  # nombre de colonnes dans des lignes données
                turn = self.board[r][c][0]  # soit blanc soit noir
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)  # prend la fonction de mouvement appropriée
        return moves

    """
    Tout les coups pour les pions qui sont dans row, col et on les ajoute dans la liste
    """

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:  # pion blanc qui joue
            if self.board[r - 1][c] == "--":  # avance d'une seule case
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":  # avance de deux cases
                        moves.append(Move((r, c), (r - 2, c), self.board))

            if c - 1 >= 0:  # capture à gauche
                if self.board[r - 1][c - 1][0] == 'b':  # Il y'a une pièce ennemie à capturer
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))

            if c + 1 <= 7:  # capture à droite
                if self.board[r - 1][c + 1][0] == 'b':  # Il y'a une pièce ennemie à capturer
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))

        else:  # pion noir qui joue
            if self.board[r + 1][c] == "--":  # avance d'une seule case
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":  # avance de deux cases
                        moves.append(Move((r, c), (r + 2, c), self.board))

            if c - 1 >= 0:  # capture à gauche
                if self.board[r + 1][c - 1][0] == 'w':  # Il y'a une pièce ennemie à capturer
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))

            if c + 1 <= 7:  # capture à droite
                if self.board[r + 1][c + 1][0] == 'w':  # Il y'a une pièce ennemie à capturer
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    """             
    Tout les coups pour les tours qui sont dans row, col et on les ajoute dans la liste
    """

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove((self.pins[i]))
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # haut, gauche, bas, droite
        enemyColor = "b" if self.whiteToMove else "w"  # peut etre rempacé avec le if traditionel
        for d in directions:
            for i in range(1, 8):  # peut bouger max 7 cases
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # dans l'échiquier
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # case vide
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # pièce ennemie disponible
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # Pièce alliée
                            break
                else:  # En dehors de l'échiquier
                    break

    """             
    Tout les coups pour les chevaux qui sont dans row, col et on les ajoute dans la liste
    """

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))  # 8 possibilitées
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:  # pas un allié (vide ou pièce ennemie)
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    """             
    Tout les coups pour les fous qui sont dans row, col et on les ajoute dans la liste
    """

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove((self.pins[i]))
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # haut à gauche, haut à droite, bas à  gauche, bas à droite
        enemyColor = "b" if self.whiteToMove else "w"  # peut etre rempacé avec le if traditionel
        for d in directions:
            for i in range(1, 8):  # peut bouger max 7 cases
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # dans l'échiquier
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # case vide
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # pièce ennemie disponible
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # Pièce alliée
                            break
                else:  # En dehors de l'échiquier
                    break

    """             
    Tout les coups pour les reines qui sont dans row, col et on les ajoute dans la liste
    """

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    """             
    Tout les coups pour les rois qui sont dans row, col et on les ajoute dans la liste
    """

    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # pas un allié (vide ou ennemie)
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    '''
    Générer tout les coups valides du roque pour le roi (r, c) et les ajoute dans la liste des coups
    '''

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return  # ne peut pas roquer car en échec
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMove(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMove(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

    """
    Retourne si le joueur est en échec, une liste des clouages, et une liste des échecs
    """

    def checkForPinsAndChecks(self):
        pins = []  # cases où la pièce alliée est coulée
        checks = []  # cases où la pièce ennemie applique un échec
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # Checker les clouages et échecs
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # réinistialise les clouages possibles
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # 1er allié qui peut etre cloué
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # il y'a qlq derrière cet allié, alors ce n'est plus un clouage
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # ça check si il y'a un vis a vis avec le roi avec le fou, tour, dame, et qu'un pion est cloué
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():  # Pas de pièce qui bloque, donc échec
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # Pièce bloquée, donc clouage
                                pins.append(possiblePin)
                                break
                        else:  # la pièce ennemie n'applique pas d'échecs
                            break
                else:
                    break  # en dehors de l'échiquier
        # Checker les coups des cavaliers
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':  # le cavalier ennemie attaque le roi
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # Transformez les colones en lettres et les lignes en chiffres de 1 à 8 car dans le jeu c'est des lettres ex: e4
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # Promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7):
            self.isPawnPromotion = True

        # En passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        # Roque
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    """
    Equals method
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
