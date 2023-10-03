import psycopg2

mydb = psycopg2.connect(
  host="localhost",
  user="postgres",
  password="password",
  database="postgres"
)

# Checking if the connection was successful
if (mydb):
    print("Connection successful!")
else:
    print("Connection unsuccessful.")

# Creating a cursor object
mycursor = mydb.cursor()

# Executing a query
# mycursor.execute("drop table chatGPTnews")

# mycursor.execute("CREATE TABLE news (title VARCHAR(1000), author VARCHAR(1000), description VARCHAR(1000), url VARCHAR(1000), urlToImage VARCHAR(1000), publishedAt VARCHAR(1000))")
mycursor.execute("CREATE TABLE chatGPTnews (title VARCHAR(1000), url VARCHAR(1000), publishedAt VARCHAR(100), summary VARCHAR(1000))")
mycursor.execute("ALTER TABLE chatGPTnews ALTER COLUMN summary TYPE VARCHAR(10000)")
mydb.commit()
mycursor.execute("SELECT * FROM chatGPTnews")

# Fetching the results
results = mycursor.fetchall()

# Printing the results
for row in results:
    print(row)

