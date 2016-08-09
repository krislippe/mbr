import boto3
from flask import Flask, render_template
from datetime import datetime
import re
import os
import MySQLdb
import logging

application = Flask(__name__)

class s3_helper():

    def __init__(self, bucket, cache = None):
        db_loc = "mydbinstance.c6dwn43xc81y.us-east-1.rds.amazonaws.com"
        db_name = "myAWSdb"
        db_user = "awsuser"
        db_passwd = "password"

        if cache is None:
            self.s3server = 'https://s3.amazonaws.com/lippe-mbr/'
        else:
            self.s3server = cache

        self.s3 = boto3.resource('s3')
        self.s3bucket = self.s3.Bucket(bucket)

        self.s3_images = []
        self.s3_html = []

        # connect to DB
        self.conn = MySQLdb.connect(db_loc, db_user, db_passwd, db_name)                                                      
        self.db = self.conn.cursor()

    def load(self, tsize):
        table_size = tsize

        # grab images from s3
        for object in self.s3bucket.objects.all():
            self.s3_images.append(object.key)

        self.s3_html.append('<table border=1>')

        # build html table in rows of x
        for i,pic in enumerate(self.s3_images):
            try:
                self.db.execute("SELECT * FROM pictures WHERE objkey=\"%s\"" % pic)
                row = self.db.fetchone()
            except MySQLdb.Error, e:
                try:
                    print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                except IndexError:
                    print "MySQL Error: %s" % str(e)

            if row:
                name = row[0]
                desc = row[1]
                size = str(row[2]) + ' KB'
            else:
                name = "No record found"
                desc = "no description"
                size = "unknown size"

            if i % table_size == 0:
                self.s3_html.append('<tr>')

            self.s3_html.append("<td><table border=0 width=\"100%\"><tr><th bgcolor=\"#DCDCDC\" colspan=2>" + name + "</th></tr>")
            self.s3_html.append("<tr><td rowspan=2 width=200px><img src=\"" + self.s3server + pic + "\"></td>")
            self.s3_html.append("<td valign=\"middle\">" + desc + "</td></tr><tr><td bgcolor=\"E8E8E8\" valign=\"middle\">" + size + "</td></tr></table></td>")

            if i % table_size == table_size-1 or i == (len(self.s3_images) - 1):
                self.s3_html.append('</tr>')

        self.s3_html.append('</table>')

        print self.s3_html
        self.conn.close()


@application.route("/")
@application.route("/index")

def cached():
    now = datetime.now()
    s3c = s3_helper('lippe-mbr', 'http://d1csbuudyxotp4.cloudfront.net/')
    s3c.load(3)

    # current date
    msg = "This website uses CloudFront to cache S3 objects"
    time = str(now)

    # grab local images
    local_images = []

    path = "/home/ubuntu/myproject/static/"

    files = [f for f in os.listdir(path)]
    for f in files:
        if re.search('(.gif)|(.jpg)|(.jpeg)', f):
            local_images.append(f)

    local_html = []
    local_html.append('<table border=1>')

    # build html table in rows of 5
    table_size = 5
    for i,pic in enumerate(local_images):
        if i % table_size == 0:
            local_html.append('<tr>')
        local_html.append('<td><img src="/static/' + pic + '"/></td>')
        if i % table_size == table_size-1 or i == (len(local_images) - 1):
            local_html.append('</tr>')

    local_html.append('</table>')

    # off to gunicorn
    return render_template("index.html",
                           title='Home',
                           msg=msg,
                           time=time,
                           s3_images=s3c.s3_html,
                           local_images=local_html)

@application.route("/nocache")

def uncached():
    now = datetime.now()
    s3c = s3_helper('lippe-mbr')
    s3c.load(4)

    # current date
    msg = "This website does not cache S3 objects"
    time = str(now)

    # grab local images
    local_images = []

    path = "/home/ubuntu/myproject/static/"

    files = [f for f in os.listdir(path)]
    for f in files:
        if re.search('(.gif)|(.jpg)|(.jpeg)', f):
            local_images.append(f)

    local_html = []
    local_html.append('<table border=1>')

    # build html table in rows of 5
    table_size = 5
    for i,pic in enumerate(local_images):
        if i % table_size == 0:
            local_html.append('<tr>')
        local_html.append('<td><img src="/static/' + pic + '"/></td>')
        if i % table_size == table_size-1 or i == (len(local_images) - 1):
            local_html.append('</tr>')

    local_html.append('</table>')

    # off to gunicorn
    return render_template("index.html",
                           title='Home',
                           msg=msg,
                           time=time,
                           s3_images=s3c.s3_html,
                           local_images=local_html)

if __name__ == "__main__":
    application.run(host='0.0.0.0')

