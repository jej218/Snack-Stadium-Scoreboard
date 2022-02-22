# Snack Stadium Scoreboard
This was a side project I worked on during my webdev bootcamp. The goal was to get a live 'scoreboard' self-updating throughout the game on a Raspberry Pi, mounted on a 'snack stadium' as its jumbotron. This is a Python web application using the [Flask Framework](https://flask.palletsprojects.com/en/2.0.x/), and uses [AJAX](https://developer.mozilla.org/en-US/docs/Web/Guide/AJAX) with JSON to send the data without reloading the page. I scraped [Fleaflicker](https://www.fleaflicker.com/nfl/pbp?gameId=6715) using [HTMLParser](https://docs.python.org/3/library/html.parser.html) to grab live score and play by play updates. I taught myself Flask and [Sass](https://sass-lang.com/) for this project.

## The Stadium in Action

## Current Phase and Future Updates
**This project is currently in pre-alpha and willnot be deployed until after my bootcamp. You _can_ run it in the development environment, in a python virtual environment with flask installed**(Although at this point all you would see is the last play and ending score of the game you choose)

For an alpha phase:
- Add styling, name, and logos for the other 32 teams
- Re-factor the AJAX to avoid connection end if the client goes to sleep or screensaver
- Add a landing page where the desired game's url is selected for viewing
- Deploy the application

There are also some loftier goals if I have time:
- Tweak responsive styling for different screen sizes and browsers
- Display all games available for selection on the landing page, by scraping the websites list for the current day
- Find a workaround for browser restrictions on autoplaying audio files (for ESPNs score alert jingle on game score)
- Re-factor scraping logic to
    - skip scraping when the page hasn't been updated
    - decrease process length
    - smoothly handle unsorted play data in the document
    - determine when the game is between quarters or at halftime
- Re-factor the AJAX to eliminate any need to refresh the page.