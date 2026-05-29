'''
Created on May 21, 2026

@author: admin
'''

from abc import ABC, abstractmethod
from tkinter import ttk

class page(ABC):
    '''
    classdocs
    '''
    
    def clearScreen(self, frame):
        for item in frame.winfo_children():
            item.destroy()
            
        ttk.Button(frame, text = 'Back', command = backHome).grid(row = 0, column = 1)
        
    def backHome(self, frame):
        for item in frame.winfo_children():
            item.destroy()
            
        # homeSetup()
    
    def homeSetup(self, frame):
        ttk.Label(frame, text = "Select the query to run").grid(row = 0, column = 1)
        ttk.Button(frame, text = "Inventory counts by dealer", command = invByDealerSetup).grid(row = 2, column = 0)
        ttk.Button(frame, text = "Inventory counts by group", command = invByGroupSetup).grid(row = 2, column = 1)
        ttk.Button(frame, text = "Inventory counts by make", command = invByMakeSetup).grid(row = 2, column = 2)
        ttk.Button(frame, text = "Import history date search", command = importByDaySetup).grid(row = 3, column = 0)
        ttk.Button(frame, text = "Import history name search", command = importByImportSetup).grid(row = 3, column = 1)


    def __init__(self):
        '''
        Constructor
        '''
        