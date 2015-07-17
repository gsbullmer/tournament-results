#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import bleach
import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("TRUNCATE matches RESTART IDENTITY CASCADE")
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("TRUNCATE players RESTART IDENTITY CASCADE")
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM players")
    player_count = c.fetchall()[0][0]
    db.close()
    return player_count


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    c = db.cursor()
    query = "INSERT INTO players (name) VALUES (%s)"
    c.execute(query, (bleach.clean(name),))
    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()
    query = '''
        SELECT player_id, name, COUNT(CASE WHEN player_id = winner THEN 1 END) AS wins, COUNT(winner + loser) AS matches
        FROM players LEFT JOIN matches
        ON player_id = winner OR player_id = loser
        GROUP BY player_id;
        '''
    c.execute(query)
    standings = [(str(row[0]), str(row[1]), int(row[2]), int(row[3]))
                 for row in c.fetchall()]
    db.close()
    print standings
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect()
    c = db.cursor()
    query = "INSERT INTO matches (winner, loser) VALUES (%s, %s)"
    c.execute(query, (winner, loser))
    db.commit()
    db.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    db = connect()
    c = db.cursor()
    query = "SELECT * FROM players"
    c.execute(query)
    pairings = [{'id1': str(row[0]), 'name1': str(row[1]), 'id2': str(row[2]), 'name2': str(row[3])}
                for row in c.fetchall()]
    db.close()
    return pairings

