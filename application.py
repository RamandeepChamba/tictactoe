from flask import Flask, flash, render_template, session, redirect, url_for
from flask_session import Session
from tempfile import mkdtemp
import time

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
    
    # --Cols match
    if board[row].count(turn) == 3:
        return redirect(url_for("reset", flash_message=f"{turn} won!"))

    # --Rows match
    if (board[0][col], board[1][col], board[2][col]) == (turn, turn, turn):
        return redirect(url_for("reset", flash_message=f"{turn} won!"))
   
    # --Diagonal match
    if [(0,0), (0,2), (1,1), (2,0), (2,2)].count((row, col)) == 1:
        if (board[0][0], board[1][1], board[2][2]) == (turn, turn, turn):
            return redirect(url_for("reset", flash_message=f"{turn} won!"))

        if (board[0][2], board[1][1], board[2][0]) == (turn, turn, turn):
            return redirect(url_for("reset", flash_message=f"{turn} won!"))
 
    # --Game tied
    if True:
        nones = 0 
        for row in board:
            nones += row.count(None)
            
        # No nones / board full 
        if nones == 0:
            return redirect(url_for("reset", flash_message="Game tied!"))


    # Toggle turn
    if turn == "X":
        session["turn"] = "O"
    else:
        session["turn"] = "X"

    # Redirect to update board
    return redirect(url_for("index"))


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


if __name__ == "__main__":

    app.run(debug=True)

