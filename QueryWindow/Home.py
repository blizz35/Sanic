'''
Created on May 21, 2026

@author: admin
'''

from tkinter import ttk
import page

class HomePage(page):
    '''
    classdocs
    '''


    def __init__(self, frame):
        '''
        Constructor
        '''
        ttk.Label(frame, text = "Select the query to run").grid(row = 0, column = 1)
        ttk.Button(frame, text = "Inventory counts by dealer", command = invByDealerSetup).grid(row = 2, column = 0)
        ttk.Button(frame, text = "Inventory counts by group", command = invByGroupSetup).grid(row = 2, column = 1)
        ttk.Button(frame, text = "Inventory counts by make", command = invByMakeSetup).grid(row = 2, column = 2)
        ttk.Button(frame, text = "Import history date search", command = importByDaySetup).grid(row = 3, column = 0)
        ttk.Button(frame, text = "Import history name search", command = importByImportSetup).grid(row = 3, column = 1)