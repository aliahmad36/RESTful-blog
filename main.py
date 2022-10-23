from flask import Flask, redirect, request, url_for, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import sqlite3
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

#create db and table
with sqlite3.connect("posts.db") as db:
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blog_post(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(250) NOT NULL UNIQUE,
    subtitle VARCHAR(250) NOT NULL,
    date VARCHAR(250) NOT NULL,
    body TEXT NOT NULL,
    author VARCHAR(250) NOT NULL,
    img_url VARCHAR(250) NOT NULL
    )
    ''')


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    # body = StringField("Blog Content")
    body = CKEditorField("Blog Content")
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    with sqlite3.connect("posts.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM blog_post")
        all_posts = cur.fetchall()
        # for posts in all_posts:
        #     print(posts)
    return render_template("index.html", posts=all_posts)


@app.route('/post/<int:index>')
def show_post(index):
    post_id = index
    with sqlite3.connect("posts.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM blog_post WHERE id=?", (post_id, ))
        selected_post = cur.fetchone()
    return render_template("post.html", post=selected_post)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/edit-post/<int:post_id>', methods=["POST", "GET"])
def edit_post(post_id):
    # edit_form = CreatePostForm()
    page_title = "Edit Post"

    with sqlite3.connect("posts.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM blog_post WHERE id=?", (post_id, ))
        post = cur.fetchone()
        edit_form = CreatePostForm(
            title=post[1],
            subtitle=post[6],
            img_url=post[5],
            author=post[4],
            body=post[3]
        )
        if edit_form.validate_on_submit():
            cur.execute("UPDATE blog_post SET title=?, subtitle=?, img_url=?, author=?, body=? WHERE id=?",
                        (edit_form.title.data, edit_form.subtitle.data, edit_form.img_url.data, edit_form.author.data,
                         edit_form.body.data, post_id, ))
            return redirect(url_for('show_post', index=post_id))
    return render_template("make-post.html", form=edit_form, page_title=page_title)


@app.route('/make-post', methods=["POST", "GET"])
def add_new_post():
    form = CreatePostForm()
    page_title = "New Post"
    if form.validate_on_submit():
        title = form.title.data
        subtitle = form.subtitle.data
        author = form.author.data
        img_url = form.img_url.data
        body = form.body.data
        today_date = datetime.datetime.now().strftime("%B %d, %Y")
        # print(f"{title}, {subtitle}, {author}, {img_url}, {body}, {today_date}")
        with sqlite3.connect("posts.db") as db:
            cur = db.cursor()
            cur.execute("INSERT INTO blog_post (title, subtitle, author, img_url, body, date) "
                        "VALUES (?, ?, ?, ?, ?, ?)", (title, subtitle, author, img_url, body, today_date, ))
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=form, page_title=page_title)


@app.route('/delete/<post_id>')
def delete_post(post_id):
    with sqlite3.connect("posts.db") as db:
        cur = db.cursor()
        cur.execute("DELETE from blog_post WHERE id=?", (post_id, ))
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)