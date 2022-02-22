DROP TABLE IF EXISTS team;
DROP TABLE IF EXISTS play;

CREATE TABLE team (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    /* Sets the nickname and abbreviation values for automation from a one letter value */
    nickname TEXT,
    abbreviation TEXT
);

CREATE TABLE play (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    /* represents WON a play had a score - used for formating descript and also any potential scoreboard animations
    determined by presence of bold text in source description */
    team_abbr TEXT,
    /* The current quarter of the game, used in the scoreboard part of the page
    determined by the 2nd cell in the source row as text with st/nd/rd/th*/
    quarter TEXT,
    /* The time of the snap of the play as text. determined from the 3rd cell in the source row and displayed on the scoreboard*/
    gameClock TEXT,
    /* The down of the play. May be null on XP or 2P conversions. 4th cell in source row and displayed on the scoreboard */
    down TEXT,
    /* The distance remaining for a 1st down. May also be 'Goal', or null on XP or 2P. 5th cell and displayed on the scoreboard*/
    distance TEXT,
    /* position of the ball on the field as text - 6th */
    yardLine TEXT,
    /* The description of the play which is dispalyed and used to determine other values  - 7th
    note that the description will be modified upon play creation to better display the tackler name or a score message */
    descript TEXT,
    /* the name of the person who tackled on this play, if hasTackler. Located at the end of descript */
    tackler TEXT DEFAULT '',
    /* the name of the type of score on this play, if isScore. Located at the end of descript */
    scoreType TEXT DEFAULT '',
    /* The home teams score which is taken from the second value in the 8th cell and displayed on the scoreboard */
    scoreHome INTEGER,
    /* The away teams score which is taken from the first value in the 8th cell and displayed on the scoreboard */
    scoreAway INTEGER,
    /* timestamp for sorting purposes */
    isScore BOOLEAN GENERATED ALWAYS AS (scoretype IS NOT '') STORED,
    /* represents WON a play had a tacker - used for formatting descript
    determined by presence of italic text at the end of source description
    there can be scores with tackles also. */
    hasTackle BOOLEAN GENERATED ALWAYS AS (tackler IS NOT '') STORED,
    /* The abbreviation of the team of the play for the purposes of coloring the element background
    determined from the first cell of the source's row. Note that this is the team that ends with possesion after turnovers */
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    /* WON the game is over. Checks a value in the sources box score */
    gameOver BOOLEAN DEFAULT FALSE,
    /* refernce to  the team it represents. */
    FOREIGN KEY (team_abbr) REFERENCES team (abbreviation)
);



INSERT INTO team (nickname, abbreviation)
VALUES ('Rams', 'LAR');
INSERT INTO team (nickname, abbreviation)
VALUES ('Bengals', 'CIN');