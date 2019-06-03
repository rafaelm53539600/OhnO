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
   self.total = \sum c : c in (self.N x self.N) : self.model[i][j].color!=GRAY

'''


from color import COLOR
from cardinal import CARDINAL
from random import Random


lot=Random()
class CellModel:
    # dot is None when not references a view.
    def __init__(self,parent,i,j):
        self.parent=parent    #Needed to update global
        self.color = COLOR.GRAY
        self.sticky = False
        self.i = i
        self.j = j
        self.dot = None

    def stick(self,color):
        self.sticky = False
        self.goal = None
        self.fireChange() # One shot for Blue
        if (color == COLOR.RED):
            self.fireChange() # two shots for Red


    #O(4n) !!. vs. O(n^3)
    # Pre: self.sticky = False and INV(self.card.scope)
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
        # Assert self.sticky == False
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
    Pre : self.color = BLUE and INV(parent.pending)!!
    Post: INV(parent.pending)
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
        # ALl GRAY
        for i in range(self.N):
            for j in range(self.N):
                self.model[i][j].stick(COLOR(lot.randint(1,2)))

        for i in range(self.N):
            for j in range(self.N):
                if (self.model[i][j].color == COLOR.BLUE) and (self.model[i][j].scope==0):
                    self.model[i][j].fireChange() #to red
                
        #Let's do
        for i in range(self.N):
            for j in range(self.N):
                if (lot.randint(0,1)==0): # stick
                    self.model[i][j].sticky = True
                    self.model[i][j].goal = self.model[i][j].scope

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





        
#blues=[(0,1), (0,2), (1,1)]
#reds =[(0,0)]
# for i in blues :
#     self.model[i[0]][i[1]].stick(COLOR.BLUE)
# for i in reds :
#     self.model[i[0]][i[1]].stick(COLOR.RED)

