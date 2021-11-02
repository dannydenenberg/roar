from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

import random

from auth import login_required
from db import get_db

bp = Blueprint("roar", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        """
        select 
            p.id, 
            roar, 
            p.created, 
            author_id, 
            (select count(*) from applaud a WHERE a.post_id = p.id) applauds,
            username
        from post p join user u on p.author_id = u.id
        order by p.created desc;
        """
    ).fetchall()

    applauds = [] # dic with {post_number: True/False} whether the post has been liked by the person.
    if g.user is not None: # if the person is signed in.
        applauds_list = db.execute(
                        "SELECT post_id FROM applaud WHERE user_id = ?",
                        (g.user["id"],),
                    ).fetchall()
        [applauds.append(a["post_id"]) for a in applauds_list] # make a list of only the ID numbers.


    return render_template("roar/index.html", posts=posts, applauds=applauds)


def get_post(id, check_author=True):
    """Get a post and its author by id.
    Checks that the id exists and optionally that the current user is
    the author.
    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, roar, p.created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        roar = request.form["roar"]
        error = None

        if not roar:
            error = "Put some VOLUME in your ROAR."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (roar, author_id) VALUES (?, ?)",
                (roar, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("roar.index"))

    return render_template("roar/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        roar = request.form["roar"]
        error = None

        if not roar:
            error = "Put some SOUND in your ROAR."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET roar = ? WHERE id = ?", (roar, id)
            )
            db.commit()
            return redirect(url_for("roar.index"))

    return render_template("roar/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.
    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("roar.index"))

@bp.route("/applaud", methods=("GET",))
@login_required
def applaud():
    post_id = request.args.get('post_id', 0, type=int)
    user_id = g.user["id"]

    previous_applauds = get_db().execute(
                "SELECT * FROM applaud WHERE post_id = ? AND user_id = ?",
                (post_id, user_id),
            ).fetchall()
    

    db = get_db()
    if len(previous_applauds) == 0:
        # not previously liked.
        # add the person to the posts likers
        db.execute(
            "INSERT INTO applaud (user_id, post_id) VALUES (?, ?)",
            (user_id, post_id),
        )
        db.commit()
    else:
        # UNlike this post for the person
        # delete this person from the post's likes
        db.execute("DELETE FROM applaud WHERE user_id = ? AND post_id = ?", (user_id, post_id))
        db.commit()
    

    return {}

@bp.route("/~<string:username>/applauds", methods=("GET", "POST"))
def show_account_applauds(username):
    """Show all the tweets from a username."""
    db = get_db()
    posts = db.execute(
        """
        select 
            p.id, 
            roar,
            p.created, 
            author_id, 
            (select count(*) from applaud a WHERE a.post_id = p.id) applauds,
            username
        from 
            applaud a 
        join post p on p.id = a.post_id 
        join user u on u.id = a.user_id 
        where username = ?;
        """,
    (username,)).fetchall()

    if len(posts) == 0:
        print('no liked posts')
        # return abort(404)

    applauds = [] # dic with {post_number: True/False} whether the post has been liked by the person.
    if g.user is not None: # if the person is signed in.
        applauds_list = db.execute(
                        "SELECT post_id FROM applaud WHERE user_id = ?",
                        (g.user["id"],),
                    ).fetchall()
        [applauds.append(a["post_id"]) for a in applauds_list] # make a list of only the ID numbers.


    return render_template("roar/show_account/base.html", applauds=applauds, username=username, posts=posts)


@bp.route("/~<string:username>", methods=("GET", "POST"))
def show_account(username):
    """Show all the tweets from a username."""
    db = get_db()
    posts = db.execute(
        """
        select 
            p.id, 
            roar, 
            p.created, 
            author_id, 
            (select count(*) from applaud a WHERE a.post_id = p.id) applauds,
            username
        from post p join user u on p.author_id = u.id
        where username = ?
        order by p.created desc;
        """,
    (username,)).fetchall()

    if posts is None:
        return abort(404)

    return render_template("roar/show_account/base.html", username=username, posts=posts)


@bp.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return "<h1>404</h1><p>Chap, you made a mistake typing that URL. Here's a link <a href='/'>home</a>.</p>", 404