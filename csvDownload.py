import psycopg2
import configparser
import csv

# Read secret data from the ini file
config = configparser.ConfigParser()
config.read('config.ini')

dbname = config['database']['DB_NAME']
user = config['database']['DB_USER']
host = config['database']['DB_HOST']
password = config['database']['DB_PASSWORD']
port = config['database']['DB_PORT']

# Connect
conn = psycopg2.connect(dbname=dbname, user=user, host=host, password=password, port=port)
cursor = conn.cursor()

# Download all data from the sovdep3587 table
cursor.execute("SELECT * FROM euratlas.sovdep3587")

# Fetch the column names from cursor.description
column_names = [desc[0] for desc in cursor.description]

# Fetch the data
data = cursor.fetchall()

# Save the fetched data into data_output.csv
with open('data_output.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(column_names)  # Write the column names as the first row
    writer.writerows(data)  # Write the data rows

print("Download complete")

cursor.close()
conn.close()
