from flask import Blueprint, render_template,request ,session, redirect,url_for, flash
from blog.db import get_db
import sqlite3
import datetime
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, TextAreaField
from ..forms import PostForm, ReplyPostForm, EditPostForm , EditReplyForm

# define our blueprint
blog_bp = Blueprint('blog', __name__)

def login_required(f):
    @wraps(f)

    
    def check(*args, **kwargs):
        

        if 'username' in session:
            return f(*args, **kwargs)
            
        else:

            return redirect('/login')
            # , next=request.url )
            
    return check


@blog_bp.route('/' , methods = ['GET', 'POST'])
@blog_bp.route('/posts' , methods = ['GET', 'POST'])
@login_required
def index():
    
    add_post_form = PostForm()

    if request.method == "GET":

        # get the DB connection
        db = get_db()

        # retrieve all posts
        posts = db.execute(
            'SELECT p.id, title, body, created, author_id, firstname , lastname'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' ORDER BY created DESC'
        ).fetchall()

        # render 'blog' blueprint with posts
        # return render_template('blog/index.html', posts = posts )

    else :
        
        if add_post_form.validate_on_submit():

            # read post values from the form
            title = add_post_form.title.data
            body = add_post_form.body.data 

            # read the 'uid' from the session for the current logged in user
            author_id = session['uid']

            # get the DB connection
            db = get_db()
            
            # insert post into database
            try:
                # execute the SQL insert statement
                db.execute("INSERT INTO post (author_id, title, body) VALUES (?, ?,?);", (author_id, title, body))
                
                # commit changes to the database
                db.commit()
                flash('You were successfully Add')
                return redirect('/posts') 

            except sqlite3.Error as er:
                print(f"SQLite error: { (' '.join(er.args)) }")
                return redirect("/404")

        # if the user is not logged in, redirect to '/login' 
        if "uid" not in session:
            return redirect('/login')
        
        # else, render the template
    return render_template("blog/index.html", form = add_post_form , posts = posts)




@blog_bp.route('/myposts')
@login_required
def myposts():
    
    # get the DB connection
    db = get_db()

    # retrieve all posts
    posts = db.execute(f'''select * from post WHERE author_id = {session['uid']}''').fetchall()
    
    # render 'blog' blueprint with posts
    return render_template('blog/myposts.html', posts = posts)


@blog_bp.route('/post/<int:post_id>')
def view_post(post_id):
    pass



@blog_bp.route('/post/add', methods = ['GET', 'POST'])
@login_required
def add_post():


    post_form = PostForm()

    if post_form.validate_on_submit():
        # read post values from the form
        title = post_form.title.data
        body = post_form.body.data 

        # read the 'uid' from the session for the current logged in user
        author_id = session['uid']

        # get the DB connection
        db = get_db()
        
        # insert post into database
        try:
            # execute the SQL insert statement
            db.execute("INSERT INTO post (author_id, title, body) VALUES (?, ?,?);", (author_id, title, body))
            
            # commit changes to the database
            db.commit()
            flash('You were successfully Add')
            return redirect('/posts') 

        except sqlite3.Error as er:
            print(f"SQLite error: { (' '.join(er.args)) }")
            return redirect("/404")

    # if the user is not logged in, redirect to '/login' 
    if "uid" not in session:
        return redirect('/login')
    
    # else, render the template
    return render_template("blog/add-post.html", form = post_form)



@blog_bp.route('/post/<int:post_id>/delete', methods = ['GET', 'POST'])
@login_required
def delete_post(post_id):

    # get the DB connection
    db = get_db()

    db.execute(f"DELETE FROM post WHERE id = {post_id} ")
    db.commit()

    return redirect(url_for("blog.myposts"))



@blog_bp.route('/post/<int:post_id>/edit', methods = ['GET', 'POST'])
@login_required
def edit_post(post_id):

    edit_post_form = EditPostForm() 

    if request.method == "GET":

        db = get_db()

        current_post = db.execute(f"select * from post WHERE id = {post_id}").fetchone()

        edit_post_form.new_title.data = current_post['title']
        edit_post_form.new_body.data = current_post['body']

    
    if edit_post_form.validate_on_submit():
        # read post values from the form
        new_title = edit_post_form.new_title.data
        new_body = edit_post_form.new_body.data 


        # get the DB connection
        db = get_db()
        
        
        try:
            
            db.execute(f"UPDATE post SET title = '{new_title}', body = '{new_body}' WHERE id = '{post_id}' ")    
            
            # commit changes to the database
            db.commit()
            
            return redirect(url_for("blog.myposts")) 

        except sqlite3.Error as er:
            print(f"SQLite error: { (' '.join(er.args)) }")
            return redirect("/404")

    # if the user is not logged in, redirect to '/login' 
    if "uid" not in session:
        return redirect('/login')
    
    # else, render the template
    return render_template("blog/edit_post.html", form = edit_post_form)



@blog_bp.route('/post/<int:post_id>/add_reply', methods = ['GET', 'POST'])
@login_required
def reply_post(post_id):
    db = get_db()
    reply_form = ReplyPostForm()

    if reply_form.validate_on_submit():

        # read post values from the form
        body = reply_form.body.data 
        author_id = session['uid']

        
        try:
            # execute the SQL insert statement
            db.execute("INSERT INTO reply (post_id,author_id,body) VALUES (?,?,?);", (post_id,author_id,body,))
            
            # commit changes to the database
            db.commit()
            return redirect(url_for('blog.reply_post', post_id = post_id))

        except sqlite3.Error as er:
            print(f"SQLite error: { (' '.join(er.args)) }")
            return redirect("/404")

        
    # Display the reply section
    
    # retrieve post
    mypost = db.execute(f"select * from post WHERE id = {post_id}").fetchone()
    
    # retrieve first and last name from author post
    author_id = mypost['author_id']
    post_author = db.execute(f'''select * from user WHERE id = {author_id}''').fetchone()
    

    #retrieve replies 
    replies = db.execute(f'''select * from reply WHERE post_id = {post_id}''').fetchall()

    
    users = db.execute("select * from user").fetchall()



    #render the template
    return render_template("blog/reply_post.html", mypost = mypost, post_author = post_author, form = reply_form, replies = replies, users = users)



@blog_bp.route('/post/<int:post_id>/delete_reply/<int:reply_id>', methods = ['GET', 'POST'])
@login_required
def delete_reply(post_id,reply_id):

    # get the DB connection
    db = get_db()
        
    # delete from DB
    db.execute(f"DELETE FROM reply WHERE id = {reply_id} ")
    db.commit()


    return redirect(url_for('blog.reply_post', post_id = post_id))



@blog_bp.route('/post/<int:post_id>/edit_reply/<int:reply_id>', methods = ['GET', 'POST'])
@login_required
def edit_reply(post_id,reply_id):

    edit_reply_form = EditReplyForm() 

    if request.method == "GET":

        db = get_db()

        current_reply = db.execute(f"select * from reply WHERE id = {reply_id}").fetchone()

        edit_reply_form.new_body.data = current_reply['body']

    
    if edit_reply_form.validate_on_submit():
        # read post values from the form
        new_body = edit_reply_form.new_body.data 


        # get the DB connection
        db = get_db()
        
        
        try:
            
            db.execute(f"UPDATE reply SET body = '{new_body}' WHERE id = '{reply_id}' ")    
            
            # commit changes to the database
            db.commit()
            
            return redirect(url_for("blog.reply_post" , post_id = post_id)) 

        except sqlite3.Error as er:
            print(f"SQLite error: { (' '.join(er.args)) }")
            return redirect("/404")

    # if the user is not logged in, redirect to '/login' 
    if "uid" not in session:
        return redirect('/login')
    
    # else, render the template
    return render_template("blog/edit_reply.html", form = edit_reply_form)