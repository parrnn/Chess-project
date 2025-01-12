# Chess Question
### **Introduction**
This project is a command-line implementation of a chess game, designed for players to experience the classic strategy game in a text-based environment. It adheres to the core rules of chess while offering an intuitive interface for move input and gameplay.

#### Players can:

- Select and move pieces according to standard chess rules.
- Track turns and enforce proper move sequences.
- Handle special gameplay features like scorekeeping and move history.
- This project is written in python and is ideal for both casual chess players and programming enthusiasts looking to explore how chess mechanics can be implemented programmatically. Its straightforward design ensures an engaging experience while highlighting the fundamentals of chess logic.
### First run the code with this snippet in your terminal `python ChessNEW.py` 
---
### **Important**
1. Input and Output Configuration
At the start of the code, there is a snippet that reads input from a third-party file and writes the output to another file. This setup allows the program to interact with external files seamlessly. If you prefer to input commands manually, simply comment out the lines from line 9 to line 13.

2. Gameplay Overview
This Python script lets you play a complete game of chess directly in the command line. While adhering to the core mechanics of chess, this implementation introduces some unique differences from traditional chess:

- There is no "check" or "checkmate" logic.
- The game ends when a player's king is captured.
- These changes make for a simpler yet engaging variation of the classic game.
### Sample Input
Below is an example of how to start and play the game using this script. Follow the commands to register users, log in, and begin your chess match:
``` 
help
register ahmad
register ali 1397
register zahra 0019
login ali 1390
login ali 1397
logout
login zahra 0019
new_game ali 10
select 2,2
move 4,2
next_turn
select 7,2
move 5,2
next_turn
forfeit
help
logout
exit
```
and here is the output of it:
```
register [username] [password]
login [username] [password]
remove [username] [password]
list_users
help
exit
invalid command
register successful
register successful
incorrect password
login successful
logout successful
login successful
new game started successfully between zahra and ali with limit 10
selected 
moved
turn completed
selected
moved
turn completed
you have forfeited
player ali with color black won
new_game [username] [limit]
scoreboard
list_users
help
logout
logout successful
program ended
```