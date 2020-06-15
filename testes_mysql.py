from datetime import datetime
from MySQLdb import _mysql
import mysql.connector
from parse import *
#from MySQLdb import mysql.connector

#var = 13

#db=_mysql.connect(host="localhost",port=3306,user="decoy",passwd="senai@123",db="decoy")


db = mysql.connector.connect(host="localhost",port=3306,user="decoy",passwd="senai@123",db="decoy")

    #função para alterar valor
#db.query("""UPDATE machine SET temperature = 457 WHERE id = 1""")
    
    
    #funço para ler variavel
cursor = db.cursor()
cursor.execute("""SELECT machine FROM machine WHERE id = 1 """)
result = cursor.fetchall()

#db.query("""SELECT machine FROM machine WHERE id = 1""")
#r=db.store_result()
    #...or...
    #r=db.use_result()

#r=r.fetch_row()

#print(r)

print(result)
print(result[0][2])

#r = "r:{0}".format(r)
#r = parse("((b'{:nr}',),)","{0}".format(r))
#r = r.split(",")

#print(r)

#r = "r:{0}{1}{2}".format(0)
#print(r)

#print("r:{0}".format(3))
#r = "r:" + str(1)
#print(r)
    
    #função para inserir dados na tabela
#db.query("""INSERT INTO historyproduction (num_order,temperature,timestamp) VALUES ("12",{0},CURRENT_TIMESTAMP)""".format(var))


