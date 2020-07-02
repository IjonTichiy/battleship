# battleship

Battleship is a strategy type guessing game for two players in which the
opponents try to find the location of their opponent's warships and sink them.
At the moment it is only possible to play vs. a simple AI opponent.
Future Releases will include networking to play against each other

# Rules

The game is played on 4 10x10 grids, 2 grids for each player. The goal is to
sink all of your oponent's ships. The game starts when both players have
secretly placed their ships on the bottom grid. The beginning player is chosen
at random. The players take turns firing shots at certain grid coordinates.
If a player hits an enemy ship

# Dependencies

- Qt5 with PyQt5
    you need Qt5 installed on your system and have python-bindings (pyqt5)

- QDarkstyle
    dark style for Qt5

# Playing the game

clone the repository and run the run.py script

    git clone https://github.com/IjonTichiy/battleship
    cd battleship
    python run.py
