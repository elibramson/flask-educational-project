from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize the database
db = SQLAlchemy(app)

@app.template_filter('nl2br')
def nl2br_filter(text):
    return text.replace('\n', '<br>')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Post {self.title}>"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@app.route("/")
@app.route("/index")
def index():
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(3).all()
    return render_template("index.html", recent_posts=recent_posts)

@app.route("/posts")
def posts():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template("posts.html", posts=posts)

@app.route("/post/<int:post_id>")
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post_detail.html", post=post)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        
        if not title or not content:
            flash("Title and content are required!", "error")
            return render_template("create.html", title=title, content=content)
        
        try:
            post = Post(title=title, content=content)
            db.session.add(post)
            db.session.commit()
            flash("Post created successfully!", "success")
            return redirect(url_for("posts"))
        except Exception as e:
            db.session.rollback()
            flash("There was an issue creating your post. Please try again.", "error")
            return render_template("create.html", title=title, content=content)
    
    return render_template("create.html")

@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        
        if not title or not content:
            flash("Title and content are required!", "error")
            return render_template("edit.html", post=post)
        
        try:
            post.title = title
            post.content = content
            db.session.commit()
            flash("Post updated successfully!", "success")
            return redirect(url_for("post_detail", post_id=post.id))
        except Exception as e:
            db.session.rollback()
            flash("There was an issue updating your post. Please try again.", "error")
            return render_template("edit.html", post=post)
    
    return render_template("edit.html", post=post)

@app.route("/delete/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    try:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("There was an issue deleting your post. Please try again.", "error")
    
    return redirect(url_for("posts"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500

if __name__ == "__main__":
    # Create the instance folder and database
    with app.app_context():
        db.create_all()

    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=debug)