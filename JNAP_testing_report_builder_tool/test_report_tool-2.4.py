#test_report_tool-2.4.py
#Justin Napoliano 
#06/12/2020
#Developed for CoxOil Corporation

#Universal imports 
import platform
import os
import pyodbc 
import pandas as pd
from pandas import ExcelWriter
import logging


#This class creates the sales report.  Others classes can be added
#later to build other types of reports.
class sales_report():
    """
    A class that creates a sales report object.
    initial_parameteres will contain one initial parameters dataframe for each of the product, organization, and calendar tables
    transaction_datframe will contain the component strings to query the sql server, the final query, and the transaction dataframe
    """
    def __init__(self):
        logging.info('Initiating Sales Report Object')
        self.inital_parameters = get_initial_parameters()
        self.transaction_dataframe = create_transaction_dataframe(self.inital_parameters)

#The Selection Levels Class can be used with any report.  IT is 
#dynamically created.  It will build tables with user selected levels
#to create custom reports from

class create_transaction_dataframe():
    """
    A class that will create a dataframe object of transactions as defined by the get_initial_parameters dataframe objects

    """
    def __init__(self,initial_parameters):
        logging.info('Initiating the transaction dataframe')
        self.organization_table_query = self.create_organization_table_query(initial_parameters.organization_table_lookup)
        self.product_table_query = self.create_product_table_query(initial_parameters.product_table_lookup)
        self.calendar_table_query = self.create_calendar_table_query(initial_parameters.calendar_table_lookup, initial_parameters.sql_connection)
        self.isf_table = self.create_isf_table(initial_parameters.sql_connection)

    def create_organization_table_query(self,organization_table_lookup):
        logging.info('Creating organization table query')
        select_list: list = organization_table_lookup['level_str'].to_list()
        select_list_str = ['O.' + item for item in select_list]
        select_list_str = str(select_list_str)
        select_list_str = select_list_str.replace("'", "")
        select_list_str = select_list_str[1:-1] 
        condition = '[{}] IN ({})'.format(organization_table_lookup['level_str'][0], str(organization_table_lookup['sub_levels'][0])[1:-1])
        for i in range(1,len(organization_table_lookup))  :
            if organization_table_lookup.at[i, 'can_select']  == True:
                addition = ' AND [{}] IN ({})'.format(organization_table_lookup.at[i, 'level_str'], str(organization_table_lookup.at[i,'sub_levels'])[1:-1])
                condition = condition + addition 
        select_condition = (select_list_str,condition)
        logging.debug('Select condition for organization table is {}'.format(select_condition))
        return(select_condition)


    def create_product_table_query(self,product_table_lookup):
        logging.info('creating product table query')
        select_list: list = product_table_lookup['level_str'].to_list()
        select_list_str = ['P.' + item for item in select_list]
        select_list_str = str(select_list_str)
        select_list_str = select_list_str.replace("'", "")
        select_list_str = select_list_str[1:-1] 
        condition = ''
        for i in range(len(product_table_lookup))  :
            if product_table_lookup.at[i, 'can_select']  == True:
                addition = ' AND [{}] IN ({})'.format(product_table_lookup.at[i, 'level_str'], str(product_table_lookup.at[i,'sub_levels'])[1:-1])
                condition = condition + addition 
        select_condition = (select_list_str,condition)
        logging.debug('Select condition for product table is {}'.format(select_condition))
        return(select_condition)


    def create_calendar_table_query(self,calendar_table_lookup, sql_connection):
        logging.info('creating calendar table query')
        column_query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS  WHERE TABLE_NAME = 'Calendar' "
        level_str_list = pd.read_sql_query(column_query, sql_connection)
        level_str_list = level_str_list['COLUMN_NAME'].to_list()
        level_str_list = ['C.' + item for item in level_str_list]
        level_str_list = str(level_str_list)
        level_str_list = level_str_list.replace("'", "")
        level_str_list = level_str_list[1:-1] 
        row = calendar_table_lookup[calendar_table_lookup['user_selected'] == True]
        start_date = row.date_range[row.index[0]][0]
        end_date = row.date_range[row.index[0]][1]
        condition = 'AND C.Day BETWEEN {} AND {}'.format(start_date, end_date)
        select_condition = (level_str_list, condition)
        logging.debug('Select condition for calendar table is {}'.format(select_condition))
        return select_condition
        

    def create_isf_table(self,sql_connection):
        logging.info('creating the isf table')
        isf_table_select = ('ISF.Qty_Sold, ISF.Extended_Cost,ISF. Extended_Sales')
        #print(self.organization_table_query[0])
        select_statement: str = 'SELECT {}, {}, {}, {}'.format(self.organization_table_query[0], self.product_table_query[0], self.calendar_table_query[0], isf_table_select)
        from_statement: str = ' FROM Item_Sales_Fact AS ISF INNER JOIN Organization AS O ON ISF.Organization_key = O.organization_key INNER JOIN Calendar AS C ON ISF.Calendar_key = C.calendar_key INNER JOIN Product AS P ON ISF.Product_Key = P.Product_Key' 
        conditions: str = ' WHERE {} {} {}'.format(self.organization_table_query[1], self.product_table_query[1], self.calendar_table_query[1])
        query: str = select_statement + from_statement + conditions
        logging.debug('query for isf table is {}'.format(query))
        #print(query)
        print('********************************************************')
        print('Creating your report.  This could take a little while.\n')
        print('********************************************************')
        isf_table_df = pd.read_sql_query(query, sql_connection)
        #print(query)
        #print(isf_table_df)
       
        return isf_table_df

class get_initial_parameters():
    """
    A class that gets the initial parameters from the user
    to use in constructing a dataframe of transactions
    """
    #initiates the lookup tables with user selected values for each table from the isf query
    def __init__(self):
        """
        initiates all of the lookup tables that will later be used to construct a query 
        to create a large dataframe of transactions
        """
        logging.info('Inititating sales_report.initial_parameters')
        self.sql_connection = self.connect()
        self.product_table_lookup = self.create_product_table_lookup()
        self.calendar_table_lookup = self.create_calendar_table_lookup()
        logging.info('Initated sales_report.inital_parameters')
 
    
    #Creates the connection object to use for all queries in the program 
    def connect(self):
        server = '' 
        database = 'Testing' 
        username = 'jnapolitano' 
        password = '' 
        driver='/usr/local/lib/libmsodbcsql.17.dylib'
        return pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    

    def create_organization_table_lookup(self):
        logging.info('Creating organization table lookup')
        level_str = pd.Series(['Location_ID', 'Organization_Key', 'Location_Desc', 'Last_Tank_Reading_Date', 'First_Transaction_Date', 'Closing_Date', 'GPS_Latitude','GPS_Longitude', 'GPS_Address1','GPS_State','GPS_City','GPS_Zip', 'Corp_Site', 'Time_Zone_ID', 'Site_ID_Formatted', 'Business_Entity_desc', 'Business_Entity_id', 'Corporate_desc','Corporate_id', 'Supervisor_desc', 'Supervisor_id', 'Site_desc', 'Site_id', 'T_Supervisor_desc', 'T_Supervisor_id', 'State_desc', 'State_id', 'PB_Cigs_Zone_desc', 'PB_Cigs_Zone_id', 'Pizza_Brand_desc', 'Pizza_Brand_id', 'Coke_Union_City_desc', 'Coke_Union_City_id' ])
        select_order = pd.Series([0,0,0,0,0,0,0,0,0,4,3,0,0,0,0,0,2,0,0,0,0,0,1,5,0,0,0,0,6,0,7,0,0])
        table_num = pd.Series([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        table_str = pd.Series(['Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization','Organization'])
        can_select = pd.Series([False, False, False, False, False , False, False, False, False, True, True, False, False, False, False, False, True, False, False, False, False, False, True, True, False, False, False, False, True, False, True, False, False])
        #user_selected = pd.Series([False, False, False, False, False , False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False])
        sub_levels = pd.Series([[],[],[],[],[], [], [] , [] , [] , [], [] , [], [] ,[] , [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [] , [] ,[]])
        sub_level_select = pd.Series([None, None, None, None, None, None, None, None, None,'[GPS_State]','[GPS_City], [GPS_State]', None, None, None, None, None, '[Business_Entity_id], [Business_Entity_desc]', None, None, None, None, None, '[Site_id], [T_Supervisor_desc], [Business_Entity_desc], [GPS_City], [GPS_State]' , '[T_Supervisor_desc]', None, None, None, None, '[PB_Cigs_Zone_id], [PB_Cigs_Zone_desc]', None, '[Pizza_Brand_id], [Pizza_Brand_desc]' , None, None])   
        organization_table_dict = {
            'level_str' : level_str,
            'select_order' : select_order, #hierarchy value in descending order.  #False means that the level is paired with another level.  
            'table_num':table_num,
            'table_str':table_str, 
            'can_select': can_select,
            #'user_selected': user_selected,
            'sub_levels': sub_levels,
            'sub_level_select' : sub_level_select
        }
    
        organization_table_lookup_df = pd.DataFrame(organization_table_dict)
        organization_table_lookup_df.sort_values(by='select_order', ascending=False, inplace=True)
        organization_table_lookup_df.reset_index(inplace=True, drop = 'index')
        #print(organization_table_lookup_df)
        #self.select_levels(organization_table)  #passes the current table to the select_levels function to cooose the levels.  Ie state, zip, etc
        self.select_sub_levels(organization_table_lookup_df)  #passes the updated table to the selecte_sub_levels_function.  Allows users to pick the specific states, citieds, etc they want to include in the reports
        logging.info('returned oranization table lookup')
        return organization_table_lookup_df


    def create_product_table_lookup(self):
        logging.info('creating product table lookup')
        level_str = pd.Series(['Product_Key', 'UPC_Sell_Unit_Desc', 'UPC', 'Sell_Unit_Desc', 'Sell_Unit_Qty', 'Item_ID', 'Item_Desc', 'Sub_Category_ID', 'Sub_Category_Desc', 'Category_ID', 'Category_Desc', 'Department_ID','Department_Desc', 'Size_Desc', 'Item_Type', 'Create_Date', 'Ent_Item_Number', 'UPC_Discontinue_Date', 'Scan_Modifier', 'IsPurchasable', 'Purchase_Discontinue_Date', 'IsSellable', 'Sales_Discontinue_Date', 'Audit_Flag'])
        select_order = pd.Series([0,0,0,0,0,1,0,2,0,3,0,4,0,0,0,0,0,0,0,0,0,0])
        table_num = pd.Series([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0])
        table_str = pd.Series(['Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product','Product'])
        can_select = pd.Series([False, False, False, False, False, True, False, True, False, True, False, True, False, False, False, False, False, False, False, False, False, False, False, False])
        user_selected = pd.Series([False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False])
        sub_levels = pd.Series([[] , [], [] ,[] ,[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [] , [] ,[]])
        sub_level_select = pd.Series([None, None, None, None,None,  '[Item_ID], [Item_Desc], [Sub_Category_ID], [Sub_Category_Desc], [Category_ID], [Category_Desc]', None, '[Sub_Category_ID], [Sub_Category_Desc], [Category_ID], [Category_Desc], [Department_ID], [Department_Desc]', None, '[Category_ID], [Category_Desc], [Department_ID], [Department_Desc]', None, '[Department_ID], [Department_Desc]', None, None , None, None, None, None, None, None, None, None , None, None])   
        product_table_dict = {
            'level_str' : level_str,
            'select_order' : select_order, #hierarchy value in descending order.  #False means that the level is paired with another level.  
            'table_num':table_num,
            'table_str':table_str, 
            'can_select': can_select,
            'user_selected': user_selected,
            'sub_levels': sub_levels,
            'sub_level_select' : sub_level_select
        }
        #print(len(level_str), len(select_order), len(table_num), len(table_str), len(can_select), len(user_selected), len(sub_levels))
        product_table_df = pd.DataFrame(product_table_dict)
       #product_table_df.set_index('level_str', inplace=True, drop='index')
        product_table_df.sort_values(by='select_order', ascending=False, inplace=True)
        product_table_df.reset_index(inplace=True, drop = 'index')
        #print(organization_table_lookup_df)
        #self.select_levels(organization_table)  #passes the current table to the select_levels function to cooose the levels.  Ie state, zip, etc
        #print(product_table_df)
        self.select_sub_levels(product_table_df)  #passes the updated table to the selecte_sub_levels_function.  Allows users to pick the specific states, citieds, etc they want to include in the reports
        logging.info('returned product table lookup')
        return product_table_df


    def create_calendar_table_lookup(self):
        logging.info('creating calendar table lookup')
        prompt = pd.Series(
            [
                'Today'
                ,'Yesterday'
                ,'Date_Range'
                , 'Select_Date'
                , 'Last N Days'
                , 'Last N Weeks'
                , 'Last N Months'
                , 'Month_To_Date'
            ]
        )
       
        calendar_lookup_table_df = pd.DataFrame()
        calendar_lookup_table_df['prompt'] =  prompt
        calendar_lookup_table_df['user_selected'] = self.select_date_range(calendar_lookup_table_df)
        calendar_lookup_table_df['user_input'] = self.input_date_range(calendar_lookup_table_df)
        calendar_lookup_table_df['date_range'] = self.sql_date_range(calendar_lookup_table_df)
       
        #print(calendar_lookup_table_df)
        logging.info('Returned calendar table lookup')
        return calendar_lookup_table_df

   
    def select_date_range(self, calendar_lookup_table_df):
        logging.info('User Selecting desired date range')
        user_selected = pd.Series(
            [
                False
                ,False
                ,False
                ,False
                ,False
                ,False 
                ,False
                ,False
            ]
        )

        user_selection_int: int = None
        #prompt = calendar_lookup_table_df['prompt']
        #print(prompt)
        
        while calendar_lookup_table_df.prompt.any():
            print(calendar_lookup_table_df.prompt)
            print('\n')
            print("Current Selection: \n")
            print("Enter the integer associated to the Date Range* value you want to add to the report")
            print("-----------------------------------------------------------------------------")
            user_selection = input("User Input: \n").lower()
            #print(user_selection)
            #D finishes the loop and returns the list
                #current_table_row['level_str'] = selected_values_lst 
            #a fills the list with all available values.  #d will do the same if the user did not select any
            if user_selection == '': 
                logging.info('User entered enter')
                if user_selection_int == None:
                    print("You did not select a data range")
                    logging.info('user did not select a date range')
                    continue
                else:
                    print("-----------------------------------------------------------------------------")
                    user_selected[user_selection] = True
                    return user_selected
                  
            elif user_selection == 'q' or user_selection =='quit':
                return user_selected
         
            #elif current_table_row["user_selected"] == False:
            #    return available_values_df[current_table_row['level_str']].tolist()

            else: 
                try:
                    user_selection_int = int(user_selection)
                    print(calendar_lookup_table_df['prompt'][user_selection_int])
                    user_selected[user_selection_int] = True
                    logging.debug('user selected date range int is: {}'.format(calendar_lookup_table_df['prompt'][user_selection_int]))
                    return user_selected
                except KeyError:
                    logging.error('Key Error')
                    print("Your entry does not match up to a column. Try again\n")
                except ValueError:
                    logging.error('Value Error')
                    print("Your Value is not a character or")


    def input_date_range(self, calendar_lookup_table_df):
        logging.info('creating user_input column of calendar_lookup')
        logging.info('User inputing date range if possible')
        user_input = pd.Series([False, False , (False,False), False, False, False, False, False])
        for i in range(len(calendar_lookup_table_df)) :
      
            if calendar_lookup_table_df.at[i,'user_selected'] == True and i == 0:
                user_input[i] = True
                logging.debug('User input at {} is True'.format(i))
    
            elif calendar_lookup_table_df.at[i,'user_selected'] == True and i == 1:
                user_input[i]  = True
                logging.debug('User input at {} is True'.format(i))

            elif calendar_lookup_table_df.at[i,'user_selected'] == True and i == 2:
                while calendar_lookup_table_df.at[i,'user_selected'] == True:
                    start_date = input("Enter a start date\n\n")
                    #create a check here
                    end_date = input("Enter an end Date\n")
                    #create a check here
                    user_input[i] = (start_date,end_date)
                    logging.debug('User input at {} is {}'.format(i,(start_date, end_date)))
                    break

            elif calendar_lookup_table_df.at[i,'user_selected'] == True and i == 3:
                #print('test')
                user_response = input('Enter a Date:\n')
                #calendar_lookup_table_df.at[i,'user_input'] =(user_response, user_response)
                user_input[i] = user_response
                logging.debug('User input at {} is {}'.format(i, user_response))
            elif calendar_lookup_table_df.at[i,'user_selected'] == True and i == 4:
                user_response = input('Enter The number of days back:\n')
                #calendar_lookup_table_df.at[i,'user_input'] = (user_response, user_response)
                user_input[i] = user_response
                logging.debug('User input at {} is {}'.format(i, user_response))
            elif calendar_lookup_table_df.at[i,'user_selected'] == True and i == 5:
                user_response = input('Enter The number of weeks back:\n')
                #calendar_lookup_table_df.at[i,'user_input'] = (user_response, user_response)
                user_input[i] = user_response
                logging.debug('User input at {} is {}'.format(i, user_response))
            elif calendar_lookup_table_df.at[i,'user_selected'] == True and i == 6:
                user_response = input('Enter The number of Months back:\n')
                #calendar_lookup_table_df.at[i,'user_input'] = (user_response, user_response)
                user_input[i] = user_response
                logging.debug('User input at {} is {}'.format(i, user_response))
            elif calendar_lookup_table_df.at[i,'user_selected'] == True and i == 7:
                #calendar_lookup_table_df.at[i,'user_input'] = (True,True)
                user_input[i] =  True
                logging.debug('User input at {} is True'.format(i))
            else:
               continue
        #print(user_input)
        logging.info('Returned user input column of calendar table lookup')
        return(user_input)
            #print(calendar_lookup_table_df)
        

    def sql_date_range(self, calendar_lookup_table_df):
        logging.info('Creating date_range column of calendar table lookup')
        date_range = pd.Series(
            [
                (
                    'CONVERT(date, GETDATE())'
                    ,'CONVERT(date, GETDATE())'
                )
                ,
                (
                    'DATEADD(day,-1, CONVERT(date, GETDATE()))'
                    ,'DATEADD(day,-1, CONVERT(date, GETDATE()))'
                )
                ,
                ( 
                    calendar_lookup_table_df['user_input'][2][0]
                    ,calendar_lookup_table_df['user_input'][2][1]
                )
                ,
                (
                    calendar_lookup_table_df['user_input'][3]
                    ,calendar_lookup_table_df['user_input'][3]
                ) 
                ,
                (
                    'DATEADD(day,-{}, CONVERT(date, GETDATE()))'.format(calendar_lookup_table_df['user_input'][4])
                    ,'DATEADD(day,-1, CONVERT(date, GETDATE()))'
                )
                , 
                (
                    '(DATEADD(dd,  6, DATEADD(ww, DATEDIFF(ww, 0, DATEADD(dd, -1, CURRENT_TIMESTAMP)) - {}, 0))'.format(calendar_lookup_table_df['user_input'][5])
                    ,'DATEADD(dd,  6, DATEADD(ww, DATEDIFF(ww, 0, DATEADD(dd, -1, CURRENT_TIMESTAMP)) - 1, 0)))'
                )
                ,
                (
                    'DATEADD(month, -1, DATEADD(DAY, 1, EOMONTH(GETDATE(), - {})))'.format(calendar_lookup_table_df['user_input'][6])
                    ,'EOMONTH(GETDATE(), -1)'
                )
                , 
                (
                    'DATEADD(DAY, 1, EOMONTH(GETDATE(), -1))'
                    ,'CONVERT(day, GETDATE()'
                )
            ]
        )
        #print(date_range)
        logging.info('Returned date column of calendar table lookup')
        return date_range 

       
    def select_sub_levels(self,working_table):
        logging.info('selecting sub levels')
        i: int = 0 
        j: int = 1
        for row in working_table.itertuples():

            if row.can_select == True:
         
                sub_level_list : list = working_table['sub_levels'][0:i]
                level_list : list = working_table['level_str'][0:i]
                level_sub_level_list = tuple(zip(level_list, sub_level_list))
                #print(select_list)
                try:
                    working_table.at[i, 'sub_levels'] = self.select_sub_level(level_sub_level_list, row, i)
                    self.display_current_table(working_table,i, j)
                    i += 1
                    j+=1
                    logging.debug('Returned sub levels at {}'.format(i))
                except KeyError:
                    print("Key Error")
                    logging.error('Key Error')


    def select_sub_level(self, working_lst, current_table_row, i):
        logging.info('User Selecting individual sub-level')
        selected_values_lst : list = []
        query : str = ''
        k: str = ''
        v: list = []
        tup: tuple = ()
        addition: str = ''
        user_selection: str = ''
        user_selection_int: int = -1 
        available_values_df = pd.DataFrame()
        if i == 0:
            query = 'SELECT DISTINCT {} FROM {}'.format(current_table_row.sub_level_select, current_table_row.table_str)
            #print('Query = {}'.format(query))
        else:
            tup = working_lst[0]
            k = tup[0]
            v = tup[1]
            query = 'SELECT DISTINCT {} FROM {} WHERE {} IN ({})'.format(current_table_row.sub_level_select, current_table_row.table_str,k,str(v)[1:-1] )
            for tup in working_lst[1:]:
                addition = ' AND {} IN ({})'.format(tup[0], str(tup[1])[1:-1])
                query = query + addition 
            #print('Query = {}'.format(query))
        available_values_df = pd.read_sql_query(query, self.sql_connection)   
        #logging.info('select_sub_level query at {} is {} '.format(i, query)) 
        print("This is the selection table\n")
        #print(available_values_df)
        
        while current_table_row:
            print(available_values_df)
            print('\n')
            print("Current Selection: \n")
            print(selected_values_lst)
            print('\n')
            print("Enter the integer associated to the *{}* value you want to add to the report".format(current_table_row.level_str))
            print("Enter (d)one when finished\n")
            print("-----------------------------------------------------------------------------")
            user_selection = input("User Input: ").lower()
            #print(user_selection)
            #D finishes the loop and returns the list
            if user_selection == 'd' or user_selection == 'done':
                if selected_values_lst == []:
                    selected_values_lst = available_values_df[current_table_row.level_str].tolist()
                print("-----------------------------------------------------------------------------")
                return selected_values_lst
                #current_table_row['level_str'] = selected_values_lst 
            #a fills the list with all available values.  #d will do the same if the user did not select any
            elif user_selection == 'a' or user_selection == 'all':
                
                selected_values_lst = available_values_df[current_table_row.level_str].tolist()
                print("-----------------------------------------------------------------------------")
                return selected_values_lst
                #current_table_row['level_str'] = selected_values_lst                 
            #quit cancels the search all together and returns false.  
            elif user_selection == '': 
                if selected_values_lst == []:
                    selected_values_lst = available_values_df[current_table_row.level_str].tolist()
                print("-----------------------------------------------------------------------------")
                logging.debug('user selected sub values at {} are {}'.format(i, str(selected_values_lst)))
                return selected_values_lst
            elif user_selection == 'q' or user_selection =='quit':
                return False       
            
            #elif current_table_row["user_selected"] == False:
            #    return available_values_df[current_table_row['level_str']].tolist()

            else: 
                try:
                    user_selection_int = int(user_selection)
                    print(available_values_df[current_table_row.level_str][user_selection_int])
                    if available_values_df[current_table_row.level_str][user_selection_int] in selected_values_lst:
                        print("You already selected {}.  Try again\n".format(available_values_df[current_table_row.level_str][user_selection_int]))
                    else: 
                        selected_values_lst.append(available_values_df[current_table_row.level_str][user_selection_int])
                        logging.debug('appended {} to selected sub levels'.format(available_values_df[current_table_row.level_str][user_selection_int]))
                except KeyError:
                    print("Your entry does not match up to a column. Try again\n")
                    logging.error('Key Error')
                except ValueError:
                    print("Your Value is not a character or")
                    logging.error('Value Error')

    def display_current_table(self, working_table,i,j ):
        logging.info('Displaying the current table to the user')
        query : str = ''
        k: str = ''
        v: list = []
        tup: tuple = ()
        addition: str = ''

        sub_level_list = working_table['sub_levels'][0:i+1]
        level_list = working_table['level_str'][0:i+1]
        level_sub_level_list = tuple(zip(level_list, sub_level_list))
        select_list = working_table['level_str'][0:j+1].tolist()
        current_table_row = working_table.iloc[i]

        select_list_str = str(select_list)
        select_list_str = select_list_str.replace("'", "")
        select_list_str = select_list_str[1:-1] 
        current_table_df = pd.DataFrame()
        if i == 0:

            sub_list = current_table_row.sub_levels
            query = 'SELECT DISTINCT {} FROM {} WHERE {} IN ({})'.format(current_table_row.level_str, current_table_row.table_str,current_table_row.level_str,str(sub_list)[1:-1] )
            
        else: 
            tup = level_sub_level_list[0]
            k = tup[0]
            v = tup[1]
            query = 'SELECT DISTINCT {} FROM {} WHERE {} IN ({})'.format(select_list_str, current_table_row.table_str,k,str(v)[1:-1] )
            for tup in level_sub_level_list[1:]:
                addition = ' AND {} IN ({})'.format(tup[0], str(tup[1])[1:-1])
                query = query + addition 

        print("\n\n\n\n\n")
        print("This is your current Table")
        print("\n")
        #rint(query)
        current_table_df = pd.read_sql_query(query, self.sql_connection)
        print(current_table_df)    
        print("\n\n\n\n\n")


class report():

    def __init__(self):
        logging.info('Initiating Report Class')

        self.report_selection = self.select_report(True)
        self.report_sorted = self.report_sorter(self.report_selection)
        
        logging.info('Report Class Initiated')

    def report_sorter(self,report_selection):
        logging.info('Report Sorter Called')
        test = int(report_selection[0])
        print(test)
        if report_selection == False:
            print('false')
            logging.info('Report Sorter Returned False')
            return False
        elif report_selection[0] == 0 :
            logging.info('Report Sorter is Creating a Sales Report')
            self.sales_report = sales_report()
            logging.info('Report Sorter Created a Sales Report')
            logging.info('Report_Sorter will return True')
            return True
    def select_report(self,report_selection):
        logging.info('User is selecting report')
        available_reports_dict = {0 :"Sales", 1 :"some other report"}
        available_reports_list = []

        for key in available_reports_dict:
            available_reports_list.append(key)    

            while report_selection:  
                print("\n")
                #print(available_reports_list)
                print("Select a Report\n")
                for key,value in available_reports_dict.items():
                    print(key,value)
                    print("\n")
                print("-----------------------------------------------------------------------------")
                report_selection = input("User input: ")

                if report_selection == 'q' or report_selection == 'quit':
                    return False
                else:
                    try: 
                        report_selection = int(report_selection)
                        logging.debug('User Selected {}'.format(available_reports_dict[int(report_selection)]))
                        return (report_selection, available_reports_dict[int(report_selection)])
                    except ValueError:
                        print('The entry is not an integer.\n')
                        print("Enter <q>uit to quit or try again")
                        print("-----------------------------------------------------------------------------")  
                        logging.error('Value Error')


class universal_settings():

    def __init__(self):
        self.cwd = (os.path.dirname(os.path.realpath(__file__)))
        self.user = os.getlogin()
        self.pandas_options = self.set_pandas_options(self.cwd)
        self.logging_options = self.set_logging_options(self.cwd)
        logging.info('Univeral Settings Successfully Set')
        

    def set_pandas_options(self,cwd):
        pd.set_option('display.max_rows', None)
        return True
    def set_logging_options(self,user):
        FORMAT = '%(asctime)-15s %(levelname)s: %(funcName)s %(message)s'
        logging.basicConfig(filename='{}/log.log'.format(self.cwd),format=FORMAT, level=logging.DEBUG)
        return True
  
        

class write_to_excel():
    
    def __init__(self,final_report,cwd): 
        logging.info('Writing to Excel')
        self.path = cwd + '/program_output.xlsx'
        self.writer = ExcelWriter(self.path)
        self.exported_to_excel = self.export_to_excel(final_report, cwd, self.writer, self.path)

    def export_to_excel(self, final_report, cwd, writer, path):
        logging.info('Exporting to Excel')
        print('********************************************************')
        print('Report is Done.  Exporting to Excel.\n')
        print('********************************************************')
        #cwd = (os.path.dirname(os.path.realpath(__file__)))
        final_report.inital_parameters.organization_table_lookup.to_excel(writer,'organization_table_lookup')
        final_report.inital_parameters.product_table_lookup.to_excel(writer,'product_table_lookup')
        final_report.inital_parameters.calendar_table_lookup.to_excel(writer,'calendar_table_lookup')
        final_report.transaction_dataframe.isf_table.to_excel(writer,'Item_Sales_Fact')
        writer.save()
        print('********************************************************')
        print('Exported to Excel.  You can find the data at {}.\n'.format(path))
        print('********************************************************')
        logging.info('Exported to Excel')
        return True

if __name__ =='__main__':
    universal_settings = universal_settings()
    logging.info('Testing_Main Function')
    print("******************************************")
    print("Cox Oil Report Builder Version 0.0")
    print("Doug...Get Ready to **** Yourself")
    print("******************************************")
    final_report = report()
    write_to_excel = write_to_excel(final_report.sales_report,universal_settings.cwd)
   
#The main function. Intitates the process of selecting the reports.  
#The end.  Watch demo video to see code in action.
    