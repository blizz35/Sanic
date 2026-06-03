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
        frm = ttk.Frame(root, padding=100)
        frm.grid()
        
        def resource(relativePath):
            basePath = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(basePath, relativePath)
        
        root.iconbitmap(resource("vincueblack.ico"))
        
        Pages.homePage(frm)
        
        root.mainloop()