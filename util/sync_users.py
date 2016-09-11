import psycopg2

"""
Synchronizes two databases by INSERTing rows missing in destination database from source database.
It assumes both databases have the same structure of tables.
"""

import importlib.machinery

source_config = importlib.machinery.SourceFileLoader('config', '../exeris/config/default_config.py').load_module()
destination_config = importlib.machinery.SourceFileLoader('config', '../exeris/config/default_config.py').load_module()

conn_source = psycopg2.connect(source_config.SQLALCHEMY_DATABASE_URI)
conn_destination = psycopg2.connect(destination_config.SQLALCHEMY_DATABASE_URI)

cur_source = conn_source.cursor()
cur_destination = conn_destination.cursor()


def get_player_ids(cursor):
    cursor.execute("SELECT id FROM players")
    return [row[0] for row in cursor.fetchall()]


players_on_destination = get_player_ids(cur_destination)
players_on_source = get_player_ids(cur_source)

missing_players_ids = [player for player in players_on_source if player not in players_on_destination]

cur_source.execute("SELECT * FROM players WHERE id IN %s", (tuple(missing_players_ids),))
players_to_add = cur_source.fetchall()

for player_tuple in players_to_add:
    cur_destination.execute("INSERT INTO players VALUES %s", (player_tuple,))
cur_destination.commit()

print("Players:", missing_players_ids, "have been copied from source to destination")