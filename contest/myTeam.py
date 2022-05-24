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


from glob import glob
from captureAgents import CaptureAgent

import random, time, util
from game import Directions
import game

GO_BACK_PERCENTAGE_THRESHOLD = 0.5

class Inlet:
  def __init__(self, start_pos, end_pos):
    self.start_pos = start_pos
    self.end_pos = end_pos
    self.size = util.manhattanDistance(start_pos, end_pos)



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

class Node():
  x_pos
  y_pos
  f
  g
  h

class MainAgent(CaptureAgent) :
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    #for line in self.getFood(gameState):
    ##  print('  '.join(map(str, line)))
    #print(self.getTeam(gameState))
    

    '''
    Your initialization code goes here, if you need any.
    '''

    self.walls = gameState.getWalls().asList()
    self.wallsDict = {wallPos: True for wallPos in self.walls}
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


class Defender(MainAgent):
  def registerInitialState(self, gameState):
    MainAgent.registerInitialState(self, gameState)
    self.debugDraw([(33,17)], [1,0,0])
    print("I am a Defender")

  def chooseAction(self, gameState):
      ##Impelemtn attacker action
    myState = gameState.getAgentState(self.index)
    actions = gameState.getLegalActions(self.index)
    carrying = myState.numCarrying
    eaten = [] #list containing the position where food has been eaten

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
          self.debugDraw([(i,j)], [1,0,0])
          eaten.append((i,j))
  
    #print("Legal actions are %s" % actions)
    #print("Possible actions are %s" % self.getPossibleActions(gameState.getAgentPosition(self.index)))

    #Defensive algo

    if(myState.isPacman):
      print("Go to the closest inlet and enter your field")
    else:
      if(myState.scaredTimer>0):
        print("I should go to the closest pacman to die and respawn")
      else:
        opponents_pos = [(x,gameState.getAgentPosition(x)) for x in self.getOpponents(gameState)]
        opponents_pos = [(x,y) for (x,y) in opponents_pos if y is not None]
        if(len(opponents_pos)>0):
          closest_opponent = min(opponents_pos, key=lambda x: self.getMazeDistance(myState.getPosition(), x[1])) #not sure of this
          print("I should go to the closest opponent to eat him")
          self.debugDraw([closest_opponent[1]], [1,1,1])
          self.debugDraw([myState.getPosition()], [0,1,0])
        else:#no opponent reachable
          #i should go to the inlet closest to the 
          print("I should go to the closest inlet and wait to chase a pacman")
      #to do so, we compute the A* path to the closest food in the enemy base

    actions = gameState.getLegalActions(self.index)
    return random.choice(actions)

  #target is a 1x2 matrix with the point to go to, e.g. [9,12]
  def astar(self, startNode, targetNode, actions: list):
    openList = list()
    closedList = list()
    openList.append(startNode)

    while openList.count > 0:
      currentNode = (0,0) ##todo find node with smallest f value
      openList.remove(currentNode)
      closedList.append(currentNode)
      if targetNode == currentNode:
        return True ##we reached the target
      
      children = list()
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
        child_g = self.calculateCost(startNode, currentNode)
        child_h = self.calculateCost(currentNode, targetNode)
        child_f = self.calculateCost(startNode, targetNode)
        if (openList.__contains__(child)):
          if (child_g > self.calculateCost(child, currentNode)):
            continue
        openList.append(child)

  def calculateCost(startNode, endNode):
    return abs(startNode[0][0] - endNode[0][0]) + abs(startNode[0][1] - endNode[0][1])



    


class Attacker(MainAgent):
  def registerInitialState(self, gameState):
    MainAgent.registerInitialState(self, gameState)
    print("I am an Attacker")

  def chooseAction(self, gameState):
      ##Impelemtn attacker action
    myState = gameState.getAgentState(self.index)
    actions = gameState.getLegalActions(self.index)
    carrying = myState.numCarrying

    #print("Legal actions are %s" % actions)
    #print("Possible actions are %s" % self.getPossibleActions(gameState.getAgentPosition(self.index)))

    if(myState.isPacman):
      if(not self.wasPacman):
        self.total_food = len(self.getFood(gameState).asList())
      print("I am pacman")
      if(carrying>self.total_food*GO_BACK_PERCENTAGE_THRESHOLD):
        print("I should go back to the closest inlet")      
      else:
        print("I should go to the closest food")
    else:
      print("Not pacman, I SHOULD GO TO THE ENEMY BASE")
      #to do so, we compute the A* path to the closest food in the enemy base
    myState.wasPacman = myState.isPacman



    actions = gameState.getLegalActions(self.index)
    return random.choice(actions)
      
