'''
Created on May 21, 2026

@author: admin
'''

import tkinter as tk
from tkinter import ttk
import Pages


class Window():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        root = tk.Tk()
        root.title("Common Queries")
        frm = ttk.Frame(root, padding=100)
        frm.grid()
        
        Pages.homePage(frm)
        
        root.mainloop()