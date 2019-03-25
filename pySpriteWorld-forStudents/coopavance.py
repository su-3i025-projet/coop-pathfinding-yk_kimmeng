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

import random 
import numpy as np
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
        
    path = path[::-1]
    for i in range(len(path)) :
        x,y = path[i]
        path[i] = x, y, i
    
    return path

    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'match'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 15  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 200 # default
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
    l = [i for i in range(len(goalStates))]
    path=[]
    goal = []
    goal = goalStates.copy()
    
    randChoice = random.choice(goalStates)
    
    #on initalise les chemins pour chaque joueurs
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
            
    #    
    non_croisement = []
    for i in range(nbPlayers):
        non_croisement.append([i])    
        
    #jP = 0
    #jR = 0
    for i in range(nbPlayers) :
        for j in range(i+1, nbPlayers):
            for x in path[i] :
                if x in path[j] :#si x dans la liste on fait rien on break
                    '''
                    if path[i].index(x) < path[j].index(x) :
                        if path[i].index(x) != len(path[i]) - 1 :
                            if path[j].index(x) != len(path[j]) - 1 :
                    
                                jP = i
                                jR = j
                    '''
                    break
                if x == path[i][len(path[i])-1] : # si x etant le dernier elem de path 
                    if x not in path[j]:          # n'etant pas dans j 
                        non_croisement[i].append(j) # alors pas de croisement
                        non_croisement[j].append(i) # on ajoute dans leur table
                        
    non_croisement.sort(key = len)
    print(non_croisement)
    '''
    if len(non_croisement[0])!=nbPlayers-1 :
        if len(path[jP]) < len(path[jR])  :
            tmp = non_croisement[jR];
            non_croisement.remove(tmp)
            non_croisement.insert(0,tmp)
    '''                
    print(non_croisement)
        
            
    print(path)                
    # on donne a chaque joueur une fiole a ramasser
    # en essayant de faire correspondre les couleurs pour que ce soit plus simple à suivre
    
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    posPlayers = initStates

    for i in range(iterations):
        
        '''on regarde dans non croisement si vide alors on supprime'''
        for x in non_croisement:
            for y in x :
                print(x, y)
                if(len(path[y]) == 0):
                    x.remove(y)
            if len(non_croisement[0]) == 0 :
                lis = []
                non_croisement.pop(0)
                non_croisement.append(lis)


    
         # on fait bouger chaque joueur séquentiellement
        for j in non_croisement[0] :
             
               
            
             row,col = posPlayers[j]
                #goal = goalStates[j%(len(goalStates))];
            
            
            #for k in range(len(posPlayers)):
                #if k!=j :
                    #wallStates.append(posPlayers[k])
            
            #path = astar((row,col), goal, wallStates)
             if len(path[j]) == 0 :
                    continue
                
             
             x,y, t = path[j][0]
             posPlayers[j] = (x,y)
             players[j].set_rowcol(x,y)
                #print ("pos : ",x,y)
             game.mainiteration()
             col=y
             row=x
             if j in non_croisement[0] :
                 path[j].pop(0);
                
             for l in range(j + 1, nbPlayers) :
                 if j in non_croisement[l] :
                     non_croisement[l].remove(j)
                
                #for k in range(len(posPlayers)):
                    #if k!=j :
                        #wallStates.remove(posPlayers[k])
                         
          
             print(path)
             
                # si on a  trouvé un objet on le ramasse
             if len(path[j]) == 0:
                 if (row,col) in goalStates:
                    
                    o = players[j].ramasse(game.layers)
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
    


