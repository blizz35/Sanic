'''
Created on May 21, 2026

@author: admin
'''

from abc import ABC
from tkinter import ttk
import tkinter as tk
from mssql_python import connect 
from _types import NoneType

class page(ABC):
    '''
    abstract class that contains the basic setup for a page
    this stores the parameters as well as basic functions
    '''    
    
    conn = connect("Server=192.168.2.19;Encrypt=yes;TrustServerCertificate=yes;Authentication=SqlPassword;UID=integration;PWD=integration")
    idInputCharLimit = 6
    textInputCharLimit = 20
    dayInputCharLimit = 3
    sqlInputCharLimit = 200
    vinInputCharLimit = 17
    
    def clearScreen(self):
        '''
        clears the screen when a new page is created so elements don't cover other elements
        also adds home button in after as part of setup
        '''
        
        for item in self.frame.winfo_children():
            item.destroy()
            
        ttk.Button(self.frame, text = 'Home', command = self.backHome).grid(row = 0, column = 1)        
        
    def backHome(self):
        '''
        defines what the home button does:
        clears the screen and creates a new homePage object
        '''
        
        for item in self.frame.winfo_children():
            item.destroy()
            
        homePage(self.frame)
        
    def formatTable(self, tableString):
        '''
        trims the rows returned by queries into a format that is more human readable
        '''
        
        recordString = str(tableString).replace('[', '').replace(']', '')
        recordString = recordString.replace('), (', '\n')
        recordString = recordString.replace('(', '').replace(')', '')
        recordString = recordString.replace("'", '').replace("'", '')

        return recordString
    
    def formatTableRow(self, tableString):
        '''
        when a query returns one row with multiple columns
        this pivots the output into one column and multiple rows
        '''
        
        recordString = str(tableString).replace('[', '').replace(']', '')
        recordString = recordString.replace('), (', '\n')
        recordString = recordString.replace('(', '').replace(')', '')
        recordString = recordString.replace("'", '').replace("'", '')
        recordString = recordString.replace(',', '\n')
        
        return recordString

    def charCheck(self, event, charnum, fieldIn):
        '''
        called every character entered into fieldIn
        checks to see if the length matches charnum - this is the character limit for the field
        if limit is reached and Backspace, Delete, Enter, or Tab are not pressed, it cancels input
        '''
        
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
    '''
    abstract class to set up for pages with one input box
    handles input validation and pulling data for these queries
    '''
    
    def copyText(self):
        '''
        copies text to the clipboard and adds feedback to the user
        '''
        
        self.frame.clipboard_clear()
        self.frame.clipboard_append(self.formatString)
        ttk.Label(self.frame, text = 'Copied').grid(row = 3, column = 1)
    
    def setup(self, msg):
        '''
        this creates the initial page that requests input
        can be called with preset text in msg to provide feedback to user
        
        [blank field, not a client, not a number, vin length]
        
        these are for input validation and error handling
        '''
        
        self.msg = msg
        
        #basic setups
        self.clearScreen()
        resetButton = ttk.Button(self.frame, text = 'Reset', command = lambda: self.setup(''))
        resetButton.grid(row = 0, column = 2)
        
        self.idLabel = ttk.Label(self.frame)
        self.idLabel.grid(row = 1, column = 1)
        self.idInput = tk.Text(self.frame, height = 1, width = self.idInputCharLimit)    
        self.idInput.grid(row = 2, column = 1)
        
        #input validation and error handling messages
        if msg == 'blank field':
            ttk.Label(self.frame, text = 'You done goofed').grid(row = 4, column = 1)
        elif msg == 'not a client':
            ttk.Label(self.frame, text = 'Not a client').grid(row = 4, column = 1)
        elif msg == 'not a number':
            ttk.Label(self.frame, text = 'Not a number').grid(row = 4, column = 1)
        elif msg == 'vin length':
            ttk.Label(self.frame, text = 'VIN is the wrong length').grid(row = 4, column = 1)
        
        #adding submit button and setting focus
        self.idInput.focus_set()
        self.sendButton = ttk.Button(self.frame, text = "Just gonna send it")
        self.sendButton.grid(row = 3, column = 1)
        
        #setup anything specific for the class extending oneInPage
        self.setupUpdate()
    
    def pullChecks(self, event, sqlIn, inputType):
        '''
        performs input validation
        calls setup() again if input checks fail
        passing a message through to the user
        
        the class extending oneInPage passes in an expected data type (inputType)
        this is used to determine if the data entered matches what is expected
        also checks to see if the input is valid to prevent SQL errors running the query
        '''
        
        dealerID = self.idInput.get("1.0", "end-1c")
        inType = inputType
        self.sqlIn = sqlIn
        
        #is there data in the field
        if dealerID == '':
            self.setup('blank field')
        #is the query expecting a group name?
        elif inType == 'group':
            #checks in the database to see if that group name exists and if they are marked as a client
            cursor = self.conn.cursor()
            cursor.execute("select top 1 accountid from admin..Account where exists (select accountid from admin..account where name like '%" + dealerID + "%' and activeind = 1)")
            sqlCheck = cursor.fetchone()
    
            #if no rows return - not an active group
            #todo: update to differentiate between group name not existing in database and group exists but isn't active
            if type(sqlCheck) is NoneType:
                self.setup('not a client')
            else:
                self.pull(event, dealerID, sqlIn, inputType)
        #is the query expecting a dealer ID?
        elif inType == 'dealer':
            #is the data entered a number?
            if dealerID.isnumeric():
                #checks in the database to see if that dealerID matches a dealer marked as our client
                cursor = self.conn.cursor()
                cursor.execute("select top 1 dealerID from admin..dealer where exists (select dealerid from admin..dealer where dealerid = " + dealerID + " and clientind = 1)")
                sqlCheck = cursor.fetchone()

                #if no rows return - dealer is not marked as our client
                #todo: update to tell when a dealerID exists but isn't our client or if it doesn't exist (edge case but dealerIDs have been deleted)
                if type(sqlCheck) is NoneType:
                    self.setup('not a client')
                else:
                    self.pull(event, dealerID, sqlIn, inputType)                    
            #if not a number
            elif dealerID.isnumeric() == 'false':
                self.setup('not a number')
        #is the query expecting an import name?
        elif inType == 'import':
            #checks in the database to see if that import name matches an active import
            cursor = self.conn.cursor()
            cursor.execute("select top 1 importname from integration..source_import where exists (select ImportProcessorID from integration..source_import where importname like '%" + dealerID + "%' and active = 1)")
            sqlCheck = cursor.fetchone()
                
            #if no rows return - import is not active
            if type(sqlCheck) is NoneType:
                self.setup('not an import')
            else:
                self.pull(event, dealerID, sqlIn, inType)       
        #is the query expecting a VIN?
        elif inType == 'vin':
            #is the VIN the right length?
            if len(dealerID) != 17:
                self.setup('vin length')
            else:
                self.pull(event, dealerID, sqlIn, inType)
        
    def pull(self, event, dealerID, sqlIn, inputType):
        '''
        pulls data from the database
        called by validation checks when passed
        formats data and displays results
        adds back button that calls setup() again with a blank msg to reset for other input
        '''
        
        self.dealerID = dealerID
        self.inType = inputType
        self.clearScreen()
        
        #back button
        backButton = ttk.Button(self.frame, text = 'Back', command = lambda: self.setup(''))
        backButton.grid(row = 0, column = 2)
                    
        sqlQueryIn = sqlIn
        
        #checking to see what the input field contains to add the input to the query           
        if self.inType == 'dealer':
            self.sqlQueryIn = sqlQueryIn.replace("where dealerid = ", "where dealerid = " + self.dealerID)
        elif self.inType == 'group':
            self.sqlQueryIn = sqlQueryIn.replace("and a.name like '%", "and a.name like '%" + self.dealerID + "%'")
        elif self.inType == 'import':
            self.sqlQueryIn = sqlQueryIn.replace("where importname like '%", "where importname like '%" + self.dealerID + "%'")
        elif self.inType == 'vin':
            self.sqlQueryIn = sqlQueryIn.replace("where vin = '", "where vin = '" + self.dealerID + "'")
                
        #todo: update with timeout to prevent query from running forever
        #todo: make this clearer with what is happening behind the scenes
        ttk.Label(self.frame, text = "Executing SQL").grid(row = 1, column = 1)
        
        #pulling the data
        cursor = self.conn.cursor()
        cursor.execute(self.sqlQueryIn)
                    
        records = cursor.fetchall()
        
        #formatting the output and displaying it on the page
        if self.inType == 'vin':
            formatString = self.formatTableRow(records)            
        else:
            formatString = self.formatTable(records)
                    
        ttk.Label(self.frame, text = formatString).grid(row = 1, column = 1)
    
    def setupUpdate(self):
        '''
        abstract method for any query specific changes
        '''
        
        pass
    
    def pullUpdate(self):
        '''
        abstract method for any query specific changes
        '''
        
        pass
    
class twoInPage(page, ABC):
    '''
    abstract class to set up for pages with two input boxes
    handles input validation and pulling data for these queries
    '''
    
    def textFocus(self):
        '''
        allows <tab> to move from the first input box (idInput) to the second (textInput)
        '''
        
        self.textInput.focus_set()
        return 'break'
    
    def copyText(self):
        '''
        copies text to the clipboard and adds feedback to the user
        '''
        
        self.frame.clipboard_clear()
        self.frame.clipboard_append(self.formatString)
        ttk.Label(self.frame, text = 'Copied').grid(row = 3, column = 1)
    
    def setup(self, msg):
        '''
        this creates the initial page that requests input
        can be called with preset text in msg to provide feedback to user
        
        [blank field, not a client, not a number, blank days, not a number of days, not an import]
        
        these are for input validation and error handling
        '''
        
        #basic setup
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
        self.sendButton = ttk.Button(self.frame, text = "Just gonna send it")
        self.sendButton.grid(row = 3, column = 2)
        
        #input validation feedback
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
        '''
        first of two functions to validate input
        this only checks what goes in the first input box (idInput)
        
        the class extending twoInPage passes in what the expected data type is (inputType)
        this is used to determine if the data entered matches what is expected
        also checks to see if the input is valid to prevent SQL errors running the query
        '''
        
        dealerID = self.idInput.get("1.0", "end-1c")
        inType = inputType
        sqlIn = sqlIn
        inCheck = inType[:inType.find(',')]
        
        #is there data in the field
        if dealerID == '':
            self.setup('blank field')
        #is the query expecting a group name?
        elif inCheck == 'group':
            #checks the database to see if the entered group exists and is marked as our client
            cursor = self.conn.cursor()
            cursor.execute("select top 1 accountid from admin..Account where exists (select accountid from admin..account where name like '%" + dealerID + "%' and activeind = 1)")
            sqlCheck = cursor.fetchone()
    
            #is the group our client?
            #todo: differentiate between exists and our client vs doesn't exist
            if type(sqlCheck) is NoneType:
                self.setup('not a client')
            else:
                self.pullCheckText(event, dealerID, sqlIn, inputType)
        #is the query expecting a dealer ID?
        elif inCheck == 'dealer':
            #is the data entered a number?
            if dealerID.isnumeric():
                #checks the database to see if the dealerID exists and if they're marked as our client 
                cursor = self.conn.cursor()
                cursor.execute("select top 1 dealerID from admin..dealer where exists (select dealerid from admin..dealer where dealerid = " + dealerID + " and clientind = 1)")
                sqlCheck = cursor.fetchone()
                
                #if no rows return - dealer is not marked as our client
                #todo: update to tell when a dealerID exists but isn't our client or if it doesn't exist (edge case but dealerIDs have been deleted)
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
        '''
        second input validation
        see pullCheckID for more details on functions
        '''
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
            #checks the database to see if the import name exists and if it is active
            cursor = self.conn.cursor()
            cursor.execute("select top 1 importname from integration..source_import where exists (select ImportProcessorID from integration..source_import where importname like '%" + textIn + "%' and active = 1)")
            sqlCheck = cursor.fetchone()
                
            #is the data entered an active import?
            #todo: differentiate between inactive import and import doesn't exist
            if type(sqlCheck) is NoneType:
                self.setup('not an import')
            else:
                self.pull(event, dealerId, textIn, sqlIn, inType)                
        #if the exact import name is required
        #this is used when feeding the input value directly into another query to prevent SQL errors
        elif inCheck == 'importExact':
            #checks to see if this exact name exists and is active
            cursor = self.conn.cursor()
            cursor.execute("select top 1 importname from integration..source_import where exists (select ImportProcessorID from integration..source_import where importname like '" + textIn + "' and active = 1)")
            sqlCheck = cursor.fetchone()
                
            #is the data entered an active import?
            #todo: differentiate between inactive import and import doesn't exist
            if type(sqlCheck) is NoneType:
                self.setup('not an import')
            else:
                self.pull(event, dealerId, textIn, sqlIn, inType)
        #is the query expecting a stock number?
        #there is no check here because stock numbers can vary greatly
        elif inCheck == 'stock':
            self.pull(event, dealerId, textIn, sqlIn, inType)
        
    def pull(self, event, dealerId, textIn, sqlIn, inputType):
        '''
        pulls data from the database
        called by validation checks when checks are passed
        formats data and displays results
        adds back button that calls setup() again with a blank msg to reset for other input
        '''
        
        dealerID = dealerId
        textIn = textIn
        inputType = inputType
        self.clearScreen()
        
        #back button
        backButton = ttk.Button(self.frame, text = 'Back', command = lambda: self.setup(''))
        backButton.grid(row = 0, column = 2)
                        
        sqlQueryIn = sqlIn
                        
        #checking to see what the input fields contain to add the input to the query 
        if inputType[:inputType.find(',')] == 'dealer':
            sqlQueryIn = sqlQueryIn.replace("dealerid = ", "dealerid = " + dealerID)
        elif inputType[:inputType.find(',')] == 'group':
            sqlQueryIn = sqlQueryIn.replace("and a.name like '%", "and a.name like '%" + self.dealerID + "%'")
        
        if inputType[inputType.find(',')+1:] == 'day':
            sqlQueryIn = sqlQueryIn.replace("and ih.HistoryDate > dateadd(day, -", "and ih.HistoryDate > dateadd(day, -" + textIn + ", getDate())")    
        elif inputType[inputType.find(',')+1:] == 'import':
            sqlQueryIn = sqlQueryIn.replace("and ih.ImportProcessorID in (select ImportProcessorID from Integration..Source_Import where ImportName like '%", "and ih.ImportProcessorID in (select ImportProcessorID from Integration..Source_Import where ImportName like '%" + textIn + "%')")
        elif inputType[inputType.find(',')+1:] == 'importExact':
            sqlQueryIn = sqlQueryIn.replace("where importname like '", "where importname like '" + textIn + "'")
        elif inputType[inputType.find(',')+1:] == 'stock':
            sqlQueryIn = sqlQueryIn.replace("and stockNo = '", "and stockNo = '" + textIn + "'")
        
        #todo: update with timeout to prevent query from running forever
        #todo: make this clearer with what is happening behind the scenes
        ttk.Label(self.frame, text = "Executing SQL").grid(row = 1, column = 1)
        
        #pulling the data
        cursor = self.conn.cursor()
        cursor.execute(sqlQueryIn)
        
        records = cursor.fetchall()
        
        #formatting the output
        self.formatString = self.formatTable(records)
        
        if inputType[:inputType.find(',')] == 'doNotExport':
            formatString = self.formatString.replace(',', '')
            self.sql2In = self.sql2In.replace("case when", "case when " + dealerId)
            self.formatString = self.sql2In.replace("s.importprocessorid = ", "s.importprocessorid = " + formatString)
        
        if inputType[inputType.find(',')+1:] == 'stock':
            formatString = self.formatTableRow(records)            
        else:
            formatString = self.formatTable(records)
        
        
        #displaying the output
        self.outputLabel = ttk.Label(self.frame, text = self.formatString)
        self.outputLabel.grid(row = 1, column = 1)
        
        self.pullUpdate()

    def setupUpdate(self):
        '''
        abstract method for any query specific changes
        '''
        
        pass
    
    def pullUpdate(self):
        '''
        abstract method for any query specific changes
        '''
        
        pass

class homePage(page):
    '''
    initial starting page
    functions call constructors for other page classes
    '''
    
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
    
    def callPriceLookupPage(self):
        pricingLookupPage(self.frame)
        
    def callPriceLookupStockPage(self):
        pricingLookupByStockPage(self.frame)
        
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
        ttk.Button(frame, text = "Pricing lookup by VIN", command = self.callPriceLookupPage).grid(row = 4, column = 0)
        ttk.Button(frame, text = "Pricing lookup by Stock Number", command = self.callPriceLookupStockPage).grid(row = 4, column = 1)
        
class integrationPage(page):
    '''
    folder to store pages for integration team use
    '''
    
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
        ttk.Button(frame, text = 'Find ImportProcessorID', command = self.callImportID).grid(row = 3, column = 1)
        ttk.Button(frame, text = 'DoNotExport transform for DMS', command = self.callDoNotExport).grid(row = 3, column = 2)

class invByDealerPage(oneInPage):
    '''
    reads in a dealerID
    returns inventory counts grouped by new/used and on hold/off hold
    '''
    
    def setupUpdate(self):
        #sql query
        sqlIn = """select case when listingtypeid = 1 then 'New' else 'Used' end, 
                case when donotexport = 0 then 'Off Hold' else 'On Hold' end, 
                count(vin) 
                from dealersite..inventory 
                where dealerid = 
                and inventorystatusid = 1 
                group by listingtypeid, donotexport 
                order by listingtypeid, donotexport"""
        
        #updates
        self.idLabel.configure(text = 'Enter DealerID here:')
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        self.idInput.bind("<Return>", lambda event: self.pullChecks(event, sqlIn, 'dealer'), add = "+")
        self.sendButton.bind("<Button-1>", lambda event: self.pullChecks(event, sqlIn, 'dealer'))
        
    def pullUpdate(self):
        super().pullUpdate()
            
    def __init__(self, frame):
        '''
        constructor
        '''
               
        self.frame = frame
        
        self.setup('')
            
class invByGroupPage(oneInPage):
    '''
    reads in a group name (allows partial names)
    returns inventory for that group grouped by dealership, new/used, and on hold/off hold
    '''
    
    def setupUpdate(self):
        
        #sql query
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
        
        #updates
        self.idLabel.configure(text = 'Enter group name here:')
        self.idInput.configure(width = self.textInputCharLimit)
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.textInputCharLimit, self.idInput))
        self.idInput.bind("<Return>", lambda event: self.pullChecks(event, sqlIn, 'group'), add = "+")
        self.sendButton.bind("<Button-1>", lambda event: self.pullChecks(event, sqlIn, 'group'))   
        
    def pullUpdate(self):
        super().pullUpdate()         

    def __init__(self, frame):
        '''
        constructor
        '''
        
        self.frame = frame
            
        self.setup('')

class invByMakePage(oneInPage):
    '''
    reads in a dealerID
    returns inventory grouped by new/used, make, and on hold/off hold
    '''
    
    def setupUpdate(self):
        
        #sql query
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
        
        #updates
        self.idLabel.configure(text = 'Enter DealerID here:')
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        self.idInput.bind("<Return>", lambda event: self.pullChecks(event, sqlIn, 'dealer'), add = "+")
        self.sendButton.bind("<Button-1>", lambda event: self.pullChecks(event, sqlIn, 'dealer'))

    def __init__(self, frame):
        '''
        constructor
        '''
        
        self.frame = frame
        
        self.setup('')
        
class importByDayPage(twoInPage):
    '''
    reads in a dealerID and an number of days
    retuns all imports that ran in that number of days behind today, timestamps, and other information on the feed
    '''
    
    def setupUpdate(self):
        
        #sql query
        self.sqlIn = """select si.ImportName, fi.FileName, ih.FileVersionID, ih.HistoryDate
                    from integration..Import_History ih
                    left join Integration..file_version fv on ih.FileVersionID = fv.FileVersionID
                    left join Integration..File_Info fi on fv.fileid = fi.FileID
                    left join Integration..Source_Import si on si.ImportProcessorID = ih.ImportProcessorID
                    where ih.dealerid = 
                    and ih.HistoryDate > dateadd(day, -
                    order by ih.HistoryDate desc"""
        
        #updates
        self.idLabel.configure(text = 'Enter dealer ID here:')
        self.textLabel.configure(text = 'Enter number of days to search:')
        self.textInput.configure(width = self.dayInputCharLimit)
        
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        self.idInput.bind("<Tab>", lambda event: self.textFocus(), add = '+')
        self.textInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.textInputCharLimit, self.textInput))
        self.textInput.bind("<Return>", lambda event: self.pullCheckID(event, self.sqlIn, 'dealer,day'), add = '+')
        self.sendButton.bind("<Button-1>", lambda event: self.pullCheckID(event, self.sqlIn, 'dealer,import'))
        
    def __init__(self, frame):
        '''
        constructor
        '''
        
        self.frame = frame
        
        self.setup('')
        
class importByImportPage(twoInPage):
    '''
    reads in a dealerID and an import name (allows partial import names)
    returns all import runs for that import name, timestamps, and other information on the feed
    '''
    
    def setupUpdate(self):
        
        #sql query
        self.sqlIn = """select si.ImportName, fi.FileName, ih.FileVersionID, ih.HistoryDate
                        from integration..Import_History ih
                        left join Integration..file_version fv on ih.FileVersionID = fv.FileVersionID
                        left join Integration..File_Info fi on fv.fileid = fi.FileID
                        left join Integration..Source_Import si on si.ImportProcessorID = ih.ImportProcessorID
                        where ih.dealerid = 
                        and ih.ImportProcessorID in (select ImportProcessorID from Integration..Source_Import where ImportName like '%
                        and ih.HistoryDate > dateadd(day, -30, getDate())
                        order by ih.HistoryDate desc"""
        
        #updates
        self.idLabel.configure(text = 'Enter dealer ID here:')
        self.textLabel.configure(text = 'Enter import name here:')
        self.textInput.configure(width = self.textInputCharLimit)
        
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        self.idInput.bind("<Tab>", lambda event: self.textFocus(), add = '+')
        self.textInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.textInputCharLimit, self.textInput))
        self.textInput.bind("<Return>", lambda event: self.pullCheckID(event, self.sqlIn, 'dealer,import'), add = '+')
        self.sendButton.bind("<Button-1>", lambda event: self.pullCheckID(event, self.sqlIn, 'dealer,import'))

    def __init__(self, frame):
        '''
        constructor
        '''
        
        self.frame = frame
        
        self.setup('')
        
class pricingLookupPage(oneInPage):
    '''
    reads in a VIN
    returns all pricing fields on that VIN if it is active
    '''
    
    def setupUpdate(self):
        
        #sql query
        sqlIn = """select 'VIN: ' + vin, 
'Price: ' + cast(isnull(price, 0) as varchar), 
'Lot Price: ' + cast(isnull(lotprice, 0) as varchar), 
'MSRP: ' + cast(isnull(pricemsrp, 0) as varchar), 
'Compare to Price: ' + cast(isnull(compareprice, 0) as varchar), 
'Cost: ' + cast(isnull(cost, 0) as varchar), 
'Invoice Price: ' + cast(isnull(invoiceprice, 0) as varchar), 
'Doc Fee: ' + cast(isnull(docfee, 0) as varchar), 
'Accessory Fee: ' + cast(isnull(AccessoryFee, 0) as varchar), 
'Special Price: ' + cast(isnull(PriceSpecial, 0) as varchar)
from dealersite..inventory
where vin = '
and inventorystatusid = 1"""
        
        #updates
        self.idLabel.configure(text = 'Enter VIN here:')
        self.idInput.configure(width = self.vinInputCharLimit)
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.vinInputCharLimit, self.idInput))
        self.idInput.bind("<Return>", lambda event: self.pullChecks(event, sqlIn, 'vin'), add = "+")
        self.sendButton.bind("<Button-1>", lambda event: self.pullChecks(event, sqlIn, 'vin'))

    def __init__(self, frame):
        '''
        constructor
        '''
        
        self.frame = frame
        
        self.setup('')
        
class pricingLookupByStockPage(twoInPage):
    '''
    reads in a dealerID and stock number pair
    returns all pricing fields on that vehicle if it is active
    '''
    
    def setupUpdate(self):
        
        #sql query
        self.sqlIn = """select 'VIN: ' + vin, 
'Price: ' + cast(isnull(price, 0) as varchar), 
'Lot Price: ' + cast(isnull(lotprice, 0) as varchar), 
'MSRP: ' + cast(isnull(pricemsrp, 0) as varchar), 
'Compare to Price: ' + cast(isnull(compareprice, 0) as varchar), 
'Cost: ' + cast(isnull(cost, 0) as varchar), 
'Invoice Price: ' + cast(isnull(invoiceprice, 0) as varchar), 
'Doc Fee: ' + cast(isnull(docfee, 0) as varchar), 
'Accessory Fee: ' + cast(isnull(AccessoryFee, 0) as varchar), 
'Special Price: ' + cast(isnull(PriceSpecial, 0) as varchar)
from dealersite..inventory
where dealerid = 
and stockNo = '
and inventorystatusid = 1"""
        
        #updates
        self.idLabel.configure(text = 'Enter dealer ID here:')
        self.textLabel.configure(text = 'Enter stock number here:')
        self.textInput.configure(width = self.textInputCharLimit)
        
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.idInputCharLimit, self.idInput))
        self.idInput.bind("<Tab>", lambda event: self.textFocus(), add = '+')
        self.textInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.textInputCharLimit, self.textInput))
        self.textInput.bind("<Return>", lambda event: self.pullCheckID(event, self.sqlIn, 'dealer,stock'), add = '+')
        self.sendButton.bind("<Button-1>", lambda event: self.pullCheckID(event, self.sqlIn, 'dealer,stock'))

    def __init__(self, frame):
        '''
        constructor
        '''
        
        self.frame = frame
        
        self.setup('')

    
class importIDPage(oneInPage):
    '''
    reads in an import name (allows partial import names)
    returns the name of all imports that match and the importProcessorID of the import
    '''
    
    def setupUpdate(self):
        
        #sql query
        sqlIn = """select importname, ImportProcessorID 
            from integration..source_import 
            where importname like '%
            and active = 1"""
        
        #updates
        self.idLabel.configure(text = 'Enter import name here:')
        self.idInput.configure(width = self.textInputCharLimit)
        self.idInput.bind("<KeyPress>", lambda event: self.charCheck(event, self.textInputCharLimit, self.idInput))
        self.idInput.bind("<Return>", lambda event: self.pullChecks(event, sqlIn, 'import'), add = "+")
        self.sendButton.bind("<Button-1>", lambda event: self.pullChecks(event, sqlIn, 'import'))          
        
    def __init__(self, frame):
        '''
        constructor
        '''
        
        self.frame = frame
        
        self.setup('')
                
class doNotExportPage(twoInPage):
    '''
    reads in a where clause and import name (requires exact import name)
    returns the DMS DoNotExport transform for that import
    '''

    #transform sql
    sql2In = ''
        
    def setupUpdate(self):
        self.sql2In = """case when
else isnull(i.donotexport, abs(s.autooffhold - 1)) end 
from #data left join dealersite..inventory i on i.dealerid = #data.dealerid and i.VIN = #data.VIN and i.inventorystatusid = 1 
left join integration..source_import_dealer s on s.dealerid = #data.dealerid and s.importprocessorid = """
        
        #sql query
        sqlIn = """select ImportProcessorID 
            from integration..source_import 
            where importname like '
            and active = 1"""
        
        #updates
        self.idLabel.configure(text = 'Enter case when and then statement here:')
        self.textLabel.configure(text = 'Enter exact import name here:')
        self.idInput.configure(width = int(self.sqlInputCharLimit/4))
        self.idInput.configure(height = 4)
        self.textInput.configure(width = self.textInputCharLimit)
        self.textInput.bind("<Return>", lambda event: self.pullCheckID(event, sqlIn, 'doNotExport,importExact'))
        self.idInput.bind("<Tab>", lambda event: self.textFocus())#, add = '+')
        self.sendButton.bind("<Button-1>", lambda event: self.pullCheckID(event, sqlIn, 'doNotExport,importExact'))
        
    def pullUpdate(self):
        #adds copy button to results page
        ttk.Button(self.frame, text = 'Copy', command = lambda: self.copyText()).grid(row = 2, column = 1)
    
    def __init__(self, frame):
        '''
        constructor
        '''
        
        self.frame = frame
        
        self.setup('')
        