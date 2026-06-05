'''
Created on May 21, 2026

@author: admin
'''

import tkinter as tk
from tkinter import ttk
import Pages
import sys, os

class Window():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        root = tk.Tk()
        root.title("Sanic")
        
        def resource(relativePath):
            basePath = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(basePath, relativePath)
        
        root.iconbitmap(resource("sanic.ico"))
        
        # root.geometry("800x450")
        # bg = tk.PhotoImage(file = resource("sanicBack.png"))
        
        
        # tk.Label(root, image = bg).place(x = 0, y = 0)
        
        frm = ttk.Frame(root, padding = 100)#, bg = '')
        # root.wm_attributes('-transparentcolor')
        frm.grid()
                
        Pages.homePage(frm)
        
        root.mainloop()