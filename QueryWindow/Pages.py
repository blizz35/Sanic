'''
Created on May 21, 2026

@author: admin
'''

from abc import ABC, abstractmethod
from tkinter import ttk
import tkinter as tk
from mssql_python import connect 
# from _types import NoneType

class page(ABC):
    '''
    classdocs
    '''    
    
    conn = connect("Server=192.168.2.19;Encrypt=yes;TrustServerCertificate=yes;Authentication=SqlPassword;UID=integration;PWD=integration")
    idInputCharLimit = 6
    textInputCharLimit = 20
    dayInputCharLimit = 3
    
    def clearScreen(self):
        for item in self.frame.winfo_children():
            item.destroy()
            
        ttk.Button(self.frame, text = 'Home', command = self.backHome).grid(row = 0, column = 1)        
        
    def backHome(self):
        for item in self.frame.winfo_children():
            item.destroy()
            
        homePage(self.frame)
        
    def formatTable(self, tableString):
        recordString = str(tableString).replace('[', '').replace(']', '')
        recordString = recordString.replace('), (', '\n')
        recordString = recordString.replace('(', '').replace(')', '')
        recordString = recordString.replace("'", '').replace("'", '')

        return recordString

    def charCheck(self, event, charnum, fieldIn):
        maxChars = charnum
        self.idEnter = fieldIn
    
        text = self.idEnter.get("1.0", "end-1c")
        textLen = len(text)
        if textLen >= maxChars and event.keysym not in {'BackSpace', 'Delete', 'Return'}: 
            return 'break'
        
    # def setup(self, msg):
    #     pass
    #
    # def pull(self, event):
    #     pass
    
    def __init__(self, frame):
        '''
        Constructor
        '''        
        self.frame = frame
        
        # @property
        # @abstractmethod
        # def conn(self):
        #     pass
        
class oneInPage(page, ABC):
    
    def setup(self, msg):
        self.msg = msg
        
        self.clearScreen()
        resetButton = ttk.Button(self.frame, text = 'Reset', command = lambda: self.invByDealerSetup(''))
        resetButton.grid(row = 0, column = 2)
        
        self.idLabel = ttk.Label(self.frame)
        self.idLabel.grid(row = 1, column = 1)
        self.idInput = tk.Text(self.frame, height = 1, width = 6)    
        self.idInput.grid(row = 2, column = 1)
        
        if msg == 'blank field':
            ttk.Label(self.frame, text = 'You done goofed').grid(row = 4, column = 1)
        elif msg == 'not a client':
            ttk.Label(self.frame, text = 'Not a client').grid(row = 4, column = 1)
        elif msg == 'not a number':
            ttk.Label(self.frame, text = 'Not a number').grid(row = 4, column = 1)
        
        self.idInput.focus_set()
        
        # self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        # self.idInput.bind("<Return>", self.invByDealerPull, add = "+")
        
        self.sendButton = ttk.Button(self.frame, text = "Send")
        self.sendButton.grid(row = 3, column = 1)
        # sendButton.bind("<Button-1>", self.invByDealerPull)
        
        self.setupUpdate()
    
    def pull(self, event):
        dealerID = self.idInput.get("1.0", "end-1c")
        
        if dealerID == '':
            self.setup('blank field')
        elif dealerID.isnumeric():
            cursor = self.conn.cursor()
            cursor.execute("select top 1 dealerID from admin..dealer where exists (select dealerid from admin..dealer where dealerid = " + dealerID + " and clientind = 1)")
            sqlCheck = cursor.fetchone()
            
            if type(sqlCheck) is NoneType:
                self.setup('not a client')
            else:    
                self.clearScreen()
                
                
            
                sqlQueryIn = """select case when listingtypeid = 1 then 'New' else 'Used' end, 
                case when donotexport = 0 then 'Off Hold' else 'On Hold' end, 
                count(vin) 
                from dealersite..inventory 
                where dealerid = 
                and inventorystatusid = 1 
                group by listingtypeid, donotexport 
                order by listingtypeid, donotexport"""
                
                sqlQuery = sqlQueryIn.replace("where dealerid = ", "where dealerid = " + dealerID)
                
                ttk.Label(self.frame, text = "Executing SQL").grid(row = 1, column = 1)
                
                # cursor = self.conn.cursor()
                cursor.execute(sqlQuery)
                
                records = cursor.fetchall()
                
                formatString = self.formatTable(records)
                
                ttk.Label(self.frame, text = formatString).grid(row = 1, column = 1)

        else:
            self.setup('not a number')
    
    def setupUpdate(self):
        pass
    
    def pullUpdate(self):
        pass
    
class twoInPage(page, ABC):
    
    def setup(self, msg):
        pass
    
    def pull(self, event):
        pass

class homePage(page):
    
    def callInvByDealer(self):
        invByDealerPage(self.frame)
        
    def callInvByGroup(self):
        invByGroupPage(self.frame)
        
    def callInvByMake(self):
        invByMakePage(self.frame)
    
    def callImportByDay(self):
        importByDayPage(self.frame)
    
    def callImportByImport(self):
        importByImportPage(self.frame)
        
    def callIntegrationPage(self):
        integrationPage(self.frame)
        
    def __init__(self, frame):
        '''
        Constructor
        '''
        self.frame = frame
        
        ttk.Label(frame, text = "Select the query to run").grid(row = 0, column = 1)
        ttk.Button(frame, text = "Inventory counts by dealer", command = self.callInvByDealer).grid(row = 2, column = 0)
        ttk.Button(frame, text = "Inventory counts by group", command = self.callInvByGroup).grid(row = 2, column = 1)
        ttk.Button(frame, text = "Inventory counts by make", command = self.callInvByMake).grid(row = 2, column = 2)
        ttk.Button(frame, text = "Import history date search", command = self.callImportByDay).grid(row = 3, column = 0)
        ttk.Button(frame, text = "Import history name search", command = self.callImportByImport).grid(row = 3, column = 1)
        ttk.Button(frame, text = "Integrations Stuff", command = self.callIntegrationPage).grid(row = 1, column = 0)
        
class integrationPage(page):
    
    def callImportID(self):
        importIDPage(self.frame)
    
    def __init__(self, frame):
        '''
        Constructor
        '''
        self.frame = frame
        
        self.clearScreen()
        
        ttk.Label(frame, text = 'Integrations queries and information').grid(row = 2, column = 1)
        ttk.Button(frame, text = 'Find ImportProcessorID', command = self.callImportID).grid(row = 3, column = 0)

class invByDealerPage(oneInPage):
    
    def setupUpdate(self):
        self.idLabel.configure(text = 'Enter DealerID here:')
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        self.idInput.bind("<Return>", self.pull, add = "+")
        self.sendButton.bind("<Button-1>", self.pull)
        
    def pullUpdate(self):
        super().pullUpdate()
    
    # def invByDealerSetup(self, msg):
    #     self.msg = msg
    #
    #     self.clearScreen()
    #     resetButton = ttk.Button(self.frame, text = 'Reset', command = lambda: self.invByDealerSetup(''))
    #     resetButton.grid(row = 0, column = 2)
    #
    #     self.idLabel = ttk.Label(self.frame, text = "Enter DealerID here:").grid(row = 1, column = 1)
    #     self.idInput = tk.Text(self.frame, height = 1, width = 6)    
    #     self.idInput.grid(row = 2, column = 1)
    #
    #     if msg == 'blank field':
    #         ttk.Label(self.frame, text = 'You done goofed').grid(row = 4, column = 1)
    #     elif msg == 'not a client':
    #         ttk.Label(self.frame, text = 'Not a client').grid(row = 4, column = 1)
    #     elif msg == 'not a number':
    #         ttk.Label(self.frame, text = 'Not a number').grid(row = 4, column = 1)
    #
    #     self.idInput.focus_set()
    #
    #     self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
    #     self.idInput.bind("<Return>", self.invByDealerPull, add = "+")
    #
    #     sendButton = ttk.Button(self.frame, text = "Send")
    #     sendButton.grid(row = 3, column = 1)
    #     sendButton.bind("<Button-1>", self.invByDealerPull)
        
    # def invByDealerPull(self, event):
    #     dealerID = self.idInput.get("1.0", "end-1c")
    #
    #     if dealerID == '':
    #         self.setup('blank field')
    #     elif dealerID.isnumeric():
    #         cursor = self.conn.cursor()
    #         cursor.execute("select top 1 dealerID from admin..dealer where exists (select dealerid from admin..dealer where dealerid = " + dealerID + " and clientind = 1)")
    #         sqlCheck = cursor.fetchone()
    #
    #         if type(sqlCheck) is NoneType:
    #             self.setup('not a client')
    #         else:    
    #             self.clearScreen()
    #
    #
    #
    #             sqlQueryIn = """select case when listingtypeid = 1 then 'New' else 'Used' end, 
    #             case when donotexport = 0 then 'Off Hold' else 'On Hold' end, 
    #             count(vin) 
    #             from dealersite..inventory 
    #             where dealerid = 
    #             and inventorystatusid = 1 
    #             group by listingtypeid, donotexport 
    #             order by listingtypeid, donotexport"""
    #
    #             sqlQuery = sqlQueryIn.replace("where dealerid = ", "where dealerid = " + dealerID)
    #
    #             ttk.Label(self.frame, text = "Executing SQL").grid(row = 1, column = 1)
    #
    #             # cursor = self.conn.cursor()
    #             cursor.execute(sqlQuery)
    #
    #             records = cursor.fetchall()
    #
    #             formatString = self.formatTable(records)
    #
    #             ttk.Label(self.frame, text = formatString).grid(row = 1, column = 1)
    #
    #     else:
    #         self.setup('not a number')
            
    def __init__(self, frame):
               
        self.frame = frame
        
        self.setup('')
        # self.invByDealerSetup('')
            
class invByGroupPage(page):
    
    def invByGroupSetup(self, msg):
        self.msg = msg
        
        self.clearScreen()
        resetButton = ttk.Button(self.frame, text = 'Reset', command = lambda: self.invByGroupSetup(''))
        resetButton.grid(row = 0, column = 2)
    
        ttk.Label(self.frame, text = "Enter group name here:").grid(row = 1, column = 1)
        self.idInput = tk.Text(self.frame, height = 1, width = 20)
        self.idInput.grid(row = 2, column = 1)
        self.sendButton = ttk.Button(self.frame, text = "Send")
        self.sendButton.grid(row = 3, column = 1)
        
        if msg == 'blank field':
            ttk.Label(self.frame, text = 'You done goofed').grid(row = 4, column = 1)
        elif msg == 'not a client':
            ttk.Label(self.frame, text = 'not an active group').grid(row = 4, column = 1)
            
        self.idInput.focus_set()
        
            
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.textInputCharLimit, self.idInput))
        self.idInput.bind("<Return>", self.invByGroupPull, add = "+")
        self.sendButton.bind("<Button-1>", self.invByGroupPull)
        
    def invByGroupPull(self, event):
        groupName = self.idInput.get("1.0", "end-1c")
        if groupName == '':
            ttk.Label(self.frame, text = 'You done goofed').grid(row = 4, column = 1)
            self.invByGroupSetup('blank field')
        else:
            cursor = self.conn.cursor()
            cursor.execute("select top 1 accountid from admin..Account where exists (select accountid from admin..account where name like '%" + groupName + "%' and activeind = 1)")
            sqlCheck = cursor.fetchone()
            
            if type(sqlCheck) is NoneType:
                self.invByGroupSetup('not a client')
            else:
                self.clearScreen()
                
                ttk.Label(self.frame, text = "Executing SQL").grid(row = 1, column = 1)
                
                sqlQueryIn = """select 
                d.dealerid, 
                d.dealername,
                d.city,
                case when listingtypeid = 1 then 'New' else 'Used' end,
                case when donotexport = 0 then 'Off Hold' else 'On Hold' end,
                count(vin)
                from dealersite..inventory i
                left join admin..Dealer d on d.dealerid = i.DealerID
                left join admin..Account_Dealer ad on d.DealerID = ad.DealerID
                left join admin..account a on a.AccountID = ad.AccountID
                where inventorystatusid = 1
                and d.ClientInd = 1
                and a.name like '%
                group by d.dealerid, d.dealername, d.city, listingtypeid, donotexport
                order by d.dealerid, d.dealername, d.city, listingtypeid, donotexport"""
                    
                sqlQuery = sqlQueryIn.replace("and a.name like '%", "and a.name like '%" + groupName + "%'")
                
                
                
                cursor = self.conn.cursor()
                cursor.execute(sqlQuery)
                
                records = cursor.fetchall()
                
                formatString = self.formatTable(records)
                
                ttk.Label(self.frame, text = formatString).grid(row = 1, column = 1)
                
        

    def __init__(self, frame):
            
        self.frame = frame
            
        self.invByGroupSetup('')    

class invByMakePage(page):
    
    def invByMakeSetup(self, msg):
        self.msg = msg
        
        self.clearScreen()
        resetButton = ttk.Button(self.frame, text = 'Reset', command = lambda: self.invByMakeSetup(''))
        resetButton.grid(row = 0, column = 2)
        
        ttk.Label(self.frame, text = "Enter DealerID here:").grid(row = 1, column = 1)
        self.idInput = tk.Text(self.frame, height = 1, width = 6)
        self.idInput.grid(row = 2, column = 1)
        self.sendButton = ttk.Button(self.frame, text = "Send")
        self.sendButton.grid(row = 3, column = 1)
        
        if msg == 'blank field':
            ttk.Label(self.frame, text = 'You done goofed').grid(row = 4, column = 1)
        elif msg == 'not a client':
            ttk.Label(self.frame, text = 'Not a client').grid(row = 4, column = 1)
        elif msg == 'not a number':
            ttk.Label(self.frame, text = 'Not a number').grid(row = 4, column = 1)
        
        self.idInput.focus_set()
        
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        self.idInput.bind("<Return>", self.invByMakePull, add = '+')
        self.sendButton.bind("<Button-1>", self.invByMakePull)

    def invByMakePull(self, event):
        dealerID = self.idInput.get("1.0", "end-1c")
        if dealerID == '':
            self.invByMakeSetup('blank field')
        elif dealerID.isnumeric():
            cursor = self.conn.cursor()
            cursor.execute("select top 1 dealerID from admin..dealer where exists (select dealerid from admin..dealer where dealerid = " + dealerID + " and clientind = 1)")
            sqlCheck = cursor.fetchone()
            
            if type(sqlCheck) is NoneType:
                self.invByMakeSetup('not a client')
            else:    
                self.clearScreen()
                
                sqlQueryIn = """select
                case when listingtypeid = 1 then 'New' else 'Used' end,
                make,
                case when donotexport = 0 then 'Off Hold' else 'On Hold' end,
                count(vin)
                from DealerSite..inventory
                where dealerid = 
                and InventoryStatusId = 1
                group by listingtypeid, Make, donotexport
                order by listingtypeid, make, donotexport"""
                
                
                sqlQuery = sqlQueryIn.replace("where dealerid = ", "where dealerid = " + dealerID)
                
                ttk.Label(self.frame, text = "Executing SQL").grid(row = 1, column = 1)
                
                cursor = self.conn.cursor()
                cursor.execute(sqlQuery)
                
                records = cursor.fetchall()
                
                formatString = self.formatTable(records)
                
                ttk.Label(self.frame, text = formatString).grid(row = 1, column = 1)
                
        else:
            self.invByMakeSetup('not a number')

    def __init__(self, frame):
        self.frame = frame
        
        self.invByMakeSetup('')
        
class importByDayPage(page):
    
    def importByDaySetup(self, msg):
        self.msg = msg
        self.clearScreen()
        resetButton = ttk.Button(self.frame, text = 'Reset', command = lambda: self.importByDaySetup(''))
        resetButton.grid(row = 0, column = 2)
        
        ttk.Label(self.frame, text = "Enter DealerID here:").grid(row = 1, column = 1)
        ttk.Label(self.frame, text = "Enter number of days to search:").grid(row = 2, column = 1)
        self.idInput = tk.Text(self.frame, height = 1, width = 6)
        self.idInput.grid(row = 1, column = 2)
        self.dayInput = tk.Text(self.frame, height = 1, width = 3)
        self.dayInput.grid(row = 2, column = 2)
        self.sendButton = ttk.Button(self.frame, text = "Send")
        self.sendButton.grid(row = 3, column = 2)
        
        if msg == 'blank field':
            ttk.Label(self.frame, text = 'You done goofed').grid(row = 4, column = 1)
        elif msg == 'not a client':
            ttk.Label(self.frame, text = 'Not a client').grid(row = 4, column = 1)
        elif msg == 'not a number':
            ttk.Label(self.frame, text = 'Not a dealerID').grid(row = 4, column = 1)
        elif msg == 'blank days':
            ttk.Label(self.frame, text = 'Enter a number of days').grid(row = 4, column = 1)
        elif msg == 'not a number of days':
            ttk.Label(self.frame, text = 'Not a number of days').grid(row = 4, column = 1)

        self.idInput.focus_set()
        
        self.idInput.bind("<KeyPress>",lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        self.idInput.bind("<Tab>", lambda: self.dayInput.focus_set, add = '+')
        self.dayInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.dayInputCharLimit, self.dayInput))
        self.dayInput.bind("<Return>", self.importByDayPull, add = '+')
        self.sendButton.bind("<Button-1>", self.importByDayPull)
    
    def importByDayPull(self, event):
        dealerID = self.idInput.get("1.0", "end-1c")
        if dealerID == '':
            self.importByDaySetup('blank field')
        elif dealerID.isnumeric():
            cursor = self.conn.cursor()
            cursor.execute("select top 1 dealerID from admin..dealer where exists (select dealerid from admin..dealer where dealerid = " + dealerID + " and clientind = 1)")
            sqlCheck = cursor.fetchone()
            
            if type(sqlCheck) is NoneType:
                self.importByDaySetup('not a client')
            else:
                days = self.dayInput.get("1.0", "end-1c")
                if days == '':
                    self.importByDaySetup('blank days')
                elif days.isnumeric():
                    self.clearScreen()
                    
                    sqlQueryIn = """select si.ImportName, fi.FileName, ih.FileVersionID, ih.HistoryDate
                    from integration..Import_History ih
                    left join Integration..file_version fv on ih.FileVersionID = fv.FileVersionID
                    left join Integration..File_Info fi on fv.fileid = fi.FileID
                    left join Integration..Source_Import si on si.ImportProcessorID = ih.ImportProcessorID
                    where ih.dealerid = 
                    and ih.HistoryDate > dateadd(day, -
                    order by ih.HistoryDate desc"""
                    
                    sqlQuery = sqlQueryIn.replace("where ih.dealerid = ", "where ih.dealerid = " + dealerID)
                    sqlQuery = sqlQuery.replace("and ih.HistoryDate > dateadd(day, -", "and ih.HistoryDate > dateadd(day, -" + days + ", getdate())")
                    
                    ttk.Label(self.frame, text = "Executing SQL").grid(row = 1, column = 1)
                    
                    cursor = self.conn.cursor()
                    cursor.execute(sqlQuery)
                    
                    records = cursor.fetchall()
                    
                    formatString = self.formatTable(records)
                    
                    ttk.Label(self.frame, text = formatString).grid(row = 1, column = 1)
                else:
                    self.importByDaySetup('not a number of days')
        else:
            self.importByDaySetup('not a number')


    def __init__(self, frame):
        self.frame = frame
        
        self.importByDaySetup('')
        
class importByImportPage(page):
    
    def importByImportSetup(self, msg):
        self.msg = msg
        
        self.clearScreen()
        resetButton = ttk.Button(self.frame, text = 'Reset', command = lambda: self.importByImportSetup(''))
        resetButton.grid(row = 0, column = 2)
        
        ttk.Label(self.frame, text = "Enter DealerID here:").grid(row = 1, column = 1)
        ttk.Label(self.frame, text = "Enter import name here:").grid(row = 2, column = 1)
        self.idInput = tk.Text(self.frame, height = 1, width = 6)
        self.idInput.grid(row = 1, column = 2)
        self.importName = tk.Text(self.frame, height = 1, width = 20)
        self.importName.grid(row = 2, column = 2)
        self.sendButton = ttk.Button(self.frame, text = "Send")
        self.sendButton.grid(row = 3, column = 2)
        
        if msg == 'blank field':
            ttk.Label(self.frame, text = 'You done goofed').grid(row = 4, column = 1)
        elif msg == 'not a client':
            ttk.Label(self.frame, text = 'Not a client').grid(row = 4, column = 1)
        elif msg == 'not a number':
            ttk.Label(self.frame, text = 'Not a dealerID').grid(row = 4, column = 1)
        elif msg == 'blank import':
            ttk.Label(self.frame, text = 'Enter an import name').grid(row = 4, column = 1)
        elif msg == 'not an import':
            ttk.Label(self.frame, text = 'Not an import name').grid(row = 4, column = 1)
        
        self.idInput.focus_set()
        
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        self.importName.bind("<KeyPress>", lambda event: self.charCheck(event, self.textInputCharLimit, self.importName))
        self.importName.bind("<Return>", self.importByImportPull, add = '+')
        self.sendButton.bind("<Button-1>", self.importByImportPull)
        
    def importByImportPull(self, event):
        dealerID = self.idInput.get("1.0", "end-1c")
        if dealerID == '':
            self.importByImportSetup('blank field')
        elif dealerID.isnumeric():
            cursor = self.conn.cursor()
            cursor.execute("select top 1 dealerID from admin..dealer where exists (select dealerid from admin..dealer where dealerid = " + dealerID + " and clientind = 1)")
            sqlCheck = cursor.fetchone()
            
            if type(sqlCheck) is NoneType:
                self.importByImportSetup('not a client')
            else:
                impName = self.importName.get("1.0", "end-1c")
                if impName == '':
                    self.importByImportSetup('blank import')
                else:
                    cursor = self.conn.cursor()
                    cursor.execute("select top 1 importprocessorid from integration..source_import where exists (select ImportProcessorID from integration..source_import where importname like '%" + impName + "%' and active = 1)")
                    sqlCheck = cursor.fetchone()
                    
                    if type(sqlCheck) is NoneType:
                        self.importByImportSetup('not an import')
                    else:
                        self.clearScreen()
                        
                        sqlQueryIn = """select si.ImportName, fi.FileName, ih.FileVersionID, ih.HistoryDate
                        from integration..Import_History ih
                        left join Integration..file_version fv on ih.FileVersionID = fv.FileVersionID
                        left join Integration..File_Info fi on fv.fileid = fi.FileID
                        left join Integration..Source_Import si on si.ImportProcessorID = ih.ImportProcessorID
                        where ih.dealerid = 
                        and ih.ImportProcessorID in (select ImportProcessorID from Integration..Source_Import where ImportName like '%
                        and ih.HistoryDate > dateadd(day, -30, getDate())
                        order by ih.HistoryDate desc"""
                        
                        sqlQuery = sqlQueryIn.replace("where ih.dealerid = ", "where ih.dealerid = " + dealerID)
                        sqlQuery = sqlQuery.replace("and ih.ImportProcessorID in (select ImportProcessorID from Integration..Source_Import where ImportName like '%", "and ih.ImportProcessorID in (select ImportProcessorID from Integration..Source_Import where ImportName like '%" + impName + "%')")
                        
                        ttk.Label(self.frame, text = "Executing SQL").grid(row = 1, column = 1)
                        
                        cursor = self.conn.cursor()
                        cursor.execute(sqlQuery)
                        
                        records = cursor.fetchall()
                        
                        formatString = self.formatTable(records)
                        
                        ttk.Label(self.frame, text = formatString).grid(row = 1, column = 1)
            
        else:
            self.importByImportSetup('not a number')

    def __init__(self, frame):
        self.frame = frame
        
        self.importByImportSetup('')
        
class importIDPage(page):
    
    def importIDSetup(self, msg):
        self.msg = msg
        
        self.clearScreen()
        resetButton = ttk.Button(self.frame, text = 'Reset', command = lambda: self.invByGroupSetup(''))
        resetButton.grid(row = 0, column = 2)
        
        ttk.Label(self.frame, text = "Import Name:").grid(row = 2, column = 1)
        self.importInput = tk.Text(self.frame, height = 1, width = 20)
        self.importInput.grid(row = 2, column = 2)
        self.sendButton = ttk.Button(self.frame, text = "Just Gonna Send It")
        self.sendButton.grid(row = 3, column = 2)
        
        if msg == 'blank field':
            ttk.Label(self.frame, text = 'You done goofed').grid(row = 4, column = 2)
        elif msg == 'not an import':
            ttk.Label(self.frame, text = 'No import found').grid(fow = 4, column = 2)
        
        self.importInput.focus_set()
        
        self.importInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.textInputCharLimit, self.importInput))
        self.importInput.bind("<Return>", self.importIDPull, add = '+')
        self.sendButton.bind("<Button-1>", self.importIDPull)
    
    def importIDPull(self, event):
        importName = self.importInput.get("1.0", "end-1c")
        
        if importName == '':
            self.importIDSetup('blank field')
        else:
            cursor = self.conn.cursor()
            cursor.execute("select top 1 importprocessorid from integration..source_import where exists (select ImportProcessorID from integration..source_import where importname like '%" + importName + "%' and active = 1)")
            sqlCheck = cursor.fetchone()
                 
            if type(sqlCheck) is NoneType:
                self.importByImportSetup('not an import')
                self.clearScreen()
            else:                    
                sqlQueryIn = """Select importname, importprocessorid
                From integration..source_import
                Where importname like '%
                """
                    
                sqlQuery = sqlQueryIn.replace("Where importname like '%", "Where importname like '%" + importName + "%'")
                    
                ttk.Label(self.frame, text = "Executing SQL").grid(row = 1, column = 1)
                  
                cursor = self.conn.cursor()
                cursor.execute(sqlQuery)
                    
                records = cursor.fetchall()
                    
                formatString = self.formatTable(records)
                   
                ttk.Label(self.frame, text = formatString).grid(row = 1, column = 1)
        
    def __init__(self, frame):
        self.frame = frame
        
        self.importIDSetup('')
        
        