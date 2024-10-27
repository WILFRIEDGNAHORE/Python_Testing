import datetime
import json
from flask import Flask, make_response
from flask import render_template, request, redirect, flash, url_for


def load_clubs():
    with open('clubs.json') as c:
        list_of_clubs = json.load(c)['clubs']
    return list_of_clubs


def load_competitions():
    with open('competitions.json') as comps:
        list_of_competitions = json.load(comps)['competitions']
    return list_of_competitions


def check_competition_is_over(list_of_competitions):
    competitions = []
    for competition in list_of_competitions:
        competition['over'] = False
        competition_date = datetime.datetime.strptime(
            competition["date"], "%Y-%m-%d %H:%M:%S"
        )
        competition['over'] = competition_date < datetime.datetime.now()
        competitions.append(competition)
    return competitions


app = Flask(__name__)
app.secret_key = 'something_special'

# Call the check_competition_is_over
#  function to update competitions with the 'over' flag
competitions = check_competition_is_over(load_competitions())
clubs = load_clubs()
MAX_PLACE_PAR_CLUB = 12
COST_PLACE = 3


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def show_summary():
    try:
        club = [club for club in clubs
                if club['email'] == request.form['email']][0]
        return render_template(
            'welcome.html', club=club, competitions=competitions)
    except IndexError:
        flash("Sorry, that email wasn't found.")
        response = make_response(render_template('index.html'))
        return response, 401


@app.route('/book/<competition>/<club>')
def book(competition, club):
    try:
        found_club = [c for c in clubs if c['name'] == club][0]
        found_competition = [c for c in competitions
                             if c['name'] == competition][0]
        if found_club and found_competition:
            if not found_competition['over']:
                return render_template(
                    'booking.html',
                    club=found_club,
                    competition=found_competition
                                                )

        flash("Something went wrong-please try again")
        response = make_response(render_template(
            'welcome.html', club=club, competitions=competitions))
        return response, 403
    except IndexError:
        flash("Something went wrong-please try again")
        response = make_response(render_template(
            'index.html', club=club, competitions=competitions))
        return response, 400


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    competition = [c for c in competitions
                   if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    if not competition['over']:
        places_required = int(request.form['places'])
        total_points_to_deduct = places_required * COST_PLACE
        if total_points_to_deduct <= int(club["points"]):
            if places_required <= MAX_PLACE_PAR_CLUB:
                competition['numberOfPlaces'] = str(
                    int(competition['numberOfPlaces']) - places_required
                )
                club["points"] = str(int
                                     (club["points"]) - total_points_to_deduct)
                flash('Great-booking complete!')
                return render_template(
                    'welcome.html', club=club, competitions=competitions)
            else:
                message = "You should book"
                " no more than 12 places per competition"
        else:
            message = 'Not enough points'
    else:
        message = "The competition is over, the booking is closed!"

    flash(message)
    response = make_response(render_template(
        'welcome.html', club=club, competitions=competitions))
    return response, 403


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
