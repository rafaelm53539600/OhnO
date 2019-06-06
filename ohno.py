#!/usr/bin/env python3
import tkinter as tk
from tkinter import simpledialog,Toplevel
from model import AppModel
from view import Application

        
def main():
    root = tk.Tk()
    root.title("OhnO game")
    root.resizable(0,0)
    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen
    root.withdraw()
    answer = simpledialog.askinteger("Input", "Enter length of matrix (3-23)",
                                     parent=root,
                                     minvalue=3, maxvalue=23,
                                     initialvalue=5)
    if (answer != None):
        root.deiconify()
        appModel = AppModel(answer)
        appModel.scramble()
        app = Application(appModel,root)
        app.mainloop()
        
if __name__ == "__main__":
    main()
