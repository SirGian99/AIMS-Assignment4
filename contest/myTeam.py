 # myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from __future__ import annotations

from math import inf
from typing import Tuple 
from capture import GameState
from captureAgents import CaptureAgent

import random, util
from game import AgentState, Actions
import game

GO_BACK_PERCENTAGE_THRESHOLD = 0.5

class Inlet:
  def __init__(self, start_pos, end_pos):
    self.start_pos = start_pos
    self.end_pos = end_pos
    self.size = util.manhattanDistance(start_pos, end_pos)

Position = Tuple[int, int]

class Node():
    """A node class for A* Pathfinding"""
    
    parent : None | Node = None 
    position : Position = None
    g = 0
    h = 0
    f = 0

    def __init__(self, parent : None | Node = None, position : Position = None):
        self.parent = parent
        self.position = position

    def __eq__(self, other : Node) -> bool:
        return self.position == other.position
    def __hash__(self):
        return hash(self.position)



def path_to_moves(path):
  """
  Given a path (a list of nodes), return a list of moves.
  """
  moves = []
  for i in range(len(path)-1):
    vector = (path[i+1][0] - path[i][0], path[i+1][1] - path[i][1])
    direction = Actions.vectorToDirection(vector)
    moves.append(direction)
  return moves

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'Attacker', second = 'Defender'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class MainAgent(CaptureAgent) :
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState : GameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)
    #for line in self.getFood(gameState):
    ##  print('  '.join(map(str, line)))
    #print(self.getTeam(gameState))
    

    '''
    Your initialization code goes here, if you need any.
    '''

    self.walls = gameState.getWalls().asList()
    self.wallsDict = {wallPos: True for wallPos in self.walls}
    self.walls = gameState.getWalls().data
    self.layout = gameState.data.layout
    self.startState = gameState.getAgentPosition(self.index)
    self.isOnRedTeam = gameState.isOnRedTeam(self.index)
    self.wasPacman = False
    self.inlets = []
    walls = gameState.getWalls()

    if(self.isOnRedTeam):
      middle_index = int( self.layout.width / 2)-1
    else:
      middle_index = int( self.layout.width / 2)
    
    current_inlet_start_y = 0
    for i in range(self.layout.height):
      if(walls[middle_index][current_inlet_start_y]):
        current_inlet_start_y += 1
        i = current_inlet_start_y+1
      if(walls[middle_index][i] and current_inlet_start_y != i):
        self.inlets.append(Inlet((middle_index, current_inlet_start_y), (middle_index, i)))
        current_inlet_start_y = i+1

    """for x in self.wallsDict.keys():
      self.debugDraw([x], [0,0,1])"""
    
    for inlet in self.inlets:
      for i in range(inlet.start_pos[1], inlet.end_pos[1]):
        self.debugDraw([(inlet.start_pos[0], i)], [1,1,0] if self.isOnRedTeam else [0,1,1])

    print("The field sixe is %d %d" % (self.layout.width, self.layout.height))



  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    #actions = gameState.getLegalActions(self.index)
    ##print("choose action")

    ##print(self.getFood(self, gameState))

    '''
    You should change this in your own agent.
    '''
    #return random.choice(actions)

  #target is a 1x2 matrix with the point to go to, e.g. [9,12]


# Function has to be here such that we can reference 'MainAgent'

def astar(maze : list[list[bool]], start : Position, end : Position, agent: MainAgent):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    #print("going from node " + str(start) + " to node " + str(end))

    # Create start and end node
    start_node = Node(None, start)
    end_node = Node(None, end)
    
    # Initialize both open and closed list
    open_list = set()
    closed_list = set()

    # Add the start node
    open_list.add(start_node)

    # Loop until you find the end
    while len(open_list) > 0:
        #print("open list length: " + str(len(open_list)))

        # Get the current node
        current_node = random.sample(open_list, 1)[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.remove(current_node)
        #open_list.pop(current_index)
        closed_list.add(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1] # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[(int)(node_position[0])][int(node_position[1])]:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            if child in closed_list:
                continue

            #for closed_child in closed_list:
             #   if child == closed_child:
              #      continue

            # Create the f, g, and h values
            child.g = current_node.g + position_cost(current_node, agent)
            # We could also use 'agent.getMazeDistance' if we had access to that
            child.h = agent.getMazeDistance(child.position, end_node.position)
            
            #child.h = calculate_h(child,end_node)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.add(child)


# This function is used to determine the punishment weight of 
# the given position
# A pacman for example should not run into a ghost if it is not scared
# also power ups should probably be a priority while choosing a path
# next priority should be food. 
def position_cost(current_node : Node, agent : MainAgent):
  gameState : GameState = agent.getCurrentObservation()
  myState : AgentState = gameState.getAgentState(agent.index)
  observable_enemies = list(filter(
    lambda pos : pos != None,
      map(
        lambda index : gameState.getAgentPosition(index),
        agent.getOpponents(gameState)
      )
      ))
  node_is_enemy = current_node.position in observable_enemies

  if(myState.isPacman):
    node_is_food = agent.getFood(gameState)[int(current_node.position[0])][int(current_node.position[1])]
    node_is_powerup = current_node.position in agent.getCapsules(gameState)

    # TODO ajust magic numbers
    if node_is_enemy:
      return inf if myState.scaredTimer == 0 else 0 # Please don't hurt me :( (but only if you are scary)
    elif node_is_food:
      return 5 # Yummy
    elif node_is_powerup:
      return 1 # even more yummy
    
    return 10 # We could make this dynamic based on the amount of food left

  else: # We are a defender 

    return 1

def find_target_attack_area( agent : MainAgent):
  
  gameState : GameState = agent.getCurrentObservation()
  myState : AgentState = gameState.getAgentState(agent.index)
  observable_enemies = list(filter(
    lambda pos : pos != None,
      map(
        lambda index : gameState.getAgentPosition(index),
        agent.getOpponents(gameState)
      )
      ))

  return (20, 9)

  for nearbypos in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares
    # Get node position
    node_position = (current_node.position[0] + nearbypos[0], current_node.position[1] + nearbypos[1])
    # Create new node
    new_node = Node(current_node, node_position)
    # Append
    nearby.append(new_node)
    foodmatrix =self.getFood(gameState)
    # Loop through nearby
    for nearnode in nearby:
      if foodmatrix[node_position[0],node_position[1]]==1:
        current_node.h-=1 #?
 


    

class Defender(MainAgent):
  def registerInitialState(self, gameState):
    MainAgent.registerInitialState(self, gameState)
    #self.debugDraw([(33,17)], [1,0,0])
    self.path = []
    if(self.index==3):
      self.path = []#astar(gameState.getWalls().data, gameState.getAgentState(self.index).getPosition(),gameState.getAgentState(self.index-1).getPosition())
      print(self.path)
      for i in range(len(self.path)):
        self.debugDraw([self.path[i]], [0,1,0])
    print(path_to_moves(self.path))
    print("I am a Defender ", self.index, "at position ", gameState.getAgentState(self.index).getPosition())
    print("ATTENTION REQUIRED ON LINE 354")
    self.move_index = 0
    self.previousPosition = gameState.getAgentState(self.index).getPosition()

  def chooseAction(self, gameState):
      ##Impelemtn attacker action
    myState = gameState.getAgentState(self.index)
    actions = gameState.getLegalActions(self.index)
    carrying = myState.numCarrying
    eaten = [] #list containing the position where food has been eaten

    #print("I'm agent ", self.index, " at position ", myState.getPosition())

    previous_observation = self.getPreviousObservation()
    if previous_observation is None:
      previous_observation = gameState

    if(self.isOnRedTeam):
      food = gameState.getRedFood()
      old_food = previous_observation.getRedFood()
    else:
      food = gameState.getBlueFood()
      old_food = previous_observation.getBlueFood()
    
    for i in range(0, food.width):
      for j in range(0, food.height):
        if(not food[i][j] and old_food[i][j]):
          #self.debugDraw([(i,j)], [1,0,0])
          eaten.append((i,j))
  
    #print("Legal actions are %s" % actions)
    #print("Possible actions are %s" % self.getPossibleActions(gameState.getAgentPosition(self.index)))


    #Defensive algo

    #First A* test
    """ATTENTION PLEASE: TOY CODE FOR TESTING PURPOSES ONLY"""
    opponents_pos = [(x,gameState.getAgentPosition(x)) for x in self.getOpponents(gameState)]
    opponents_pos = [(x,y) for (x,y) in opponents_pos if y is not None]
    if(len(opponents_pos)>0):
      closest_opponent = min(opponents_pos, key=lambda x: self.getMazeDistance(myState.getPosition(), x[1]))
      x = closest_opponent[0]
      y = closest_opponent[1]
      target= (x,y)
      self.path = astar(self.walls, gameState.getAgentState(self.index).getPosition(), target , self)
    else:
      self.path = astar(self.walls, gameState.getAgentState(self.index).getPosition(), find_target_attack_area(self) , self)
    #self.path = astar(self.walls, gameState.getAgentState(self.index).getPosition(), find_target_attack_area(self), self)
    self.debugDraw(self.path, [0,1,0], True)
    moves = path_to_moves(self.path)
    self.move_index +=1

    if(len(moves) == 0):
      #print("Fine")
      return "Stop"
    if moves[0] not in gameState.getLegalActions(self.index):
      print("Azione illegale")
      return "Stop"
    return moves[0]

    """REMOVE THE ABOVE CODE UP TO HERE AND UNCOMMENT THE FOLLOWING"""

    if(myState.isPacman):
      print("Go to the closest inlet and enter your field") #lo sto facendo andare al centro del campo
      middle_index_x = int( self.layout.width / 2)-1
      vai = False
      index_y = 9
      while (vai==True) :
        if(self.walls[middle_index_x][index_y]):
          index_y+=1
        else :
          vai=True

      self.path = astar(self.walls, gameState.getAgentState(self.index).getPosition(), (middle_index_x,index_y ), self)
      self.debugDraw(self.path, [0,1,0], True)
      moves = path_to_moves(self.path)
      self.move_index +=1
    else:
      if(myState.scaredTimer>0): #same of the next
        print("I should go to the closest pacman to die and respawn")
      else:
        opponents_pos = [(x,gameState.getAgentPosition(x)) for x in self.getOpponents(gameState)]
        opponents_pos = [(x,y) for (x,y) in opponents_pos if y is not None]
        if(len(opponents_pos)>0):
          closest_opponent = min(opponents_pos, key=lambda x: self.getMazeDistance(myState.getPosition(), x[1])) #not sure of this
          print("I should go to the closest opponent to eat him")
          #self.debugDraw([closest_opponent[1]], [1,1,1])
          #self.debugDraw([myState.getPosition()], [0,1,0])
        else:#no opponent reachable
          #i should go to the inlet closest to the 
          print("I should go to the closest inlet and wait to chase a pacman") #stessa cosa di se è pacman
          middle_index_x = int( self.layout.width / 2)-1
          vai = False
          index_y = 9
          while (vai==True) :
            if(self.walls[middle_index_x][index_y]):
              index_y+=1
            else :
              vai=True
          self.path = astar(self.walls, gameState.getAgentState(self.index).getPosition(), (middle_index_x,index_y ), self)
          self.debugDraw(self.path, [0,1,0], True)
          moves = path_to_moves(self.path)
          self.move_index +=1
      #to do so, we compute the A* path to the closest food in the enemy base

    actions = gameState.getLegalActions(self.index)
    return random.choice(actions)

class Attacker(MainAgent):
  def registerInitialState(self, gameState):
    MainAgent.registerInitialState(self, gameState)
    print("I am an Attacker")

  def chooseAction(self, gameState):
      ##Impelemtn attacker action
    myState = gameState.getAgentState(self.index)
    actions = gameState.getLegalActions(self.index)
    carrying = myState.numCarrying
    eaten = []

    previous_observation = self.getPreviousObservation()
    if previous_observation is None:
      previous_observation = gameState

    if(self.isOnRedTeam):
      food = gameState.getRedFood()
      old_food = previous_observation.getRedFood()
    else:
      food = gameState.getBlueFood()
      old_food = previous_observation.getBlueFood()
    
    for i in range(0, food.width):
      for j in range(0, food.height):
        if(not food[i][j] and old_food[i][j]):
          #self.debugDraw([(i,j)], [1,0,0])
          eaten.append((i,j))

    #print("Legal actions are %s" % actions)
    #print("Possible actions are %s" % self.getPossibleActions(gameState.getAgentPosition(self.index)))

    if(myState.isPacman):
      if(not self.wasPacman):
        self.total_food = len(self.getFood(gameState).asList())
      #print("I am pacman")
      if(carrying>self.total_food*GO_BACK_PERCENTAGE_THRESHOLD):
        pass
        #print("I should go back to the closest inlet")      
      else:
                pass

        #print("I should go to the closest food")
    else:
              pass

      #print("Not pacman, I SHOULD GO TO THE ENEMY BASE")
      #to do so, we compute the A* path to the closest food in the enemy base
    myState.wasPacman = myState.isPacman



    actions = gameState.getLegalActions(self.index)
    return random.choice(actions)

    
    """
    
    def astar_flami(self,  startNode,  targetNode, actions: list):
    openList = list(Node)
    closedList = list(Node)
    openList.append(startNode)

    while openList.count > 0:
      currentNode = openList[0] ##todo find node with smallest f value
      openList.remove(currentNode)
      closedList.append(currentNode)
      currentIndex = 0
      for index, item in enumerate(openList):
        if item.f < currentNode.f:
          currentNode = item
          currentIndex = index
      openList.pop(currentIndex)
      closedList.append(currentNode)

      if targetNode == currentNode:
        path = []
        current = currentNode
        while current.parent:
          path.append(current.position)
          current = current.parent
        return path[::-1] # Return reversed path
      
      children = list(Node)
      if (actions.__contains__('North')):
        children.append((currentNode[0][0], currentNode[0][1]+1)) # append node above currentNode
      if (actions.__contains__('South')):
        children.append((currentNode[0][0], currentNode[0][1]-1)) # append node below currentNode
      if (actions.__contains__('West')):
        children.append((currentNode[0][0]-1, currentNode[0][1])) # append node left to currentNode
      if (actions.__contains__('East')):
        children.append((currentNode[0][0]+1, currentNode[0][1])) # append node right to currentNode
      
      for child in children:
        if closedList.__contains__(child):
          continue
        child.g = self.calculateCost(startNode, currentNode)
        child.h = self.calculateCost(currentNode, targetNode)
        child.f = self.calculateCost(startNode, targetNode)
        if (openList.__contains__(child)):
          if (child.g > self.calculateCost(child, currentNode)):
            continue
        openList.append(child)

  def calculateCost(startNode, endNode):
    return abs(startNode[0][0] - endNode[0][0]) + abs(startNode[0][1] - endNode[0][1])
    
    
    """