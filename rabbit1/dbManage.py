#msql connector libs
import mysql.connector

import config 


class DBManage:
    def __init__(self):
        self.db = mysql.connector.connect(
            host = config.host,
            user = config.user,
            password = config.password,
            database = config.database          
        )
        self.cursorDB = self.db.cursor()

    def add_subscriber(self, user_id, user_name):  
        self.cursorDB.execute("INSERT INTO rabbit_table (user_id, user_name) VALUES(%s,%s)", (user_id,user_name))
        self.db.commit()

   
    def subscriber_exists(self, user_id):
        sql_request = 'SELECT * FROM rabbit_table WHERE user_id = ' + str(user_id)
        self.cursorDB.execute(sql_request)
        result = self.cursorDB.fetchall()
       
        #self.cursorDB.close()
        return bool(len(result))

    def get_column(self, table_name, column_name):
        #self.cursorDB.execute('SELECT %s FROM %s', (column_name, table_name))
        sql_request = 'SELECT ' + table_name + ' FROM ' + column_name
        self.cursorDB.execute(sql_request)
        resultRQST = self.cursorDB.fetchall()
        resultSTR = str(resultRQST).replace("[('","").replace("',)]","").replace("',)","").replace(" ('"," ")
        return resultSTR

    def get_price(self, products_name):
        sql_request = 'SELECT price FROM products_table WHERE products_name = \'' + products_name + '\''
        self.cursorDB.execute(sql_request)
        resultRQST = self.cursorDB.fetchall()
        resultSTR = str(resultRQST).replace("[(","").replace(",)]","")
        return resultSTR

    def product_exist(self, products_name):
        sql_request = 'SELECT products_name FROM products_table WHERE products_name = \'' + products_name + '\''
        self.cursorDB.execute(sql_request)
        resultRQST = self.cursorDB.fetchall()
        resultSTR = str(resultRQST).replace("[('","").replace("',)]","")
        return (resultSTR == products_name)

    def get_product_id(self, products_name):
        sql_request = 'SELECT id FROM products_table WHERE products_name = \'' + products_name + '\''
        self.cursorDB.execute(sql_request)
        resultRQST = self.cursorDB.fetchall()
        resultSTR = str(resultRQST).replace("[(","").replace(",)]","")
        return resultSTR

    def add_order(self, id_user, id_product):
        sql_request = "INSERT INTO orders_table (user_who_order, product) VALUES(%s,%s)"
        self.cursorDB.execute(sql_request,(id_user, id_product))
        self.db.commit()

    def get_product_list(self, id_user):
        id_product_list = list()
        product_list = list()

        sql_request = "SELECT product FROM orders_table WHERE user_who_order = " + str(id_user)
        self.cursorDB.execute(sql_request)
        resultRQST = self.cursorDB.fetchall()#id list of products
        
        for i in range(len(resultRQST)):#to clear ,) and (
            id_product_list.append(str(resultRQST[i]).replace("(","").replace(",)",""))
          
        for i in range(len(id_product_list)):
            sql_request = "SELECT products_name FROM products_table WHERE id = " + id_product_list[i]
            self.cursorDB.execute(sql_request)
            resultRQST = self.cursorDB.fetchall()
            product_list.append(str(resultRQST).replace("[('","").replace("',)]",""))
        return product_list

    def delete_orders_by_id_user(self, id_user):
        sql_request = "DELETE FROM orders_table WHERE user_who_order = " + str(id_user)
        self.cursorDB.execute(sql_request)
        self.db.commit()