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
               first = 'Defender', second = 'Attacker'):
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

  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)

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
      
