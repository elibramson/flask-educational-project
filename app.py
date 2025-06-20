from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Post {self.title}>"

@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/posts")
def posts():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template("posts.html", posts=posts)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        try:  
            post = Post(title=title, content=content)
            db.session.add(post)
            db.session.commit()
            return redirect("/")
        except: 
            return "There was an issue adding your record"
    else:
        return render_template("create.html")
        


@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    # Create the instance folder and database
    with app.app_context():
        db.create_all()

    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)