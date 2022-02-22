from urllib.request import urlopen
from html.parser import HTMLParser
import time
import os

import click
from flask import Flask

from dotenv import load_dotenv
from flaskr import create_app, db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


def getWebsiteData():
    link = "https://www.fleaflicker.com/nfl/pbp?gameId=6567"
    pageAsString = urlopen(link).read().decode('utf-8')
    parser = MyHTMLParser()
    parser.clear()
    parser.feed(pageAsString)
    rowNumber = parser.rowCounter
    print(rowNumber)
    parser.clear()
    parser.rowTarget = 119
    parser.secondPass = True
    print(parser.rowTarget)
    parser.feed(pageAsString)
    print(str(parser.teamAbbr))
    print(str(parser.quarter))
    print(str(parser.clock))
    print(str(parser.down))
    print(str(parser.yards))
    print(str(parser.ballOn))
    print(str(parser.playText))
    print(str(parser.score))
    print(str(parser.score).index('-'))
    print(str(parser.score)[:str(parser.score).index('-')])
    print(str(parser.score)[str(parser.score).index('-')+1:])
    print(str(parser.isScore))
    print(str(parser.scoreText))
    print(str(parser.isTackle))
    print(str(parser.tackleText))


class MyHTMLParser(HTMLParser):
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

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.inRow = True
            self.rowCounter += 1
            if self.secondPass and self.rowCounter == self.rowTarget:
                self.inTargetRow = True

        if self.inTargetRow:
            if tag == 'td':
                self.cellCounter += 1
            if tag == 'span' and attrs.count(('class', 'strong')) > 0:
                self.isScore = True
                self.lookForScore = True
            if tag == 'em' and self.cellCounter == 7:
                self.isTackle = True
                self.lookForTackler = True

    def handle_endtag(self, tag):
        if tag == 'tr':
            self.inRow = False
            self.inTargetRow = False

        if self.lookForTackler and tag == 'em':
            self.lookForTackler = False

    def handle_data(self, data):
        if self.inTargetRow:
            if self.cellCounter == 1:
                self.teamAbbr = data
            elif self.cellCounter == 2:
                self.quarter = data
            elif self.cellCounter == 3:
                self.clock = data
            elif self.cellCounter == 4:
                self.down = data
            elif self.cellCounter == 5:
                self.yards = data
            elif self.cellCounter == 6:
                self.ballOn = data
            elif self.cellCounter == 7:
                if self.lookForScore:
                    self.scoreText = data
                    self.lookForScore = False
                if self.lookForTackler:
                    if data != ', ':
                        self.tackleText.append(data)
                    self.playText = self.playText.strip()
                else:
                    self.playText += data

            elif self.cellCounter == 8:
                self.score += data


"""
setInterval(function(){
    $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
        $.getJSON($SCRIPT_ROOT + '/_run_scraper', 
        {
            row: rowHolder
        }, 
        function(data) {
            $('div#tester-3').text(data);
            rowHolder = data;
        });
        $.getJSON($SCRIPT_ROOT + '/_add_play',
            updateData(data)
        );
}, 5000);
*/
"""