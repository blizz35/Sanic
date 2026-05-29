'''
Created on May 19, 2026

@author: admin
'''

# import json
import tkinter as tk
from tkinter import ttk
#    from tkinter import messagebox
# from os import getenv
# from dotenv import load_dotenv
# from mssql_python import connect 
import Window


try:
    import pyi_splash
    pyi_splash.close()
except:
    pass

Window.Window()

# root = tk.Tk()
# root.title("Common Queries")
# frm = ttk.Frame(root, padding=100)
# frm.grid()

# homeSetup()