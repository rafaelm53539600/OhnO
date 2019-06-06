#!/usr/bin/env python3
'''
Sort of "distributed Model", BroadCast Algorithm.

       N             N             N             N              
       |             |             |             |              
    +-----+       +-----+       +-----+       +-----+           
    |     |       |     |       |     |       |     |           
 W--|     |--E W--|     |--E W--|     |--E W--|     |--E        
    |     |       |     |       |     |       |     |           
    +-----+       +-----+       +-----+       +-----+           
       |             |             |             |              
       S             S             S             S                   
       N             N             N             N                   
       |             |             |             |                   
    +-----+       +-----+       +-----+       +-----+                
    |     |       |     |       |     |       |     |                
 W--|     |--E W--|     |--E W--|     |--E W--|     |--E             
    |     |       |     |       |     |       |     |                
    +-----+       +-----+       +-----+       +-----+                
       |             |             |             |                   
       S             S             S             S              
       N             N             N             N              
       |             |             |             |              
    +-----+       +-----+       +-----+       +-----+           
    |     |       |     |       |     |       |     |           
 W--|     |--E W--|     |--E W--|     |--E W--|     |--E        
    |     |       |     |       |     |       |     |           
    +-----+       +-----+       +-----+       +-----+           
       |             |             |             |              
       S             S             S             S       
       N             N             N             N       
       |             |             |             |       
    +-----+       +-----+       +-----+       +-----+    
    |     |       |     |       |     |       |     |    
 W--|     |--E W--|     |--E W--|     |--E W--|     |--E 
    |     |       |     |       |     |       |     |    
    +-----+       +-----+       +-----+       +-----+    
       |             |             |             |       
       S             S             S             S       
            

After each user-interaction,next class invariants
must hold . By proceeding so, you will get an effciency of O(n) (vs O(n^3))
Notation may be exhausting....(pseudo-ocl)
This may require textual description.

INV(self.model[i][j].scope)=
  : self.model[i][j].scope = sum \c : CARDINAL(c) :
                             self.model[i][j].neigh.c.scope

INV(self.model[i][j].neigh.c.scope) =
  : self.color = RED | GRAY  
       self.model[i][j].neigh.c.scope)=-1
  : self.color = BLUE:
     self.model[i][j].neigh.oposit(self.neigh.card).node == None
       self.model[i][j].neigh.(self.neigh.card).scope)=0
     self.model[i][j].neigh.oposit(self.neigh.card).node != None
       self.model[i][j].neigh.(self.neigh.card).scope)=
               self.prev(oposit(self.neigh.card)).scope + 1 

INV(self.pending)=
   :self.model[i][j].color = BLUE and self.model[i][j].sticky 
      self.model[i][j].scope == self.model[i][j].goal <-> (i,j) \not in pending
   :self.model[i][j].color = BLUE and !self.model[i][j].sticky 
      self.model[i][j].scope > 0 <-> (i,j) \not in pending              

INV(self.total)=
   self.total = \sum i,j : (i,j) in (self.N x self.N) : self.model[i][j].color!=GRAY

'''


from color import COLOR
from cardinal import CARDINAL
from random import Random


class CellModel:
    # self.parent reference breaks decoupling (shortcut)
    # Distributed algorithm results more simple
    def __init__(self,parent,i,j,view=None):
        self.parent=parent    
        self.color = COLOR.GRAY
        self.sticky = False
        self.i = i
        self.j = j
        self.goal = None
        self.dot = view
        # TODO

    #Pre : TODO
    def stick(self):
        self.sticky = True
        self.goal = self.scope

        
    #O(4n) !!. vs. O(n^3)
    # Pre: all INV
    # Post: all INV
    def fireChange(self):
        self.color = self.color.succ()
        #Restoring INV(self.neigh.card.scope)
        for towards in CARDINAL:
            prev = self.neighboors[towards.opposite()]['node']
            self.neighboors[towards.opposite()]['scope'] = (
                -1  if (self.color != COLOR.BLUE) else
                0 if (prev==None) else
                prev.neighboors[towards.opposite()]['scope'] + 1)
        #Restore INV(self.scope)
        # O(4) 
        self.scope=sum([self.neighboors[cardinal]['scope'] for cardinal in CARDINAL])
        #Restore INV(self.parent.total)
        self.parent.total = (self.parent.total + 1  if (self.color == COLOR.BLUE) else
                             self.parent.total - 1  if (self.color == COLOR.GRAY) else
                             self.parent.total)
        #Restore INV(self.pending)
        if (self.color == COLOR.BLUE):
            if (self.scope>0):
                self.parent.pending.discard((self.i,self.j))
            else:
                self.parent.pending.add((self.i,self.j))
        else:
            self.parent.pending.discard((self.i,self.j))
        #BroadCast
        for towards in CARDINAL:
            next = self.neighboors[towards]['node']
            next != None and next.color == COLOR.BLUE and next.propagate(towards,self)
        #Update view
        self.dot!=None and self.dot.draw(self)
        return

    '''
    Pre : self.color = BLUE and all INV
    Post: all INV
    '''
    def propagate(self,towards,previous):
        #Restoring INV(self.neigh.card.scope)            
        self.neighboors[towards.opposite()]['scope'] = (
            previous.neighboors[towards.opposite()]['scope'] + 1
        )
        #Restore INV(self.scope)
        self.scope=sum([self.neighboors[cardinal]['scope'] for cardinal in CARDINAL])
        #Restore INV(self.pending)
        if self.sticky:
            if (self.scope==self.goal): 
                self.parent.pending.discard((self.i,self.j))
            else:
                self.parent.pending.add((self.i,self.j))
        else:
            if (self.color == COLOR.BLUE):
                if (self.scope>0):
                    self.parent.pending.discard((self.i,self.j))
                else:
                    self.parent.pending.add((self.i,self.j))                   
        #Broad cast
        next = self.neighboors[towards]['node']
        next != None and next.color == COLOR.BLUE and next.propagate(towards,self)
        #Update view
        self.dot!=None and self.dot.draw(self)
        return

class AppModel():
    # POST : INV
    def __init__(self,N):
        self.N = N
        self.model= [[CellModel(self,i,j) for j in range(N)] for i in range(N) ]
        # build the web
        for i in range(N):
            for j in range(N):
                print(i,j)
                self.model[i][j].neighboors = {
                    CARDINAL.NORTH:{ 'node': (None if i==0 else
                                              self.model[i-1][j]),'scope' : -1},
                    CARDINAL.EAST :{ 'node': (None if j==(N-1)else
                                              self.model[i][j+1]),'scope' : -1},
                    CARDINAL.SOUTH:{ 'node': (None if i==(N-1) else
                                              self.model[i+1][j]),'scope' : -1},
                    CARDINAL.WEST :{ 'node': (None if j==0 else
                                              self.model[i][j-1]),'scope' : -1}
                }
        self.total = 0
        self.pending = set()
        #Assert all INV
        # ALl GRAY
        for i in range(self.N):
            for j in range(self.N):
                self.model[i][j].fireChange() #blue
                if (Random().randint(0,1)==1):
                    self.model[i][j].fireChange() #red

        for i in range(self.N):
            for j in range(self.N):
                if (self.model[i][j].color == COLOR.BLUE) and (self.model[i][j].scope==0):
                    self.model[i][j].fireChange() # red
                
        #Let's do
        for i in range(self.N):
            for j in range(self.N):
                if (Random().randint(0,1)==0): # stick
                    self.model[i][j].stick()


        # Assert solved problem
        
        #Then drop off not sticky dots
        for i in range(self.N):
            for j in range(self.N):
                if (self.model[i][j].sticky == False):
                    self.model[i][j].fireChange()
                    if (self.model[i][j].color==COLOR.RED):
                        self.model[i][j].fireChange()
        #Transient values for active pending
        self.faulty=None

    def update(self,view):
        text1 = str(((1.0*self.total)/(self.N*self.N))*100)[:3]+'%'
        text0=str(self.N)+' X '+str(self.N)
        if (self.total == self.N*self.N):
            if (len(self.pending)>0):
#                print(self.pending)
                faulty=self.pending.copy().pop()
                self.faulty = self.model[faulty[0]][faulty[1]]
                self.faulty.dot.draw(self.faulty,'black')
                text0='Check '+str(faulty)
            else:
                text0='SOLVED!'
        view.lbl0.config(text=text0)
        view.lbl1.config(text=text1)
        return 
                                 
        
    def fireChange(self,i,j,view):
        self.faulty!=None and self.faulty.dot.draw(self.faulty)
        self.faulty = None
        self.model[i][j].fireChange() 
        self.update(view)
