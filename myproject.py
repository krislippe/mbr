from flask import Flask, render_template
from datetime import datetime

application = Flask(__name__)

@application.route("/")
@application.route("/index")

def hello():
    now = datetime.now()

    user = {'nickname': 'Kris'}
    posts = [  # fake array of posts
        { 
            'author': {'nickname': 'John'}, 
            'body': 'The date is: ' + str(now)
        },
        { 
            'author': {'nickname': 'Susan'}, 
            'body': 'The weather is nice!' 
        }
    ]
    return render_template("index.html",
                           title='Home',
                           user=user,
                           posts=posts)

if __name__ == "__main__":
    application.run(host='0.0.0.0')

