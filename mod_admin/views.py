from flask import render_template ,  redirect ,  request , flash , url_for
from flask_login import login_user , logout_user , login_required , current_user
from sqlalchemy.exc import IntegrityError
from mod_admin import admin
from mod_blog.models import Post
from mod_blog.forms import PostForm
from app import db 

@admin.route('/')
def index():
    return render_template('admin/index.html' , title='Dashboard')


#### Post ####

# Show List Post
@admin.route('posts/')
def post_show():
    page = request.args.get('p' , default=1 , type=int)
    per_page = request.args.get('n' , default=10 , type=int)
    posts = Post.query.paginate(page=page , per_page=per_page , error_out=False)
    return f'{posts.items}'
    # return render_template('admin/posts/post.html' , title='Show Posts' , posts=posts)

# Create Post
@admin.route('posts/create/' , methods=['GET' , 'POST'])
def post_create():
    form = PostForm()

    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('admin/posts/post-form.html' , title=f'Create New Post' , form=form)
        
        NewPost = Post(
            title=form.title.data,
            content=form.content.data,
            summary=form.summary.data,
            slug=form.slug.data,
            image=1 # -> temporarily until the completion of the blueprint (media)
        )
        
        NewPost.author = current_user

        try :
            db.session.add(NewPost)
            db.session.commit()
            flash('Post successfully created')
        except IntegrityError :
            db.session.rollback()
            flash('Post could not be created successfully')

    return render_template('admin/posts/post-form.html' , title=f'Create New Post' , form=form)


# Edite Post
@admin.route('posts/edite/<int:post_id>' , methods=['GET' , 'POST'])
def post_edite(post_id):
    form = PostForm()
    post = Post.query.get_or_404(int(post_id))
    
    if request.method == 'GET' :
        form.title.data = post.title
        form.content.data = post.content
        form.slug.data = post.slug
        form.summary.data = post.summary
        
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('admin/posts/post-form.html' , title=f'Edite {post.title}' , form=form)
        
        post.title = form.title.data
        post.content = form.content.data
        post.slug = form.slug.data
        post.summary = form.summary.data

        try :
            db.session.commit()
            flash('Post successfully update')
        except IntegrityError :
            db.session.rollback()
            flash('Post could not be update successfully')

    return render_template('admin/posts/post-form.html' , title=f'Edite {post.title}' , form=form)



# Delete Post
@admin.route('posts/delete/<int:post_id>')
def post_delete(post_id):
    post = Post.query.get_or_404(int(post_id))
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('admin.post_show'))
