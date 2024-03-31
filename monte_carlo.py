
import sys
import random
import numpy as np
import copy
import math
import time
from collections import defaultdict

def read_game_state(file_path):
    """
    Reads the game state from a file.
    """
    with open(file_path, 'r') as file:
        algorithm = file.readline().strip()
        player = file.readline().strip()
        board = [list(file.readline().strip()) for _ in range(6)]
    return algorithm, player, board

def find_legal_moves(board):
    """
    Finds legal moves based on the current board state.
    Legal moves are columns that are not full (i.e., do not have a piece in the top row).
    """
    return [col for col in range(7) if board[0][col] == 'O']

def uniform_random_move(legal_moves):
    """
    Selects a legal move using the uniform random strategy.
    """
    return random.choice(legal_moves)

class MonteCarloTreeSearchNode():
  """
  state: For our game it represents the board state.
  parent: It is None for the root node and for other nodes it is equal to the node it is derived from. For the first turn as you have seen from the game it is None.
  children: It contains all possible actions from the current node.
  parent_action: None for the root node and for other nodes it is equal to the action which it’s parent carried out.
  _number_of_visits: Number of times current node is visited
  results: It’s a dictionary
  _untried_actions: Represents the list of all possible actions
  action: Move which has to be carried out.
  """
  def __init__(self, state, parent=None, parent_action=None, verbosity = 0):
    self.state = state
    self.parent = parent
    self.parent_action = parent_action
    self.children = []
    self._number_of_visits = 0
    self._results = defaultdict(int)
    self._results[1] = 0
    self._results[-1] = 0
    self._untried_actions = None
    self._untried_actions = self.untried_actions()
    self.verbosity = verbosity # 0 = None , 1 = Brief, 2 = Verbose
    return

  def untried_actions(self):
    """
    get any possible actions
    """
    self._untried_actions = self.get_legal_actions()
    return self._untried_actions

  def q(self):
      wins = self._results[1]
      losses = self._results[-1]
      return wins - losses

  def n(self):
      return self._number_of_visits

  def UCB(self):
    if self.n() == 0: return math.sqrt(2)
    return self._results[1] / self.n() + math.sqrt(math.log(self.parent.n())/self.n())

  def expand(self):
      """
      From the present state, next state is generated depending on the action which is carried out.
      In this step all the possible child nodes corresponding to generated states are appended to the children array and the child_node is returned.
      The states which are possible from the present state are all generated and the child_node corresponding to this generated state is returned.
      """
      if self.verbosity == 2:
        print('adding children')
      while len(self._untried_actions) != 0:
        action = self._untried_actions.pop()
        next_state = self.move(action)
        child_node = MonteCarloTreeSearchNode(next_state, parent=self, parent_action=action, verbosity=self.verbosity)
        self.children.append(child_node)

  def is_terminal_node(self):
      """
      This is used to check if the current node is terminal or not.
      Terminal node is reached when the game is over.
      """
      return self.is_game_over()

  def rollout(self):
      """
      From the current state, entire game is simulated till there is an outcome for the game.
      the outcome of the game is returned
      """
      if self.verbosity == 2:
        print('simulating...')
      current_node = copy.deepcopy(self)
      while not current_node.is_game_over():

        possible_moves = current_node.get_legal_actions()
        action = current_node.rollout_policy(possible_moves)#later its possible to change how we select nodes for simulation
        if self.verbosity == 2:
          print('Move Selected:', action)
        current_node.state = current_node.move(action)

      return current_node.game_result()

  def backpropagate(self, result):
      """
      In this step all the statistics for the nodes are updated.
      """
      if self.verbosity == 2:
        print('backpropogating...')
      self._number_of_visits += 1.
      self._results[result] += 1.
      if self.parent:
        if self.verbosity == 2:
          print('New Values:')
          print('Wi:', self._results[1])
          print('Ni:', self.n())
        self.parent.backpropagate(result)

  def is_fully_expanded(self):
      """
      returns true if all actions are popped from untried actions
      """
      return len(self._untried_actions) == 0

  def best_child(self, c_param=0.1):
      """
      Once fully expanded, this function selects the best child out of the children array.
      """
      possible_children = []
      for child in self.children:
        if child.n() > 0:
          possible_children.append(child)

      choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in possible_children]
      return self.children[np.argmax(choices_weights)]

  def rollout_policy(self, possible_moves):
      """
      randomly selects a move out of possible moves
      """
      return possible_moves[np.random.randint(len(possible_moves))]

  def _tree_policy(self, algo = 'MCTS'):
      """
      Selects node to run rollout.
      """
      if algo == 'MCTS':
        current_node = self
        while len(current_node.children) > 0 : #while node is not leaf
          children = current_node.children
          current_node = random.choice(children)
        return current_node

      elif algo == 'UCT':
        current_node = self
        while len(current_node.children) > 0: # while node is not a leaf
          max_value= float('-inf')
          possible_children = []

          if current_node.verbosity == 2:
            print('Wi : ' , current_node._results[1])
            print('Ni : ' , current_node.n())

          for node in current_node.children:
            UCB = node.UCB()
            if node.verbosity == 2:
              print('Child UCB Value:' , UCB)

            if UCB > max_value:
              max_value = UCB

          for child in current_node.children:
            if child.UCB() == max_value:
              possible_children.append(child)

          current_node = random.choice(possible_children)
          if current_node.verbosity == 2:
            print('Move Selected:', current_node.parent_action)

        return current_node


  def best_action(self, simulations = 100, c_param=0.1, algo = 'MCTS'):
      """
      This is the best action function which returns the node corresponding to best possible move.
      The step of expansion, simulation and backpropagation are carried out by the code above.
      """
      start_time = time.time()

      for i in range(simulations):
        v = self._tree_policy(algo)#select node based on tree policy
        v.expand()
        reward = v.rollout()
        v.backpropagate(reward)

      if self.verbosity == 1 or self.verbosity == 2:
        print('Number of rollouts:', simulations)
        print('Seconds elapsed: ', time.time()- start_time)

      return self.best_child(c_param)

  def is_game_over(self):
    """
    Returns true or false depending on if game is over
    """
    def check_consecutive(lst):
        count = 1
        for i in range(len(lst) - 1):
            if lst[i] != 'O' and lst[i] == lst[i + 1]:
                count += 1
                if count == 4:
                    return True
            else:
                count = 1
        return False

    def check_rows(board):
        for row in board:
            if check_consecutive(row):
                return True
        return False

    def check_columns(board):
        for col in range(len(board[0])):
            column = [board[row][col] for row in range(len(board))]
            if check_consecutive(column):
                return True
        return False

    def check_diagonals(board):
        for i in range(len(board) - 3):
            for j in range(len(board[0]) - 3):
                if board[i][j] != 'O' and board[i][j] == board[i + 1][j + 1] == board[i + 2][j + 2] == board[i + 3][j + 3]:
                    return True
                if board[i][j + 3] != 'O' and board[i][j + 3] == board[i + 1][j + 2] == board[i + 2][j + 1] == board[i + 3][j]:
                    return True
        return False

    if check_rows(self.state) or check_columns(self.state) or check_diagonals(self.state):
      return True

    if len(find_legal_moves(self.state)) == 0:  # Assuming find_legal_moves function is defined elsewhere
      return True

    return False

  def game_result(self):
    """
    Returns 1, 0, or -1 depending on the game state:
    1 for a win, 0 for a tie, and -1 for a loss.
    """
    def get_winner(player):
      if player == 'Y':
        return 1
      else:
        return -1

    # Check for horizontal wins.
    for row in self.state:
      for i in range(len(row) - 3):
        if row[i] == row[i + 1] == row[i + 2] == row[i + 3] and row[i] != 'O':
          return get_winner(row[i])

    # Check for vertical wins.
    for col in range(len(self.state[0])):
      for i in range(len(self.state) - 3):
        if self.state[i][col] == self.state[i + 1][col] == self.state[i + 2][col] == self.state[i + 3][col] and self.state[i][col] != 'O':
          return get_winner(self.state[i][col])

    # Check for diagonal wins.
    for i in range(len(self.state) - 3):
      for j in range(len(self.state[0]) - 3):
        if self.state[i][j] == self.state[i + 1][j + 1] == self.state[i + 2][j + 2] == self.state[i + 3][j + 3] and self.state[i][j] != 'O':
          return get_winner(self.state[i][j])

        if self.state[i][j + 3] == self.state[i + 1][j + 2] == self.state[i + 2][j + 1] == self.state[i + 3][j] and self.state[i][j + 3] != 'O':
          return get_winner(self.state[i][j + 3])

    #in case of draw
    if len(find_legal_moves(self.state)) == 0:
      return 0

    # If there is no winner, return None.
    return None



  def move(self, action):
      """
      Given an action, Return a new state after that action occurs
      ASSUMES YELLOW ALWAYS GOES FIRST
      """
      #calculate which players turn it is
      b = np.array(self.state)
      num_ys = (b == 'Y').sum()
      num_rs = (b == 'R').sum()
      player = 'R' if num_ys > num_rs else 'Y'

      #copy the new board
      board = copy.deepcopy(self.state)
      row = 0
      #drop piece
      for i in range(len(board[0])-1):
        if board[i][action] == 'O':
          row = i

      board[row][action] = player
      return board

  def get_legal_actions(self):

      '''
      gets legal moves of the state
      '''
      return find_legal_moves(self.state)

def main(file_path, verbosity, simulations):
    # Read game state
    algorithm, player, board = read_game_state(file_path)

    #for testing
    algorithm = 'UCT'

    match verbosity:
      case 'None':
        v = 0
      case 'Brief':
        v = 1
      case 'Verbose':
        v = 2

    # Select move based on the algorithm
    if algorithm == 'UR':
        # Find legal moves
        legal_moves = find_legal_moves(board)
        move = uniform_random_move(legal_moves)

    if algorithm == 'PMCGS':
      root = MonteCarloTreeSearchNode(state = board, verbosity=v)
      selected_node = root.best_action(simulations = simulations)
      print(selected_node.parent_action)

    if algorithm == 'UCT':
      root = MonteCarloTreeSearchNode(state = board, verbosity=v)
      selected_node = root.best_action(simulations = simulations, algo='UCT')
      print(selected_node.parent_action)


if __name__ == "__main__":
    file_path = './test1.txt'  # The name of the input file
    verbosity = 'Verbose'  # Verbose, Brief, or None
    simulations = 100  # Number of simulations, not used for UR but required for the script

    main(file_path, verbosity, simulations)