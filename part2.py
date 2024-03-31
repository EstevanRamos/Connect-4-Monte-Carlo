from monte_carlo import *
from collections import defaultdict

# You will run an experiment to test five variations of your algorithms against each 
# other, as listed below. The numbers after the algorithm acronym are the parameter 
# settings. Run a round-robin tournament where you run each combination of the five 
# against each other for 100 games, recording the number of wins for each algorithm. 
# There should be 25 combinations in total. Present a table in your final report of the 
# results, showing the winning percentage for the algorithm specified on the row vs 
# the algorithm specified on the column. 

def main():
    scores = defaultdict(lambda: defaultdict(int))
    contenders = ["UR", "PMCGS500", "PMCGS10000", "UCT500", "UCT10000"]
    for contender1 in contenders:
        for contender2 in contenders:
            wins = [0, 0]
            ties = 0
            for x in range(25):
                board = [['O', 'O', 'O', 'O', 'O', 'O', 'O'],['O', 'O', 'O', 'O', 'O', 'O', 'O'],['O', 'O', 'O', 'O', 'O', 'O', 'O'],['O', 'O', 'O', 'O', 'O', 'O', 'O'],['O', 'O', 'O', 'O', 'O', 'O', 'O'],['O', 'O', 'O', 'O', 'O', 'O', 'O']]
                winner = play_game(contender1, contender2, board)
                if winner == 1:
                   wins[0] += 1
                elif winner == -1:
                   wins[1] += 1
                else:
                    ties+=1
            scores[contender1][contender2]+=wins[0]
            scores[contender2][contender1]+=wins[1]
            print(f"{contender1} {wins[0]} to {contender2} {wins[1]}", end=" ")
            print(f"Ties: {ties}")
    print("_"*11*(len(contenders)+1))
    prettyPrint(scores)

def prettyPrint(scores):
    '''prints dictionary into a grid'''
    grid=[]
    temp=["     "]
    for contender1 in scores.keys():
        temp.append(contender1)
    grid.append(temp)
    for contender1 in scores.keys():
        temp=[contender1]
        grid.append(temp)
    for row in grid[1:]:
        for contender2 in scores.keys():
            row.append(scores[row[0]][contender2])

    #pad all values to 11 chars
    for row in grid:
        for i in range(len(row)):
            row[i] = str(row[i]).ljust(11)
    for row in grid:
        print("".join(row))

def printBoard(board):
    for row in board:
        print("\t"+" ".join(row))
    print()

def play_game(contender1, contender2, board):
    #yellow goes first
    Yturn = True
    while True:
        if Yturn:
            move = getMove(contender1, "Y", board)
            board = play_move(board, move)
        else:
            move = getMove(contender2, "R", board)
            board = play_move(board, move)

        Yturn = not Yturn
        if is_game_over(board):
           return get_game_result(board)

def getMove(algorithm, player, board, verbosity="NONE"):
    ["UR", "PMCGS500", "PMCGS10000", "UCT500", "UCT10000"]
    if algorithm == 'UR':
        # Find legal moves
        legal_moves = find_legal_moves(board)
        return uniform_random_move(legal_moves)

    if algorithm == "PMCGS500":
      simulations = 500
      root = MonteCarloTreeSearchNode(state = board, player=player ,verbosity=verbosity)
      return root.best_action(simulations = simulations).parent_action
    

    if algorithm == "PMCGS10000":
      simulations = 1000
      root = MonteCarloTreeSearchNode(state = board, player=player , verbosity=verbosity)
      return root.best_action(simulations = simulations).parent_action
    
    if algorithm == "UCT500":
      simulations = 500
      root = MonteCarloTreeSearchNode(state = board, player=player , verbosity=verbosity)
      return root.best_action(simulations = simulations, algo='UCT').parent_action
    
    if algorithm == "UCT10000":
      simulations = 1000
      root = MonteCarloTreeSearchNode(state = board, player=player , verbosity=verbosity)
      return root.best_action(simulations = simulations, algo='UCT').parent_action
 



if __name__ == '__main__':
    main()