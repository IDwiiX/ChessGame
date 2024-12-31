import random

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

knightScore = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
               [0.1, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.1],
               [0.1, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.1],
               [0.1, 0.4, 0.3, 0.3, 0.3, 0.3, 0.4, 0.1],
               [0.1, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.1],
               [0.1, 0.3, 0.4, 0.3, 0.3, 0.4, 0.3, 0.1],
               [0.1, 0.3, 0.2, 0.4, 0.4, 0.2, 0.3, 0.1],
               [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishopScore = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
               [0.1, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.1],
               [0.1, 0.3, 3, 0.3, 0.3, 0.3, 0.4, 0.1],
               [0.1, 0.6, 0.3, 0.3, 0.3, 0.3, 0.6, 0.1],
               [0.1, 0.4, 0.6, 0.3, 0.3, 0.6, 0.4, 0.1],
               [0.5, 0.1, 0.0, 0.6, 0.6, 0.0, 0.1, 0.5],
               [0.2, 1, 0.4, 0.6, 0.6, 0.4, 1, 0.2],
               [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rookScore = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
             [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
             [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
             [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
             [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
             [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
             [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
             [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queenScore = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
              [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
              [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
              [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
              [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
              [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
              [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
              [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawnScore = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
             [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
             [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
             [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
             [0.2, 0.2, 0.2, 1, 1, 0.2, 0.2, 0.2],
             [0.25, 0.5, 0.1, 0.2, 0.2, 0.1, 0.5, 0.25],
             [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
             [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piecePositionScores = {"wN": knightScore,
                       "bN": knightScore[::-1],
                       "wB": bishopScore,
                       "bB": bishopScore[::-1],
                       "wQ": queenScore,
                       "bQ": queenScore[::-1],
                       "wR": rookScore,
                       "bR": rookScore[::-1],
                       "wp": pawnScore,
                       "bp": pawnScore[::-1]}

CHECKMATE = 1000  # c'est des points, on essaye de dire les meilleurs coups à faire pour l'odinateur avec des points
STALEMATE = 0
DEPTH = 4

global nextMove
global counter

'''
Méthode d'aide qui va nous permettre de faire le premier appel récursif
'''


def findBestMove(gs, validMoves, returnQueue):
    global nextMove, counter
    nextMove = None
    random.shuffle(validMoves)
    counter = 0
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    # print(counter)
    returnQueue.put(nextMove)


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    #  l'ordre des coups, du pire au meilleur
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                print(move, score)
        gs.undoMove()
        if maxScore > alpha:  # élagage (pruning)
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


'''
Score positive ==> Bien pour les blans / score négatif ==> bien pour les noirs
'''


def evaluatePieceActivity(piece, row, col):
    activity_score = 0

    # Coordonnées du centre de l'échiquier
    center_row, center_col = 3, 3

    # Distance euclidienne entre la pièce et le centre
    distance_to_center = ((row - center_row) ** 2 + (col - center_col) ** 2) ** 0.5

    # Attribution de points en fonction de la distance
    if piece[1] == "N":
        activity_score = 0.1 * (3 - distance_to_center)
    if piece[1] == "B":
        activity_score = 0.1 * (3 - distance_to_center)
    elif piece[1] == "Q":
        activity_score = 0.1 * (3 - distance_to_center)
    elif piece[1] == "R":
        activity_score = 0.1 * (3 - distance_to_center)
    elif piece[1] == "p":
        activity_score = 0.2 * (3 - distance_to_center)
    # Ajoutez des conditions similaires pour les autres types de pièces

    return activity_score


def scoreBoard(gs):
    #  échec et mat
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE  # victoire des noirs
        else:
            return CHECKMATE  # victoire des blancs
    elif gs.stalemate:
        return STALEMATE

    #  le rapport matériel
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board)):
            piece = gs.board[row][col]
            if piece != "--":
                # Ajouter au score de manière à améliorer la position
                piecePositionScore = 0
                if piece[1] != "K":
                    piecePositionScore = piecePositionScores[piece][row][col]

                if piece[0] == 'w':
                    score += pieceScore[piece[
                        1]] + piecePositionScore + evaluatePieceActivity(piece, row,
                                                                         col)  # vers positif alors c'est avantage au blanc
                elif piece[0] == 'b':
                    score -= pieceScore[piece[
                        1]] + piecePositionScore + evaluatePieceActivity(piece, row,
                                                                         col)  # vers négatif alors c'est avantage au noir

    # les échecs
    if gs.checks:
        score += 0.01

    return score


'''
Réalise un coup aléatoire
'''


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]
