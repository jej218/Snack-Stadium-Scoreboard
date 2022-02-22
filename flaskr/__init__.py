from . import display
import os

from flask import Flask
from flask import render_template, jsonify, request
# import click
from urllib.request import urlopen
from html.parser import HTMLParser
#from flask.cli import with_appcontext

import time

rowNumberStart = 0  # TODO: This should be 0 on deployment, or 6 for testing
rowNumberHolder = 0


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello

    from . import db
    db.init_app(app)

    from . import display
    app.register_blueprint(display.bp)

    # This is the default home route
    @app.route('/')
    def landingPage():
        # at the end of the landing page function, we call the display BP's scoreboard method, which loads the scoreboard page
        return display.scoreboard()

    @app.route('/_send_data')
    def send_data():
        global rowNumberHolder
        global rowNumberStart
        # Calls getWebsiteData, with rowNumberStart. RNS is the representation of the target row number of the previous getWebsiteData call
        # It is stored in a global variable. RNH is a variable to hold the output of getWebsite Data. The conditional cases after the function call
        # explain the different cases for this value
        rowNumberHolder = getWebsiteData(rowNumberStart)
        # we can set a 5 second delay here, in order to make sure the scraper has enough time to fully execute
        # TODO: it may be the case that the previous line of code always executes fully before subsequent lines, due to passing a value to RNH
        # time.sleep(5)
        # if RNH is -1, getWebsiteData didn't create a new play because there is no new play. We then return false to tell
        # the Jquery that it doesn't need to render a new play. This also avoids all the code below that checks the db and
        # handles formatting
        if rowNumberHolder == -1:
            return jsonify(False)
        elif rowNumberHolder <= -2:
            rowNumberStart += 1
            return jsonify(False)
        elif rowNumberHolder < 7:
            return jsonify(scoreHome='0', scoreAway='0', down='1st', distance='10', quarter='1st', gameClock='15:00',
                           yardLine='50', descript='Kickoff at 3:30 PST', isScore=False, scoreType='', hasTackle=False, tackler='',
                           playTeamAbbr='CIN', awayTeamAbbr='LAR', homeTeamAbbr='CIN', awayTeamName='Rams', homeTeamName='Bengals')
        # in any other case we continue the function. First set RNS to the value of RNH, which is assigned to the row Target if it is new
        # this sets up RNS to be used in the next call of this function
        rowNumberStart = rowNumberHolder
        # getter methods for the newest play and the teams via the display blueprint
        play = display.get_newest_play()
        teams = display.get_teams()
        # specifies the home and away abbreviations and nicknames
        for team in teams:
            homeTeam = teams[0]
            awayTeam = teams[1]
            if team['abbreviation'] == 'CIN':
                homeTeam = team
            elif team['abbreviation'] == 'LAR':
                awayTeam = team
            awayTeamAbbr = awayTeam['abbreviation']
            homeTeamAbbr = homeTeam['abbreviation']
            awayTeamName = awayTeam['nickname']
            homeTeamName = homeTeam['nickname']
        print('Inside send_data ' + play['gameClock'])  # FIXME: Reference
        # sends all the proper data to the jquery
        return jsonify(scoreHome=str(play['scoreHome']), scoreAway=str(play['scoreAway']),
                       down=play['down'], distance=play['distance'], quarter=play['quarter'], gameClock=play['gameClock'],
                       yardLine=play['yardLine'], descript=play['descript'], isScore=play['isScore'], scoreType=play['scoreType'],
                       hasTackle=play['hasTackle'], tackler=play['tackler'], playTeamAbbr=play['team_abbr'], awayTeamAbbr=awayTeamAbbr,
                       homeTeamAbbr=homeTeamAbbr, awayTeamName=awayTeamName, homeTeamName=homeTeamName)

    return app

# this is the 'main' method for scraping the page of information
# it runs the feed function twice - once to determine the row number, and a second time using that row number as the target row for data
# it also takes an argument 'previousRowNumber' and returns 'newRowNumber'. These are compared to determine if a new play needs to be added to the database.
# if the numbers are different, then the method calls on a method in the display blueprint that creates a new database entry for the play


def getWebsiteData(previousRowNumber):
    # Link to game to scrape TODO:
    link = "https://www.fleaflicker.com/nfl/pbp?gameId=6715&tableSortName=2&tableSortDirection=ASC"
    pageAsString = urlopen(link).read().decode(
        'utf-8')  # Formatting the page as a string
    parser = MyHTMLParser()  # creating the parser object
    parser.clear()  # Calling the function to clear the parsers data from previous scrape
    parser.feed(pageAsString)  # feeding the parser the page for the first time
    rowNumber = parser.rowCounter  # storing the number of rows to determine targeted row
    parser.clear()  # clearing all information from the parser object
    # setting the now cleared parser object's target row to be the last row
    # TODO: This is set to previousRowNumber + 1 for development so it progresses through rows sequentially each call
    # TODO: set the second side of the expression to rowNumber to fix
    parser.rowTarget = rowNumber
    # telling the parser we are on the second pass - this grabs output data

    # creates new play if the targeted row is new
    if previousRowNumber != parser.rowTarget and parser.rowTarget >= 7:
        parser.secondPass = True
        print(parser.rowTarget)  # FIXME: reference
        parser.feed(pageAsString)  # feeding the parser the page again
        if parser.isBadRow:
            print('Got to a Bad Row')
            return -2
        if parser.isInvalidRow:
            print('Got to an Invalid Row')
            return -3
        print('Created a play in getWebsiteData')  # FIXME: reference
        print(str(parser.teamAbbr) + ', ' + str(parser.quarter) +
              ', ' + str(parser.clock) + ', ' + str(parser.down) + ', ' + str(parser.yards) + ', ' + str(parser.ballOn) + ', ' + str(parser.score))
        print(str(parser.playText) + ', ' +
              str(parser.tackleText) + ', ' + str(parser.scoreText))
        display.auto_create_play(parser.teamAbbr, parser.quarter, parser.clock, parser.down, parser.yards,
                                 parser.ballOn, parser.playText, parser.score, parser.scoreText, parser.tackleText)
        return parser.rowTarget
    elif parser.rowTarget < 7:
        print('Row Number is too low')
        return parser.rowTarget
    else:
        print('Row Number is not new')
        return -1


class MyHTMLParser(HTMLParser):  # parser class
    inRow = False
    rowCounter = 0
    secondPass = False
    rowTarget = 0
    inTargetRow = False
    cellCounter = 0
    teamAbbr = ""
    quarter = ""
    clock = ""
    down = ""
    yards = ""
    ballOn = ""
    playText = ""
    score = ""
    isScore = False
    scoreText = ""
    lookForScore = False
    isTackle = False
    lookForTackler = False
    tackleText = []
    isBadRow = False
    isInvalidRow = False

    # method that clears all the data back to original values
    def clear(self):
        self.inRow = False
        self.rowCounter = 0
        self.secondPass = False
        self.rowTarget = 0
        self.inTargetRow = False
        self.cellCounter = 0
        self.teamAbbr = ""
        self.quarter = ""
        self.clock = ""
        self.down = ""
        self.yards = ""
        self.ballOn = ""
        self.playText = ""
        self.score = ""
        self.isScore = False
        self.scoreText = ""
        self.lookForScore = False
        self.isTackle = False
        self.lookForTackler = False
        self.tackleText = []
        self.tacklerCounter = 0
        self.isBadRow = False
        self.isInvalidRow = False

    # handles start tags
    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            # if the tag is in a row, it tells the obect that it is currently looking within a row, and increases the row counter by 1
            # the row counter is used on the first pass through to determine the number of rows in the table
            # on the second pass through, the resulting number is used as the reference to the last row (which is always the target)
            self.inRow = True
            self.rowCounter += 1
            # if the parser is passing throught the page on the second time, and it has reached its target row, it tells the object it is now within its target
            if self.secondPass and self.rowCounter == self.rowTarget:
                self.inTargetRow = True

        # if the tag is within the targeted row
        if self.inTargetRow:
            # if it is a table cell, increase the cell counter by 1
            # the cell counter is used to determine what data is inside the cell
            if tag == 'td':
                self.cellCounter += 1
                if attrs.count(('class', 'vertical-spacer')) > 0:
                    self.isBadRow = True
                if attrs.count(('class', 'vertical-spacer table-heading')) > 0:
                    self.isInvalidRow = True
            # if the tag is a span and it is bolded, this represents a scoring play
            # it also sets lookForScore to be true, to help the handle_data function to grab the score text
            if tag == 'span' and attrs.count(('class', 'strong')) > 0:
                self.isScore = True
                self.lookForScore = True
            # if the tag is 'em' and we are in the description cell (em means italics)
            # this looks for the text that represents the player/s that made tackles on the play
            # sets the isTackle to be true, and also the lookForTackler to help the handle_data function to grab the tackler text
            if tag == 'em' and self.cellCounter == 7:
                self.isTackle = True
                self.lookForTackler = True

    def handle_endtag(self, tag):
        # at the end of a row, sets all 'in Row' booleans as false
        if tag == 'tr':
            self.inRow = False
            self.inTargetRow = False

        # if we are at the end of an 'em' tag (a tackler name tag), set lookForTackler to be false
        # so that the handle_data doesn't keep looking for a tackler's name
        if self.lookForTackler and tag == 'em':
            self.lookForTackler = False

    def handle_data(self, data):
        # data is only grabbed from a row if we are in the target row
        if self.inTargetRow:
            # Team's abbreviated name
            if self.cellCounter == 1:
                self.teamAbbr = data
            # Text representing the quarter (works for OT too)
            elif self.cellCounter == 2:
                self.quarter = data
            # The time on the clock
            elif self.cellCounter == 3:
                self.clock = data
            # The down of the play
            elif self.cellCounter == 4:
                self.down = data
            # The yards left for 1st down
            elif self.cellCounter == 5:
                self.yards = data
            # The location of the ball
            elif self.cellCounter == 6:
                self.ballOn = data
            # The play description
            elif self.cellCounter == 7:
                # lookForScore is true if handle_starttag saw a bolded span (a score text)
                # this conditional resets the scoreText to be the text in the newest bolded span, as some plays have multiple, separated bolded spans
                # the last bolded span always has the appropriate scoreText.
                # The lookForScore is set back to false, requiring handle_starttag to find another bolded span to re-enter this conditional
                if self.lookForScore:
                    self.scoreText = data
                    self.lookForScore = False
                # lookForTackler is true if handle_starttag saw italicized data (a tackler name)
                if self.lookForTackler:
                    # This adds each taclker to a list, which can be formatted into a string in the auto_play_create function
                    # In the case of multiple tacklers, there will be a ', ' within the italicized data
                    # this is not added to the list of tacklers.
                    if data != ', ':
                        self.tackleText.append(data)
                    # if the play has a tackler, the tackler text is only added to the list, not the playText string.
                    # this leaves a waiting space before/after tacklers, which is stripped here
                    self.playText = self.playText.strip()
                # the new section play text is added in all cases except when the function is looking for tackler text
                else:
                    self.playText += data
            # The score in the format 'HOME-AWAY'. This is reformatted in the function that creates the play.
            elif self.cellCounter == 8:
                self.score += data
