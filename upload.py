import boto3
import os
import re
import MySQLdb
import random

s3 = boto3.resource('s3')
mybucket = s3.Bucket('lippe-mbr')

path = "/Users/lippek/Documents/pics/"

# connect to DB
conn = MySQLdb.connect("mydbinstance.c6dwn43xc81y.us-east-1.rds.amazonaws.com", "awsuser", "password", "myAWSdb")
db = conn.cursor()

db.execute("SELECT VERSION()")
ver = db.fetchone()
print "Database version : %s " % ver

# grab files from directory
files = [f for f in os.listdir(path)]

for f in files:
    if re.search('(.gif)|(.jpg)|(.jpeg)', f):
        print "Uploading file: %s" % f

        data = open(path + f, 'rb')
        mybucket.put_object(Key=f, Body=data)

        object_acl = s3.ObjectAcl(mybucket.name, f)
        object_acl.load()
        object_acl.put(ACL='public-read')

        description = "test description " + str(random.randint(1, 10000))

        size = int(os.path.getsize(path + f) / 1024)
        print "Size: %s" % size

        desc = "foobar"

        try:
            db.execute("INSERT INTO pictures (objkey, description, size_kb) VALUES (%s, %s, %s)", (f, description, size))
        except MySQLdb.Error, e:
            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error: %s" % str(e)

# commit transactions and print current conents of DB
conn.commit()

db.execute("SELECT * FROM pictures")
rows = db.fetchall()

for row in rows:
    print row

conn.close()

