import mysql.connector

var = 17


db = mysql.connector.connect(
  host="localhost",
  user="decoy",
  password="senai@123",
  database="decoy"
)

cursor = db.cursor()
cursor.execute("SELECT * FROM machine WHERE id = 1")
#cursor.execute("SELECT * FROM orders WHERE num_order = (SELECT max(num_order) FROM orders)")
result = cursor.fetchall()
r = result[0][1]

print(r)


cursor.execute("UPDATE machine SET temperature = 461 WHERE id = 1")
db.commit()



sql= "INSERT INTO historyproduction (num_order,temperature,timestamp) VALUES (12,{0},CURRENT_TIMESTAMP)".format(var)

cursor.execute(sql)

db.commit()
