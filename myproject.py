import boto3
from flask import Flask, render_template
from datetime import datetime
import re
import os

application = Flask(__name__)

class s3_helper():

    def __init__(self, bucket, cache = None):
        if cache is None:
            self.s3server = 'https://s3.amazonaws.com/lippe-mbr/'
        else:
            self.s3server = cache

        self.s3 = boto3.resource('s3')
        self.s3bucket = self.s3.Bucket(bucket)

        self.s3_images = []
        self.s3_html = []

    def load(self, tsize):
        table_size = tsize

        # grab images from s3
        for object in self.s3bucket.objects.all():
            self.s3_images.append('<img src="' + self.s3server + object.key + '"/>')

        self.s3_html.append('<table border=1>')

        # build html table in rows of x
        for i,pic in enumerate(self.s3_images):
            if i % table_size == 0:
                self.s3_html.append('<tr>')
            self.s3_html.append('<td>' + pic + '</td>')
            if i % table_size == table_size-1 or i == (len(self.s3_images) - 1):
                self.s3_html.append('</tr>')

        self.s3_html.append('</table>')

        print self.s3_html


@application.route("/")
@application.route("/index")

def cached():
    now = datetime.now()
    s3c = s3_helper('lippe-mbr', 'http://d1csbuudyxotp4.cloudfront.net/')
    s3c.load(5)

    # current date
    user = {'nickname': 'Kris'}
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
                           user=user,
                           time=time,
                           s3_images=s3c.s3_html,
                           local_images=local_html)

@application.route("/nocache")

def uncached():
    now = datetime.now()
    s3c = s3_helper('lippe-mbr')
    s3c.load(5)

    # current date
    user = {'nickname': 'Kris'}
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
                           user=user,
                           time=time,
                           s3_images=s3c.s3_html,
                           local_images=local_html)

if __name__ == "__main__":
    application.run(host='0.0.0.0')

