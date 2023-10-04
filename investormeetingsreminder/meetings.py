from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from investormeetingsreminder.auth import login_required
from investormeetingsreminder.db import get_db

bp = Blueprint('meetings', __name__)

@bp.route('/')
def index():
    db = get_db()
    meetings = db.execute(
        'SELECT m.id, title, body, created, investor_id, username,hours_time'
        ' FROM meeting m JOIN user u ON m.investor_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('index.html', meetings=meetings)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        hours_time = request.form['hours_time']
        error = None

        if not title:
            error = 'Title is required.'

        if not hours_time:
            error = 'Time is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO meeting (title, body, investor_id,hours_time)'
                ' VALUES (?, ?, ?,?)',
                (title, body,hours_time, g.user['id'])
            )
            db.commit()
            return redirect(url_for('meetings.index'))

    return render_template('meetings/create.html')

def get_meetings(id, check_investor=True):
    meeting = get_db().execute(
        'SELECT m.id, title, body, created, investor_id, username,hours_time'
        ' FROM meeting m JOIN user u ON m.investor_id = u.id'
        ' WHERE m.id = ?',
        (id,)
    ).fetchone()

    if meeting is None:
        abort(404, f"Meeting id {id} doesn't exist.")

    if check_investor and meeting['investor_id'] != g.user['id']:
        abort(403)

    return meeting

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    meetings = get_meetings(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        hours_time = request.form['hours_time']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE meeting SET title = ?, body = ?, hours_time = ?'
                ' WHERE id = ?',
                (title, body, hours_time, id)
            )
            db.commit()
            return redirect(url_for('meetings.index'))

    return render_template('meetings/update.html', meetings=meetings)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_meetings(id)
    db = get_db()
    db.execute('DELETE FROM meeting WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('meetings.index'))