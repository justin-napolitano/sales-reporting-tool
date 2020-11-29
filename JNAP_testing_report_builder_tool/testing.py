#testing.py
import openpyxl
import os
import pyodbc 
import pandas as pd
from pandas import ExcelWriter
import logging
import platform
import csv

class universal_settings():

    def __init__(self):
        self.cwd = (os.path.dirname(os.path.realpath(__file__)))
        pd.set_option('display.max_rows', None)
        logging.basicConfig(filename='{}/log.log'.format(self.cwd),level=logging.DEBUG)


def create_isf_table(sql_connection):
    logging.info('creating the isf table')
    #isf_table_select = ('ISF.Qty_Sold, ISF.Extended_Cost,ISF. Extended_Sales')
    #print(self.organization_table_query[0])
    #select_statement: str = 'SELECT {}, {}, {}, {}'.format(self.organization_table_query[0], self.product_table_query[0], self.calendar_table_query[0], isf_table_select)
    #from_statement: str = ' FROM Item_Sales_Fact AS ISF INNER JOIN Organization AS O ON ISF.Organization_key = O.organization_key INNER JOIN Calendar AS C ON ISF.Calendar_key = C.calendar_key INNER JOIN Product AS P ON ISF.Product_Key = P.Product_Key' 
    #conditions: str = ' WHERE {} {} {}'.format(self.organization_table_query[1], self.product_table_query[1], self.calendar_table_query[1])
    query: str = "SELECT O.Pizza_Brand_id, O.PB_Cigs_Zone_id, O.T_Supervisor_desc, O.GPS_State, O.GPS_City, O.Business_Entity_id, O.Site_id, O.Supervisor_id, O.Site_desc, O.T_Supervisor_id, O.State_desc, O.Corporate_id, O.State_id, O.PB_Cigs_Zone_desc, O.Pizza_Brand_desc, O.Coke_Union_City_desc, O.Supervisor_desc, O.Location_ID, O.Corporate_desc, O.Organization_Key, O.Business_Entity_desc, O.Site_ID_Formatted, O.Time_Zone_ID, O.Corp_Site, O.GPS_Zip, O.GPS_Address1, O.GPS_Longitude, O.GPS_Latitude, O.Closing_Date, O.First_Transaction_Date, O.Last_Tank_Reading_Date, O.Location_Desc, O.Coke_Union_City_id, P.Department_ID, P.Category_ID, P.Sub_Category_ID, P.Item_ID, P.Size_Desc, P.Purchase_Discontinue_Date, P.IsPurchasable, P.Scan_Modifier, P.UPC_Discontinue_Date, P.Ent_Item_Number, P.Create_Date, P.Item_Type, P.Product_Key, P.Department_Desc, P.UPC_Sell_Unit_Desc, P.Category_Desc, P.Sub_Category_Desc, P.Item_Desc, P.Sell_Unit_Qty, P.Sell_Unit_Desc, P.UPC, P.IsSellable, P.Sales_Discontinue_Date, P.Audit_Flag, C.calendar_key, C.Day, C.Day_of_Week_ID, C.Day_Of_Weej, C.Holiday, C.Type_Of_Day, C.Calendar_Month_No, C.Calendar_Month_Name, C.Calendar_Quarter_No, C.Calendar_Qtr_Desc, C.Calendar_Year, C.Fiscal_Week, C.Fiscal_Period_No, C.Fiscal_Period_Desc, C.Fiscal_Year, ISF.Qty_Sold, ISF.Extended_Cost,ISF. Extended_Sales FROM Item_Sales_Fact AS ISF INNER JOIN Organization AS O ON ISF.Organization_key = O.organization_key INNER JOIN Calendar AS C ON ISF.Calendar_key = C.calendar_key INNER JOIN Product AS P ON ISF.Product_Key = P.Product_Key WHERE [Pizza_Brand_id] IN ('Godfathers', 'Hunt Brothers', 'N A') AND [PB_Cigs_Zone_id] IN ('69') AND [T_Supervisor_desc] IN ('Dennis Mires') AND [GPS_State] IN ('KY') AND [GPS_City] IN ('Fulton') AND [Business_Entity_id] IN (2) AND [Site_id] IN (69)  AND [Department_ID] IN ('17') AND [Category_ID] IN (17) AND [Sub_Category_ID] IN (1701, 1702, 1703, 1705, 1706, 1707, 1708) AND [Item_ID] IN (-703322, -703321, -703316, -703315, -703314, -703313, -703307, -173758, -173757, -173756, -173755, -173754, -173753, -173752, -173751, -173750, -173749, -173748, -173747, -173746, -173745, -173744, -173743, -173742, -172951, -172950, -172949, -172948, -172947, -172946, -172945, -172944, -172943, -172942, -172941, -172940, -172939, -172938, -172937, -172936, -172935, -172934, -172933, -172932, -172931, -172930, -172929, -172928, -172927, -172926, -172925, -172924, -172851, -172838, -172741, -172740, -172739, -172305, -172267, -172266, -172265, -172264, -172263, -172262, -172260, -172259, -172257, -172255, -172254, -172251, -172249, -172248, -172245, -172244, -172243, -172242, -172241, -172237, -172236, -172235, -172234, -172233, -172232, -172230, -172229, -172226, -172225, -172224, -172223, -172222, -172221, -172220, -11123, -11122, -11121, -11120) AND C.Day BETWEEN DATEADD(month, -1, DATEADD(DAY, 1, EOMONTH(GETDATE(), - 5))) AND EOMONTH(GETDATE(), -1)"
    logging.debug('query for isf table is {}'.format(query))
    #print(query)
    print('********************************************************')
    print('Creating your report.  This could take a little while.\n')
    print('********************************************************')
    isf_table_df = pd.read_sql_query(query, sql_connection)
    #print(query)
    #print(isf_table_df)
    return isf_table_df

class sql_connection():

    def __init__(self):
        logging.debug('Connecting To Database')
        self.system = platform.system()
        self.system = self.system.lower()
        print(self.system)
        if self.system =='windows':
            driver = '{ODBC Driver 17 for SQL Server}'
        else:
            driver = '/usr/local/lib/libmsodbcsql.17.dylib'
        server = '' 
        database = 'Testing' 
        username = 'jnapolitano' 
        password = '' 
        #driver='/usr/local/lib/libmsodbcsql.17.dylib'
        self.connection = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        self.cursor = self.connection.cursor()

def get_user_info():
    get_enve = os.getenv('USERNAME')
    get_login = os.getlogin()
    print(get_enve)
    print(get_login)



if __name__ =='__main__':
    cwd = (os.path.dirname(os.path.realpath(__file__)))
    path = cwd + '/queries.csv'
    csvfile = open(path, 'r')
    fieldnames = ['DateTime', 'User', 'Query']
    
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            last_row = row
            line_count +=1
        print(f'Processed {line_count} lines.')
        print(last_row[1])

        # this is the last row!
    #username = get_user_info()
    #universal_settings = universal_settings()
    #connection = sql_connection()
    #isf_table = create_isf_table(connection.connection)
    #print(universal_settings.cwd)

   #print(file_writer.log_writer)
   #file_writer.log_writer_close()
   #file_writer.excel_writer_close()

   #log_writer = file_writer().log_writer_open(file_writer().cwd)
   #print(log_writer)
   #file_writer().log_writer_close(log_writer)
