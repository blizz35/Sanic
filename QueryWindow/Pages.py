'''
Created on May 21, 2026

@author: admin
'''

from abc import ABC
from tkinter import ttk
import tkinter as tk
from mssql_python import connect 
from _types import NoneType
# from PyInstaller.compat import pywintypes

class page(ABC):
    '''
    classdocs
    '''    
    
    conn = connect("Server=192.168.2.19;Encrypt=yes;TrustServerCertificate=yes;Authentication=SqlPassword;UID=integration;PWD=integration")
    idInputCharLimit = 6
    textInputCharLimit = 20
    dayInputCharLimit = 3
    sqlInputCharLimit = 200
    
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
        if textLen >= maxChars and event.keysym not in {'BackSpace', 'Delete', 'Return', 'Tab'}: 
            return 'break'
    
    def __init__(self, frame):
        '''
        Constructor
        '''        
        self.frame = frame
        
class oneInPage(page, ABC):
    
    def setup(self, msg):
        self.msg = msg
        
        self.clearScreen()
        resetButton = ttk.Button(self.frame, text = 'Reset', command = lambda: self.setup(''))
        resetButton.grid(row = 0, column = 2)
        
        self.idLabel = ttk.Label(self.frame)
        self.idLabel.grid(row = 1, column = 1)
        self.idInput = tk.Text(self.frame, height = 1, width = self.idInputCharLimit)    
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
    
    def pullChecks(self, event, sqlIn, inputType):
        dealerID = self.idInput.get("1.0", "end-1c")
        inType = inputType
        self.sqlIn = sqlIn
        
        #is there data in the field
        if dealerID == '':
            self.setup('blank field')
        #is the query expecting a group name?
        elif inType == 'group':
            cursor = self.conn.cursor()
            cursor.execute("select top 1 accountid from admin..Account where exists (select accountid from admin..account where name like '%" + dealerID + "%' and activeind = 1)")
            sqlCheck = cursor.fetchone()
    
            if type(sqlCheck) is NoneType:
                self.setup('not a client')
            else:
                self.pull(event, dealerID, sqlIn, inputType)
        #is the query expecting a dealer ID?
        elif inType == 'dealer':
            #is the data entered a number?
            if dealerID.isnumeric():
                cursor = self.conn.cursor()
                cursor.execute("select top 1 dealerID from admin..dealer where exists (select dealerid from admin..dealer where dealerid = " + dealerID + " and clientind = 1)")
                sqlCheck = cursor.fetchone()

                #is the data entered an active client?
                if type(sqlCheck) is NoneType:
                    self.setup('not a client')
                else:
                    self.pull(event, dealerID, sqlIn, inputType)                    
            #if not a number
            elif dealerID.isnumeric() == 'false':
                self.setup('not a number')
        #is the query expecting an import name?
        elif inType == 'import':
            cursor = self.conn.cursor()
            cursor.execute("select top 1 importname from integration..source_import where exists (select ImportProcessorID from integration..source_import where importname like '%" + dealerID + "%' and active = 1)")
            sqlCheck = cursor.fetchone()
                
            #is the data entered an active import?
            if type(sqlCheck) is NoneType:
                self.setup('not an import')
            else:
                self.pull(event, dealerID, sqlIn, inType)            
        
    def pull(self, event, dealerID, sqlIn, inputType):
        self.dealerID = dealerID
        self.inType = inputType
        self.clearScreen()
                    
        sqlQueryIn = sqlIn
                   
        if self.inType == 'dealer':
            self.sqlQueryIn = sqlQueryIn.replace("where dealerid = ", "where dealerid = " + self.dealerID)
        elif self.inType == 'group':
            self.sqlQueryIn = sqlQueryIn.replace("and a.name like '%", "and a.name like '%" + self.dealerID + "%'")
        elif self.inType == 'import':
            self.sqlQueryIn = sqlQueryIn.replace("where importname like '%", "where importname like '%" + self.dealerID + "%'")
                
        ttk.Label(self.frame, text = "Executing SQL").grid(row = 1, column = 1)
        
        cursor = self.conn.cursor()
        cursor.execute(self.sqlQueryIn)
                    
        records = cursor.fetchall()
                    
        formatString = self.formatTable(records)
                    
        ttk.Label(self.frame, text = formatString).grid(row = 1, column = 1)
    
    def setupUpdate(self):
        pass
    
    def pullUpdate(self):
        pass
    
class twoInPage(page, ABC):
    
    def textFocus(self):
        self.textInput.focus_set()
        return 'break'
    
    def copyText(self):
        self.frame.clipboard_clear()
        self.frame.clipboard_append(self.formatString)
    
    def setup(self, msg):
        self.msg = msg
        self.clearScreen()
        resetButton = ttk.Button(self.frame, text = 'Reset', command = lambda: self.setup(''))
        resetButton.grid(row = 0, column = 2)
        
        self.idLabel = ttk.Label(self.frame)
        self.idLabel.grid(row = 1, column = 1)
        self.textLabel = ttk.Label(self.frame)
        self.textLabel.grid(row = 2, column = 1)
        self.idInput = tk.Text(self.frame, height = 1, width = self.idInputCharLimit)
        self.idInput.grid(row = 1, column = 2)
        self.textInput = tk.Text(self.frame, height = 1)
        self.textInput.grid(row = 2, column = 2)
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
        elif msg == 'not an import':
            ttk.Label(self.frame, text = 'Not an import').grid(row = 4, column = 1)

        self.idInput.focus_set()
        
        self.setupUpdate()

    
    def pullCheckID(self, event, sqlIn, inputType):
        dealerID = self.idInput.get("1.0", "end-1c")
        inType = inputType
        sqlIn = sqlIn
        inCheck = inType[:inType.find(',')]
        
        #is there data in the field
        if dealerID == '':
            self.setup('blank field')
        #is the query expecting a group name?
        elif inCheck == 'group':
            cursor = self.conn.cursor()
            cursor.execute("select top 1 accountid from admin..Account where exists (select accountid from admin..account where name like '%" + dealerID + "%' and activeind = 1)")
            sqlCheck = cursor.fetchone()
    
            if type(sqlCheck) is NoneType:
                self.setup('not a client')
            else:
                self.pullCheckText(event, dealerID, sqlIn, inputType)
        #is the query expecting a dealer ID?
        elif inCheck == 'dealer':
            #is the data entered a number?
            if dealerID.isnumeric():
                cursor = self.conn.cursor()
                cursor.execute("select top 1 dealerID from admin..dealer where exists (select dealerid from admin..dealer where dealerid = " + dealerID + " and clientind = 1)")
                sqlCheck = cursor.fetchone()
                
                #is the data entered an active client?
                if type(sqlCheck) is NoneType:
                    self.setup('not a client')
                else:
                    self.pullCheckText(event, dealerID, sqlIn, inputType)                    
            #if not a number
            elif not dealerID.isnumeric():
                self.setup('not a number')        
        elif inCheck == 'doNotExport':
            self.pullCheckText(event, dealerID, sqlIn, inputType)
    
    def pullCheckText(self, event, dealerId, sqlIn, inputType):
        textIn = self.textInput.get("1.0", "end-1c")
        inType = inputType
        sqlIn = sqlIn
        dealerId = dealerId
        inCheck = inType[inType.find(',')+1:]

        #is there data in the field
        if textIn == '':
            self.setup('blank field')
        #is the query expecting a number of days?
        elif inCheck == 'day':
            #is there a number in the field?
            if textIn.isnumeric():
                self.pull(event, dealerId, textIn, sqlIn, inType)
            else:
                self.setup('not a number of days')
        #is the query expecting the name of an import?
        elif inCheck == 'import':
            cursor = self.conn.cursor()
            cursor.execute("select top 1 importname from integration..source_import where exists (select ImportProcessorID from integration..source_import where importname like '%" + textIn + "%' and active = 1)")
            sqlCheck = cursor.fetchone()
                
            #is the data entered an active import?
            if type(sqlCheck) is NoneType:
                self.setup('not an import')
            else:
                self.pull(event, dealerId, textIn, sqlIn, inType)                
        elif inCheck == 'importExact':
            cursor = self.conn.cursor()
            cursor.execute("select top 1 importname from integration..source_import where exists (select ImportProcessorID from integration..source_import where importname like '" + textIn + "' and active = 1)")
            sqlCheck = cursor.fetchone()
                
            #is the data entered an active import?
            if type(sqlCheck) is NoneType:
                self.setup('not an import')
            else:
                self.pull(event, dealerId, textIn, sqlIn, inType)
            
        
    def pull(self, event, dealerId, textIn, sqlIn, inputType):
        dealerID = dealerId
        textIn = textIn
        inputType = inputType
        self.clearScreen()
                        
        sqlQueryIn = sqlIn
                        
        if inputType[:inputType.find(',')] == 'dealer':
            sqlQueryIn = sqlQueryIn.replace("where ih.dealerid = ", "where ih.dealerid = " + dealerID)
        elif inputType[:inputType.find(',')] == 'group':
            sqlQueryIn = sqlQueryIn.replace("and a.name like '%", "and a.name like '%" + self.dealerID + "%'")
        
        if inputType[inputType.find(',')+1:] == 'day':
            sqlQueryIn = sqlQueryIn.replace("and ih.HistoryDate > dateadd(day, -", "and ih.HistoryDate > dateadd(day, -" + textIn + ", getDate())")    
        elif inputType[inputType.find(',')+1:] == 'import':
            sqlQueryIn = sqlQueryIn.replace("and ih.ImportProcessorID in (select ImportProcessorID from Integration..Source_Import where ImportName like '%", "and ih.ImportProcessorID in (select ImportProcessorID from Integration..Source_Import where ImportName like '%" + textIn + "%')")
        elif inputType[inputType.find(',')+1:] == 'importExact':
            sqlQueryIn = sqlQueryIn.replace("where importname like '", "where importname like '" + textIn + "'")
        
        ttk.Label(self.frame, text = "Executing SQL").grid(row = 1, column = 1)
        
        cursor = self.conn.cursor()
        cursor.execute(sqlQueryIn)
                    
        records = cursor.fetchall()
                        
        formatString = self.formatTable(records)
        
        if inputType[:inputType.find(',')] == 'doNotExport':
            formatString = formatString.replace(',', '')
            self.sql2In = self.sql2In.replace("case when", "case when " + dealerId)
            self.formatString = self.sql2In.replace("s.importprocessorid = ", "s.importprocessorid = " + formatString)
                        
        self.outputLabel = ttk.Label(self.frame, text = self.formatString)
        self.outputLabel.grid(row = 1, column = 1)
        
        self.pullUpdate()

    def setupUpdate(self):
        pass
    
    def pullUpdate(self):
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
        
    def callDoNotExport(self):
        doNotExportPage(self.frame)
    
    def __init__(self, frame):
        '''
        Constructor
        '''
        self.frame = frame
        
        self.clearScreen()
        
        ttk.Label(frame, text = 'Integrations queries and information').grid(row = 2, column = 1)
        ttk.Button(frame, text = 'Find ImportProcessorID', command = self.callImportID).grid(row = 3, column = 0)
        ttk.Button(frame, text = 'DoNotExport transform for DMS', command = self.callDoNotExport).grid(row = 3, column = 1)

class invByDealerPage(oneInPage):
    
    def setupUpdate(self):
        sqlIn = """select case when listingtypeid = 1 then 'New' else 'Used' end, 
                case when donotexport = 0 then 'Off Hold' else 'On Hold' end, 
                count(vin) 
                from dealersite..inventory 
                where dealerid = 
                and inventorystatusid = 1 
                group by listingtypeid, donotexport 
                order by listingtypeid, donotexport"""
        
        self.idLabel.configure(text = 'Enter DealerID here:')
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        self.idInput.bind("<Return>", lambda event: self.pullChecks(event, sqlIn, 'dealer'), add = "+")
        self.sendButton.bind("<Button-1>", lambda event: self.pullChecks(event, sqlIn, 'dealer'))
        
    def pullUpdate(self):
        super().pullUpdate()
            
    def __init__(self, frame):
               
        self.frame = frame
        
        self.setup('')
            
class invByGroupPage(oneInPage):
    
    def setupUpdate(self):
        
        sqlIn = """select 
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
        
        self.idLabel.configure(text = 'Enter group name here:')
        self.idInput.configure(width = self.textInputCharLimit)
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.textInputCharLimit, self.idInput))
        self.idInput.bind("<Return>", lambda event: self.pullChecks(event, sqlIn, 'group'), add = "+")
        self.sendButton.bind("<Button-1>", lambda event: self.pullChecks(event, sqlIn, 'group'))   
        
    def pullUpdate(self):
        super().pullUpdate()         

    def __init__(self, frame):
        self.frame = frame
            
        self.setup('')

class invByMakePage(oneInPage):
    
    def setupUpdate(self):
        
        sqlIn = """select
                case when listingtypeid = 1 then 'New' else 'Used' end,
                make,
                case when donotexport = 0 then 'Off Hold' else 'On Hold' end,
                count(vin)
                from DealerSite..inventory
                where dealerid = 
                and InventoryStatusId = 1
                group by listingtypeid, Make, donotexport
                order by listingtypeid, make, donotexport"""
        
        self.idLabel.configure(text = 'Enter DealerID here:')
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        self.idInput.bind("<Return>", lambda event: self.pullChecks(event, sqlIn, 'dealer'), add = "+")
        self.sendButton.bind("<Button-1>", lambda event: self.pullChecks(event, sqlIn, 'dealer'))

    def __init__(self, frame):
        self.frame = frame
        
        self.setup('')
        
class importByDayPage(twoInPage):
    
    def setupUpdate(self):
        self.sqlIn = """select si.ImportName, fi.FileName, ih.FileVersionID, ih.HistoryDate
                    from integration..Import_History ih
                    left join Integration..file_version fv on ih.FileVersionID = fv.FileVersionID
                    left join Integration..File_Info fi on fv.fileid = fi.FileID
                    left join Integration..Source_Import si on si.ImportProcessorID = ih.ImportProcessorID
                    where ih.dealerid = 
                    and ih.HistoryDate > dateadd(day, -
                    order by ih.HistoryDate desc"""
        
        self.idLabel.configure(text = 'Enter dealer ID here:')
        self.textLabel.configure(text = 'Enter number of days to search:')
        self.textInput.configure(width = self.dayInputCharLimit)
        
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        self.idInput.bind("<Tab>", lambda event: self.textFocus(), add = '+')
        self.textInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.textInputCharLimit, self.textInput))
        self.textInput.bind("<Return>", lambda event: self.pullCheckID(event, self.sqlIn, 'dealer,import'), add = '+')
        self.sendButton.bind("<Button-1>", lambda event: self.pullCheckID(event, self.sqlIn, 'dealer,import'))
        
    def __init__(self, frame):
        self.frame = frame
        
        self.setup('')
        
class importByImportPage(twoInPage):
    
    def setupUpdate(self):
        self.sqlIn = """select si.ImportName, fi.FileName, ih.FileVersionID, ih.HistoryDate
                        from integration..Import_History ih
                        left join Integration..file_version fv on ih.FileVersionID = fv.FileVersionID
                        left join Integration..File_Info fi on fv.fileid = fi.FileID
                        left join Integration..Source_Import si on si.ImportProcessorID = ih.ImportProcessorID
                        where ih.dealerid = 
                        and ih.ImportProcessorID in (select ImportProcessorID from Integration..Source_Import where ImportName like '%
                        and ih.HistoryDate > dateadd(day, -30, getDate())
                        order by ih.HistoryDate desc"""
        
        self.idLabel.configure(text = 'Enter dealer ID here:')
        self.textLabel.configure(text = 'Enter import name here:')
        self.textInput.configure(width = self.textInputCharLimit)
        
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        self.idInput.bind("<Tab>", lambda event: self.textFocus(), add = '+')
        self.textInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.textInputCharLimit, self.textInput))
        self.textInput.bind("<Return>", lambda event: self.pullCheckID(event, self.sqlIn, 'dealer,import'), add = '+')
        self.sendButton.bind("<Button-1>", lambda event: self.pullCheckID(event, self.sqlIn, 'dealer,import'))

    def __init__(self, frame):
        self.frame = frame
        
        self.setup('')
        
class importIDPage(oneInPage):
    
    def setupUpdate(self):
        
        sqlIn = """select importname, ImportProcessorID 
            from integration..source_import 
            where importname like '%
            and active = 1"""
        
        self.idLabel.configure(text = 'Enter import name here:')
        self.idInput.configure(width = self.textInputCharLimit)
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.textInputCharLimit, self.idInput))
        self.idInput.bind("<Return>", lambda event: self.pullChecks(event, sqlIn, 'import'), add = "+")
        self.sendButton.bind("<Button-1>", lambda event: self.pullChecks(event, sqlIn, 'import'))          
        
    def __init__(self, frame):
        self.frame = frame
        
        self.setup('')
                
class doNotExportPage(twoInPage):
    
    sql2In = """case when
else isnull(i.donotexport, abs(s.autooffhold - 1)) end 
from #data left join dealersite..inventory i on i.dealerid = #data.dealerid and i.VIN = #data.VIN and i.inventorystatusid = 1 
left join integration..source_import_dealer s on s.dealerid = #data.dealerid and s.importprocessorid = """
    
    def setupUpdate(self):
        
        sqlIn = """select ImportProcessorID 
            from integration..source_import 
            where importname like '
            and active = 1"""
            
        
        
        self.idLabel.configure(text = 'Enter case when and then statement here:')
        self.textLabel.configure(text = 'Enter import name here:')
        self.idInput.configure(width = int(self.sqlInputCharLimit/4))
        self.idInput.configure(height = 4)
        self.textInput.configure(width = self.textInputCharLimit)
        self.textInput.bind("<Return>", lambda event: self.pullCheckID(event, sqlIn, 'doNotExport,importExact'))
        self.idInput.bind("<Tab>", lambda event: self.textFocus())#, add = '+')
        self.sendButton.bind("<Button-1>", lambda event: self.pullCheckID(event, sqlIn, 'doNotExport,importExact'))
        
    def pullUpdate(self):
        ttk.Button(self.frame, text = 'Copy', command = self.copyText()).grid(row = 2, column = 1)
    
    def __init__(self, frame):
        self.frame = frame
        
        self.setup('')