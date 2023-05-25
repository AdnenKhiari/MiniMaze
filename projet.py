from enum import Enum
from msvcrt import getch
import os
import time
import numpy as np
from pynput import keyboard
from pynput.keyboard import Key
from queue import PriorityQueue




    
class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Entity():
    def __init__(self,x,y,map) -> None:
        self.x=x
        self.y=y
        self.map = map
    def go(self,d):
        if(d == Direction.DOWN):
            if(self.map.empty(self.x,self.y+1)):
                self.y=self.y+1
        elif (d == Direction.UP):
            if(self.map.empty(self.x,self.y-1)):
                self.y=self.y-1
        elif (d == Direction.LEFT):
            if(self.map.empty(self.x-1,self.y)):
                self.x=self.x-1      
        elif (d == Direction.RIGHT):
            if(self.map.empty(self.x+1,self.y)):
                self.x=self.x+1      
        self.y = min(max(self.y,0),self.map.h-1)
        self.x = min(max(self.x,0),self.map.w-1)
    def getPosition(self):
        return (self.x,self.y)
    def getDistance(x,y,_x,_y):
        return abs(x-_x) + abs(y-_y)
class Monster(Entity):
    def __init__(self, x, y,map) -> None:
        super().__init__(x, y,map)
class Player(Entity):
    def __init__(self, x, y,map) -> None:
        super().__init__(x, y,map)

dir = Direction.DOWN
def getDirection(pos1,pos2):
    if(pos1[0]<pos2[0]):
        return Direction.RIGHT
    if(pos1[0]>pos2[0]):
        return Direction.LEFT
    if(pos1[1]<pos2[1]):
        return Direction.DOWN
    if(pos1[1]>pos2[1]):
        return Direction.UP
def on_key_release(key):
    global dir
    if key == Key.right:
        
        #print("Right key clicked")
        dir =  Direction.RIGHT
    elif key == Key.left:
        #print("Left key clicked")
        dir =  Direction.LEFT

    elif key == Key.up:
        #print("Up key clicked")
        dir =  Direction.UP

    elif key == Key.down:
        #print("Down key clicked")
        dir =  Direction.DOWN


    elif key == Key.esc:
        exit()
        
class Map():
    p = None
    enemies = []
    enemyPath = []
    def __init__(self,w,h,en) -> None:
        self.w = w
        self.h = h
        self.grid = [["#" for __ in range(2*w)] for _ in range(2*h)]
        self.p=Player(5,5,self)
        for e in range(en):
            self.enemies.append(Monster(np.random.randint(0,self.w),np.random.randint(0,self.h),self))
    def __str__(self) -> str:
        s = ""
        for i,row in enumerate(self.grid):
            row = row+[]
            
            for en_path in self.enemyPath:
                for point in en_path:
                    if(point[1] == i):
                        row[point[0]] = '❌'
            
            if(i == self.p.y):
                row[self.p.x] = '🤖'
            for e in self.enemies:
                if(i == e.y):
                    row[e.x] = '👾'

            s+=''.join(row).replace("#",'🧱').replace("-",'🚪').replace(".",'⚪')+"\n"
            #s+=''.join(row)+"\n"

        return s
    def AStar(self,pos1,pos2):
        #print(pos1,pos2)
        open = PriorityQueue()
        closed = {}
        pred = {}
        pred[pos1] = pos1
        open.put((Entity.getDistance(*pos1,*pos2),pos1))
        found = False
        while(not open.empty()):
            current = open.get()
            current_position = current[1]
            #print(current)
            if(current_position == pos2):
                found = True
                break
            current_score = current[0] - Entity.getDistance(*current_position,*pos2)
            adj = list(filter(lambda d: self.notWall(*d),[(current_position[0]+1,current_position[1]),
                                                        (current_position[0]-1,current_position[1]),
                                                        (current_position[0],current_position[1]+1),
                                                        (current_position[0],current_position[1]-1)])
                       )
            #print(f"Potential Next : {adj}")
            for item in adj:
                new_item_score = current_score+1
                # if(item in closed):
                #     old_item_score = closed[item]
                #     if(old_item_score < new_item_score):
                #         new_item_score = old_item_score
                #         closed.pop(item)     
                if(item not in closed):
                    open.put((new_item_score+Entity.getDistance(*item,*pos2),item))
                    pred[item] = current_position
            closed[current_position] = current_score
        last = pos2
        path= []
        if(not found):
            return path
       # print(pred)
        while(pred[last] != last):
            path.append(last)
            #print(last)
            last = pred[last]
        #print(path)
        path.reverse()
        return path
        
        
    def updateEnemies(self):
        self.enemyPath = []
        for e in self.enemies:
            res = self.AStar(e.getPosition(),self.p.getPosition())
            #print(res)
            self.enemyPath.append(res)
            if(len(res) > 0):
                e.go(getDirection(e.getPosition(),res[0]))
        
        #print(self.enemyPath)
    def valid(self,x,y):
        return not (x <= -1 or x >= self.w or y <= -1 or y >= self.h)
    def empty(self,x,y):
        return self.valid(x,y) and self.grid[y][x] != '#'
    def notWall(self,x,y):
        return self.valid(x,y) and self.grid[y][x] != '#' and  self.grid[y][x] != '-'
    def generateRandomMap(self) -> None:
        nextrow = []
        self.grid = []
        for j in range(self.h//2):
            self.grid.extend([["#","."],[]])
            row = [i for i in range(self.w)]
            for i in range(1,self.w//2):
                isWall =  np.random.uniform() > 0.5
                if(not isWall):
                    row[i] = row[i-1]
                    self.grid[2*j].append(".")
                    self.grid[2*j].append(".")
                else:
                    
                    self.grid[2*j].append(".")
                    self.grid[2*j].append("#" if np.random.rand() > 0.7 else "-")
            nextrow = [self.h*j+i for i in range(self.w)]
            for i in range(self.w//2):
                isHorizontalWall = np.random.uniform() > 0.5
                if(not isHorizontalWall):
                    nextrow[i] = row[i]
                    self.grid[2*j+1].append(".")
                    self.grid[2*j+1].append(".")
                else:
                    self.grid[2*j+1].append(".")
                    self.grid[2*j+1].append("#" if np.random.rand() > 0.7 else "-")
#Init
m = Map(40,10,2)
print(m.generateRandomMap())
with keyboard.Listener(on_release=on_key_release) as listener:
    while(True): 
        
        #update loop :
        m.p.go(dir)
        
        m.updateEnemies()
        if(len(list(filter(lambda p: p == m.p.getPosition(),map(lambda d: d.getPosition(),m.enemies))))>0):
            print("YOU LOST , Press to respawn")
            input()
            m.p.x = np.random.randint(m.w)
            m.p.y = np.random.randint(m.h)

        # render loop 
        os.system("cls")
        print("\n")
        print(m)
        print("\n")
        time.sleep(0.5)
