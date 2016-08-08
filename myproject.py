import boto3
from flask import Flask, render_template
from datetime import datetime

application = Flask(__name__)

@application.route("/")
@application.route("/index")

def hello():
    now = datetime.now()
    s3 = boto3.resource('s3')

    images = []
    mybucket = s3.Bucket('lippe-mbr')

    # grab images from s3
    for object in mybucket.objects.all():
        images.append('<img src="https://d1csbuudyxotp4.cloudfront.net/' + object.key + '" width="300" heigh="200">')

    imagehtml = []
    imagehtml.append('<table border=1>')

    # build html table in rows of 3    
    for i,pic in enumerate(images):
        if i % 3 == 0:
            imagehtml.append('<tr>')
        imagehtml.append('<td>' + pic + '</td>')
        if i %3 == 2 or i == (len(images) - 1):
            imagehtml.append('</tr>')

    imagehtml.append('</table>')

    user = {'nickname': 'Kris'}
    posts = [  # fake array of posts
        { 
            'author': {'nickname': 'John'}, 
            'body': 'The date is: ' + str(now)
        },
        { 
            'author': {'nickname': 'Susan'}, 
            'body': 'The weather is warm!!' 
        }
    ]
    return render_template("index.html",
                           title='Home',
                           user=user,
                           posts=posts,
                           images=imagehtml)

if __name__ == "__main__":
    application.run(host='0.0.0.0')

