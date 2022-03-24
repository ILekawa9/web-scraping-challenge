import os
from flask import Flask, render_template, redirect
import scrape_mars
from flask_pymongo import PyMongo


app = Flask(__name__)

app.config["MONGO_URI"] = ('mongodb://localhost:27017/mars_db')
mongo = PyMongo(app)


@app.route('/')
def index():
    mars = mongo.db.images.find_one()
    return render_template("index.html", mars=mars)


@app.route('/scrape')
def scrape():
 	scrape_mars.scrape()
    return redirect('/', code =302)



if __name__ == "__main__":
    app.run(debug=True)
