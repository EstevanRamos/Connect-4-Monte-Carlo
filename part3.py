from monte_carlo import *

ROWS = 6
COLUMNS = 7
EMPTY = 'O'
PLAYER1 = 'R'
PLAYER2 = 'Y'

# Board
board = [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]
def print_board(board):
    for row in board:
        print(" ".join(row))
    print()

def make_move(column, current_player):
    for row in range(ROWS - 1, -1, -1):
        if board[row][column] == EMPTY:
            board[row][column] = current_player
            winner = get_game_result(board)
            if winner:
                print(f"Player {current_player} wins!")
                return True
            else:
                print_board(board)
                return False
            break

def switch_player(current_player):
    return PLAYER1 if current_player == PLAYER2 else PLAYER2

def make_ai_move(current_player, AI, parameter):
    root = MonteCarloTreeSearchNode(state=board, player=current_player)
    selected_node = root.best_action(simulations=parameter)
    column = selected_node.parent_action
    for row in range(ROWS - 1, -1, -1):    
        if board[row][column] == EMPTY:
            board[row][column] = current_player
            winner = get_game_result(board)
            if winner:
                print(f"Player {current_player} wins!")
                return True
            else:
                return False
            break
    

if __name__ == "__main__":
    ai = input('Enter name of AI to play against (UCT500 or PMCGS10000): ')
    current_player = PLAYER1

    while True:
        if current_player == PLAYER1:
            column = int(input(f"Player {current_player}, enter column number (0-6) to make a move: "))
            if make_move(column, current_player):
                break
        else:
            AI, parameter = None, None
            if ai == "UCT500":
                AI, parameter = uniform_random_move, 500
            elif ai == "PMCGS10000":
                AI, parameter = MonteCarloTreeSearchNode, 1000
            
            if make_ai_move(current_player, AI, parameter):
                break
            print("AI MOVE: \n")
            print_board(board)
        
        current_player = switch_player(current_player)
