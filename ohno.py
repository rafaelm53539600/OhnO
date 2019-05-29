#!/usr/bin/env python3
import tkinter as tk
from tkinter import simpledialog,Toplevel
from model import AppModel
from view import Application

        
def main():
    root = tk.Tk()
    root.title("OhnO game")
    root.resizable(0,0)
    root.withdraw()
    answer = simpledialog.askinteger("Input", "Enter length of matrix (3-23)",
                                     parent=root,
                                     minvalue=3, maxvalue=23,
                                     initialvalue=3)
    if (answer != None):
        root.deiconify()
        appModel = AppModel(answer)
        app = Application(appModel,root)
        app.mainloop()
        
if __name__ == "__main__":
    main()