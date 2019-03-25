# -*- coding: utf-8 -*-

# Nicolas, 2015-11-18

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo
import heapq
import random 
import numpy as np
import sys


# ---- ---- ---- ---- ---- ----
# ---- Misc                ----
# ---- ---- ---- ---- ---- ----
class Noeud :
    def __init__(self, position=None, parent=None):
        self.position = position
        self.parent = parent


def h(a, b):
    x1,y1 = a #depart
    x2,y2 = b #arrive
    
    return abs(x2-x1) + abs(y2-y1)


def g(a, b):
    x1,y1 = a #depart
    x2,y2 = b #arrive
    
    return abs(x2-x1) + abs(y2-y1)


def estBut(node, goal) :
    my_pos, parent_pos = node
    goal_pos, pg_pos = goal
    if my_pos == goal_pos and parent_pos == pg_pos:
        return True
    else :
        return False
    

def expand(node, wall):
    x, y = node.position
    res = []
    for newX,newY in [(0,-1),(0,1),(-1,0),(1,0)] :
        pos_final = newX+x,newY+y
        if(pos_final) not in wall: # créer les noeuds fils seulement hors des murs
            res.append(Noeud(pos_final, node))
    return res

def choisir(frontiere):
    min_f, node = frontiere[0]
    for f,n in frontiere :
        if f<min_f :
            min_f = f
            node = n
    frontiere.remove((min_f,node))
    return (min_f,node)


def astar(initStates, goalStates, wallStates):
    nodeInit = Noeud(initStates)
    goal = goalStates
    frontiere = []
    reserve = []
    
    frontiere.append ((g(nodeInit.position, nodeInit.position)+h(nodeInit.position,goal),nodeInit))
    
    bestNoeud = nodeInit
    
    while frontiere != [] and not estBut(bestNoeud.position, goal) :
        (min_f, bestNoeud) = choisir(frontiere)
        
        if bestNoeud.position not in reserve :
            reserve.append(bestNoeud.position)
            nouveauxNoeuds = expand(bestNoeud, wallStates)
            
            for fils in nouveauxNoeuds :
                f = g(nodeInit.position,fils.position) + h(fils.position, goal)

                frontiere.append((f,fils))


            
    path = []
    while bestNoeud.parent != None :
        path.append(bestNoeud.position)
        bestNoeud = bestNoeud.parent
    
    return path

# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    name = _boardname if _boardname is not None else 'tictactoe'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 100 # default
    if len(sys.argv) == 5:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    

    
    #-------------------------------
    # Building the matrix
    #-------------------------------
       
           
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    # on localise tous les objets ramassables
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print ("Goal states:", goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)
        
    
    #-------------------------------
    # Building the best path with A*
    #-------------------------------
    path = astar(initStates[0], goalStates[0], wallStates)
    
    print("Chemin trouvé : ",path)
    
        
    #-------------------------------
    # Moving along the path
    #-------------------------------
        
    # bon ici on fait juste un random walker pour exemple...
    

    row,col = initStates[0]
    #row2,col2 = (5,5)

    for i in range(len(path)):
        x,y = path[len(path)-i-1]
        player.set_rowcol(x,y)
        print ("pos : ",x,y)
        game.mainiteration()
        col=y
        row=x
            
        # si on a  trouvé l'objet on le ramasse
        if (row,col)==goalStates[0]:
            o = game.player.ramasse(game.layers)
            game.mainiteration()
            print ("Objet trouvé!", o)
            break
        
    path = astar((x,y), (10,10), wallStates)
    for i in range(len(path)):
        x,y = path[len(path)-i-1]
        player.set_rowcol(x,y)
        print ("pos : ",x,y)
        game.mainiteration()
        col=y
        row=x
        
        if (row,col)==(10,10):
            o = game.player.depose(game.layers)
            game.mainiteration()
            print ("Objet déposé!", o)
            break
    player.set_rowcol(10,9)
    print ("pos : ",x,y)
    game.mainiteration()    
    

    pygame.quit()
    
        
    
   

if __name__ == '__main__':
    main()
    


