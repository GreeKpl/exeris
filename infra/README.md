# How to run in prod mode

Copy file `.env.default` to `.env` and update the values.
Copy file `game_config.py.default` to `game_config.py` and update the values.

Then enter this directory (`infra/`) and run `docker-compose up`.

The application (frontend) will be available at port `8089`.

Regardless of this being a 'production' setup, it shouldn't be exposed to the outside world. 

Production version shouldn't have DEBUG option set to True, so the application will start without any player account.
Usually it's not a good idea to change database directly, but currently it's the easiest way.

Login to psql (assuming the db user is called `postgres` and database is `exeris1`):

```
docker exec -ti infra_postgres_1 bash
psql -U postgres

\c exeris1
```

You are logged in as a user with admin role to the game's database. Now run the following query:

> INSERT INTO players (id, email, language, register_date, register_game_date, password, active, confirmed_at, serial_id)
>   VALUES ('**alchrabas**', '**alchrabas@exeris.org**', 'en', NOW(), 1, '**test**', true, NOW(), nextval('player_serial_id'));

You can set the highlighted parameters (id, email, password) to anything you like. **Passwords are not hashed yet.** So it's not secure at all.

