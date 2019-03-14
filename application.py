import copy
from flask import Flask, flash, render_template, session, redirect, url_for
from flask_session import Session
import math
from tempfile import mkdtemp

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():

    if "board" not in session:
        session["board"] = [[None, None, None], [None, None, None], [None, None, None]]
        session["turn"] = "X"

    return render_template("game.html", game=session["board"], turn=session["turn"])


@app.route("/play/<int:row>/<int:col>")
def play(row, col):

    turn = session["turn"]

    # Update game board
    session["board"][row][col] = turn

    # -Check game status
    board = session["board"]
    status = gameStatus(board, row, col, turn)

    # --Got a winner?
    if status == 1 or status == -1:
        return redirect(url_for("reset", flash_message=f"{turn} won!"))

    # --Game tied?
    if status == 0:
        return redirect(url_for("reset", flash_message="Game tied!"))


    # Toggle turn
    if turn == "X":
        session["turn"] = "O"
    else:
        session["turn"] = "X"

    # Redirect to update board
    return redirect(url_for("index"))


@app.route("/playAI")
def playAI():
    board = session["board"]
    turn = session["turn"]

    # Use AI to select best move
    move = minmax(board, turn)
    # Play the move
    return redirect(url_for("play", row=move[0], col=move[1]))


@app.route("/reset", defaults={"flash_message": None})
@app.route("/reset/<flash_message>")
def reset(flash_message):

    # Reset
    session.clear()

    if flash_message:
        if flash_message == "Game tied!":
            flash(flash_message, "warning")
        else:
            flash(flash_message, "success")

    # Redirect
    return redirect("/")


"""
    0 - game tied
    1 - X won
   -1 - O won
    2 - ongoing
"""
def gameStatus(board, row, col, turn):

    # -Functions
    # --winner
    def winner(turn):
        if turn == "X":
            return 1
        else:
            return -1

    # -Game status

    # --Cols match (horizontal)
    if board[row].count(turn) == 3:
        return winner(turn)

    # --Rows match (vertical)
    if (board[0][col], board[1][col], board[2][col]) == (turn, turn, turn):
        return winner(turn)

    # --Diagonal match
    if [(0,0), (0,2), (1,1), (2,0), (2,2)].count((row, col)) == 1:
        if (board[0][0], board[1][1], board[2][2]) == (turn, turn, turn):
            return winner(turn)

        if (board[0][2], board[1][1], board[2][0]) == (turn, turn, turn):
            return winner(turn)

    # --Game tied
    if True:
        nones = 0
        for row in board:
            nones += row.count(None)

        # No nones / board full
        if nones == 0:
            return 0

    # --Ongoing
    return 2


# AI tictactoe algorithm
"""
    X - tries to maximize score
    O - tries to minimize score

    returns best move
      - (row, col)
"""
def minmax(board, turn):
    # Original moves
    moves = []

    for i in range(3):
        for j in range(3):
            # Available moves
            if board[i][j] == None:
                moves.append((i, j))

    # -Functions
    # --bestMove
    def bestMove(board, turn, row=None, col=None):

        # Possible moves that can be made with tempBoard
        tempMoves = []

        for i in range(3):
            for j in range(3):
                # Available moves
                if board[i][j] == None:
                    tempMoves.append((i, j))

        # Base case
        if row != None and col != None:
            # Last played turn
            if turn == "X":
                lastTurn = "O"
            else:
                lastTurn = "X"

            # Status after last played move
            status = gameStatus(board, row, col, lastTurn)
            # Game over
            if status != 2:
                return {
                    "value": status
                }

        if turn == "X":
            value = -(math.inf)
        else:
            value = math.inf

        values = []
        for move in tempMoves:
            # Temporary board to test different moves
            tempBoard = copy.deepcopy(board)
            row = move[0]
            col = move[1]

            # Play this move
            tempBoard[row][col] = turn
            # Play recursively by checking other turn's moves (brute force)
            if turn == "X":
                value = max(value, bestMove(tempBoard, "O", row, col)["value"])
            else:
                value = min(value, bestMove(tempBoard, "X", row, col)["value"])

            # Add this value to compare moves later
            values.append(value)

        # Best move
        if turn == "X":
            return {
                "value": max(values),
                "move": moves[values.index(max(values))]
            }
        else:
            return {
                "value": min(values),
                "move": moves[values.index(min(values))]
            }

    # Return best move
    return bestMove(board, turn)["move"]


if __name__ == "__main__":

    app.run(debug=True)
