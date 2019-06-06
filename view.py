import tkinter as tk
from color import COLOR

class CellCanvas(tk.Canvas):
    def __init__(self,root,  **kwargs):
        tk.Canvas.__init__(self,root,kwargs)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.scope_id = None
        self.font = ('Times',str(int(self.height/4)),'bold italic')

    def draw(self,model,bg='white'):
        w,h = self.width/2,self.height/2
        self.config(bg=bg)
        self.create_oval(w-(w-2),h-(h-2),
                        w+(w-2),h+(h-2),
                        fill=model.color.name,
                        outline='')
        if model.sticky :
            self.delete(self.scope_id)
            text = (str(model.scope)+'/'+str(model.goal) if model.color == COLOR.BLUE
                    else 'L')
            self.scope_id = self.create_text(w,h,
                                                font=self.font,fill='#fff',
                                                text=text)
    
class Application(tk.Frame):
    def __init__(self, appmodel,master=None):
        tk.Frame.__init__(self, master)
        self.font=('Times','24','bold italic')
        self.appmodel = appmodel
        self.initUI()
        self.grid(sticky=tk.E+tk.W+tk.S+tk.N)
        self.appmodel.update(self)


    def initUI(self):
        
        self.lbl0 = tk.Label(self,font=self.font )
        self.lbl0.grid(sticky=tk.W, row=0, columnspan=4, pady=4, padx=5)
        
        cellFrame = tk.Frame(self)
        cellFrame.grid(row=1, column=0,
                       columnspan=self.appmodel.N, rowspan=self.appmodel.N,
                       sticky=tk.E+tk.W+tk.S+tk.N)

        self.dot = []
        for i in range(0,self.appmodel.N):
            self.dot.append([None]*self.appmodel.N)
            for j in range(0,self.appmodel.N):
                dim = (self.master.winfo_reqheight()/self.appmodel.N)*3 # geometry??
                self.dot[i][j] = CellCanvas(cellFrame, bg='white', width=dim, height=dim)
                self.appmodel.model[i][j].dot = self.dot[i][j]
                self.dot[i][j].draw(self.appmodel.model[i][j])
                self.dot[i][j].grid(row=i,column=j)
                def handler(event,self=self,i=i,j=j): # Trick. See *
                    return self.__buttonHandler(event,i,j)
                self.dot[i][j].bind('<Button-1>',handler)

        self.lbl1 = tk.Label(self, font=self.font )
        self.lbl1.grid(sticky=tk.W, row=self.appmodel.N+1, columnspan=4, pady=4, padx=5)

        
# * import partial from functiontools to implement closures...

    # Controller action
    # Model is accesed
    def __buttonHandler(self,event,i,j):
        if (self.appmodel.model[i][j].sticky == True):
            self.bell()
        else:
            self.appmodel.fireChange(i,j,self)
