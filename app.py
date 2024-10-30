import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'


# Function to open a connection to the database.db file
def get_db_connection():
    # create connection to the database
    conn = sqlite3.connect('database.db')
    
    # allows us to have name-based access to columns
    # the database connection will return rows we can access like regular Python dictionaries
    conn.row_factory = sqlite3.Row

    #return the connection object
    return conn

# function to retrieve post from database
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id, )).fetchone()
    conn.close()

    if post is None:
        abort(404)

    return post

# use the app.route() decorator to create a Flask view function called index()
@app.route('/')
def index():
    #get connection to db
    conn = get_db_connection()

    #execute query to read all blog posts
    posts = conn.execute("SELECT * FROM posts").fetchall()

    #close connection
    conn.close()

    #send posts to index.html for display
    return render_template('index.html', posts=posts)

# route to create a post
@app.route('/create/', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        #get the data submitted in form
        title = request.form['title']
        content = request.form['content']

        #display error if form item is blank
        #else send blog post to database
        if not title:
            flash("Title is required")
        elif not content:
            flash("Content is required")
        else:
            conn = get_db_connection()
            #insert data into db
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content)) 
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

#route to edit a post
@app.route('/<int:id>/edit/', methods=['GET', 'POST'])
def edit(id):
    #get post to be edited from db
    post = get_post(id)

    if request.method == 'POST':
        #get form data
        title = request.form['title']
        content = request.form['content']

        #display error if form item is blank
        if not title:
            flash("Title is required")
        elif not content:
            flash("Content is required")
        else:
            conn = get_db_connection()
            #insert data into db
            conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, id)) 
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

#route to delete post
@app.route('/<int:id>/delete/', methods=['POST',])
def delete(id):
    #get the post from db
    post = get_post(id)

    conn= get_db_connection()
    conn.execute('DELETE from posts WHERE id = ?', (id, ))
    conn.commit()
    conn.close()

    flash("'{}' was successfully deleted!".format(post['title']))

    return redirect(url_for('index'))

app.run()