# -*- coding: utf-8 -*-

# Nicolas, 2015-11-18

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from ontology import Ontology
import pygame

import random 
import sys

#MISC

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
        n,m = pos_final
        if n<0 or m<0 :
            continue
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
    
    return path[::-1]

    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer1bis'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 20  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 100 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()

    #-------------------------------
    # Initialisation
    #-------------------------------
       
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    score = [0]*nbPlayers
    
    
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
    # Placement aleatoire des fioles 
    #-------------------------------
    path=[]
    goal = []
    goal = goalStates.copy()
    
    randChoice = random.choice(goalStates)
    
    
    if nbPlayers == len(goal):
        for i in range(nbPlayers) :
            randChoice = random.choice(goal)
            goal.remove(randChoice)
            list = []
            for g in goalStates :
                if g != randChoice :
                    list.append(g)
            
            for l in list :
                wallStates.append(l)
            path.append(astar(initStates[i], randChoice, wallStates))
            for l in list :
                wallStates.remove(l)
    else :
        for i in range(nbPlayers) :
            randChoice = random.choice(goal)
            list = []
            for g in goalStates :
                if g != randChoice :
                    list.append(g)
            
            for l in list :
                wallStates.append(l)
            path.append(astar(initStates[i], randChoice, wallStates))
            for l in list :
                wallStates.remove(l)
            
    
    # on donne a chaque joueur une fiole a ramasser
    # en essayant de faire correspondre les couleurs pour que ce soit plus simple à suivre
    
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
        
    # bon ici on fait juste plusieurs random walker pour exemple...
    
    posPlayers = initStates

    for i in range(iterations):
        
        for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement
            row,col = posPlayers[j]
            
            pos_other_player = []
            for k in range(len(posPlayers)):
                if k!=j :
                    pos_other_player.append(posPlayers[k])

            if path[j] == [] :
                continue
            x,y = path[j][0]
            if (x,y) in pos_other_player :
                for pos in pos_other_player :
                    wallStates.append(pos)
                path[j] = astar(posPlayers[j], path[j][len(path[j])-1], wallStates)
                for pos in pos_other_player :
                    wallStates.remove(pos)
                x,y = path[j][0]    
                
            posPlayers[j] = (x,y)
            players[j].set_rowcol(x,y)

            game.mainiteration()
            col=y
            row=x
            path[j].pop(0)
            
            # si on a  trouvé un objet on le ramasse
            if (row,col) in goalStates:
                players[j].ramasse(game.layers)
                game.mainiteration()
                print ("Objet trouvé par le joueur ", j)
                goalStates.remove((row,col)) # on enlève ce goalState de la liste
                score[j]+=1
                
                # et on remet un même objet à un autre endroit
              
                break
            
    print ("scores:", score)
    pygame.quit()

if __name__ == '__main__':
    main()
    


