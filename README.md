What is Exeris?
===============
Exeris is an open-source, free, browser-based multiplayer mix of crafting and exploration game. 


Goals
-----
I like Python. My main goal is to learn it efficiently and I always prefer to learn by solving some
real challenging problems, not by reading books or doing simple excercises which have nothing to do with real-life.

The second reason is lack of satisfaction in any of currently existing games.

It has lead me to the idea that I'm the only person that can create the game I will fully enjoy.

That's why I'm not looking for anybody to help me in programming (or telling me what to do),
but suggestions, bug reports and proposals of bug fixes are welcome.

The game should be **able to be extremely challenging**, **self-managing**, not **time-restricted** (open-endness),
**slow paced** with **elastic time requirements** (good for busy people) and **full of surprises**.

Plans
-----

There is no goal to run pre-alpha version of the game as soon as possible.
Most of the backend code is validated by automatic tests, so there's no need to have a running game server.

There is no planned release date.


Technologies
------------
 - Python
 - Flask + Flask-Socketio (and other Flask extensions)
 - Postgres + PostGIS
 - SQLAlchemy ORM
 - Jinja2 tamplates
 - Pyslate i18n library


Game features
-------------
By playing a character in the virtual world consisting of two main continents you can cooperate
or compete with characters of other players to collect resources and use them to build or craft
more advanced tools, machines, buildings or ships.
There are two main continents, called **Old** and **New World**.

**The Old World** is a persistent group of islands where most of the new players start.
It's not very rich or large, but it's relatively safe to live there and easy to prepare basic tools.

The most wealthy and fertile area is **The New World** - a land ready to be explored and settled to get its riches.
But after finite amount of time all the new world would be mapped and fully developed, so where would open-endness be?
That's why **The New World** is not durable and, after certain period of time (about a year) **The New World** sinks in the ocean.
After a few days **The New New World** is generated and emerges from the ocean, ready to be explored and exploited.

Apart of that, almost every entity in the game needs to be built by players and it requires maintenance to work.
Tools or machines need to be repaired or they degrade until they turn into a pile of rubbish.
Food cannot be stored permanently, it starts to decay some time after it's produced.
When the environment created by players is abandoned, then it slowly comes back to its original state.
When character dies, then their death is permanent and they cannot be revived in any way.


Development
-----------
Development progress available on [Taiga.io](https://tree.taiga.io/project/greekpl-exeris/).

Wiki also on [Taiga.io](https://tree.taiga.io/project/greekpl-exeris/wiki/home).


Main principles
---------------
1. Automation is good if it makes things easier
2. Don't rely on hiding the global knowledge
3. Possible should be easy. Impossible should be impossible
4. Less numbers, more fun
5. Promote diversity
6. Promote activity
7. Nothing should last forever
8. More freedom, less restrictions
9. No immediate actions impacting other people