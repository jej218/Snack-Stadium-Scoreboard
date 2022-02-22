from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .db import get_db
from flask_sock import Sock

bp = Blueprint('display', __name__)


@bp.route('/team')
def team():
    db = get_db()
    teams = db.execute(
        'SELECT * FROM team'
    ).fetchall()
    return render_template('display/team.html', teams=teams)


@bp.route('/play')
def play():
    db = get_db()
    plays = db.execute(
        'SELECT * FROM play ORDER BY id DESC'
    ).fetchall()
    teams = db.execute(
        'SELECT team.abbreviation FROM team JOIN play ON team.abbreviation = play.team_abbr'
    )
    return render_template('display/play.html', plays=plays, teams=teams)


@bp.route('/scoreboard')
def scoreboard():
    db = get_db()
    teams = db.execute(
        'SELECT * FROM team'
    ).fetchall()
    play = db.execute(
        'SELECT * FROM play ORDER BY created DESC',
    ).fetchone()
    return render_template('display/scoreboard.html', teams=teams, play=play)


@ bp.route('/create_team', methods=('GET', 'POST'))
def create_team():
    if request.method == 'POST':
        nickname = request.form['nickname']
        abbreviation = request.form['abbreviation']
        error = None

        if not nickname:
            error = 'Nickname is required'

        if not abbreviation:
            error = 'Abbreviation is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO team (nickname, abbreviation)'
                ' VALUES (?, ?)',
                (nickname, abbreviation)
            )
            db.commit()
            return redirect(url_for('display.team'))

    return render_template('display/create_team.html')


@ bp.route('/create_play', methods=('GET', 'POST'))
def create_play():
    if request.method == 'POST':
        team_abbr = request.form['team_abbr']
        quarter = request.form['quarter']
        gameClock = request.form['gameClock']
        down = request.form['down']
        distance = request.form['distance']
        yardLine = request.form['yardLine']
        descript = request.form['descript']
        tackler = request.form['tackler']
        scoreType = request.form['scoreType']
        scoreHome = request.form['scoreHome']
        scoreAway = request.form['scoreAway']
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO play (team_abbr, quarter, gameClock, down, distance, yardLine, descript, tackler, scoreType, scoreHome, scoreAway)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (team_abbr, quarter, gameClock, down, distance, yardLine,
                 descript, tackler, scoreType, scoreHome, scoreAway)
            )
            db.commit()
            return redirect(url_for('display.play'))

    return render_template('display/create_play.html')


def get_team(id):
    team = get_db().execute(
        'SELECT * FROM team t WHERE t.id = ?',
        (id,)
    ).fetchone()
    if team is None:
        abort(404, f"team id {id} doesn't exist.")
    return team


def get_newest_play():
    db = get_db()
    play = db.execute(
        'SELECT * FROM play ORDER BY created DESC',
    ).fetchone()
    return play


def get_teams():
    db = get_db()
    teams = db.execute(
        'SELECT * FROM team'
    ).fetchall()
    return teams


def get_play(id):
    play = get_db().execute(
        'SELECT * FROM play p WHERE p.id = ?',
        (id,)
    ).fetchone()
    if play is None:
        abort(404, f"play id {id} doesn't exist.")
    return play


@ bp.route('/<int:id>/update_team', methods=('GET', 'POST'))
def update_team(id):
    team = get_team(id)

    if request.method == 'POST':
        nickname = request.form['nickname']
        abbreviation = request.form['abbreviation']
        error = None

        if not nickname:
            error = 'Nickname is required'

        if not abbreviation:
            error = 'Abbreviation is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE team SET nickname = ?, abbreviation = ?'
                ' WHERE id = ?',
                (nickname, abbreviation, id)
            )
            db.commit()
            return redirect(url_for('display.team'))

    return render_template('display/update_team.html', team=team)


@ bp.route('/<int:id>/update_play', methods=('GET', 'POST'))
def update_play(id):
    play = get_play(id)

    return render_template('display/update_play.html', play=play)


@ bp.route('/<int:id>/delete_team', methods=('POST',))
def delete_team(id):
    get_team(id)
    db = get_db()
    db.execute('DELETE FROM team WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('display.team'))


@ bp.route('/<int:id>/delete_play', methods=('POST',))
def delete_play(id):
    get_play(id)
    db = get_db()
    db.execute('DELETE FROM play WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('display.play'))


def auto_create_play(teamAbbr, quarter, clock, down, yards, ballOn, playText, score, scoreText, tackleText):
    tacklers = ""
    for tackler in tackleText:
        tacklers += tackler
        if tackleText.index(tackler) < len(tackleText) - 1:
            tacklers += ', '
    scoreHome = str(score)[:str(score).index('-')]
    scoreAway = str(score)[str(score).index('-')+1:]
    db = get_db()
    db.execute(
        'INSERT INTO play (team_abbr, quarter, gameClock, down, distance, yardLine, descript, tackler, scoreType, scoreHome, scoreAway)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (teamAbbr, quarter, clock, down, yards, ballOn,
         playText, tacklers, scoreText, scoreHome, scoreAway)
    )
    db.commit()
