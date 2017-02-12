What is Exeris?
===============
Exeris is an open-source, free, browser-based multiplayer mix of crafting and exploration game. It should let you collect wood in the forest, build a house, found a town or sail to the unknown lands.


Goals
-----
My main goal is to learn the new technologies (mainly Python and ES6) by solving the real, challenging problems. Creating a game I'd really enjoy playing looks like a perfect choice.

The game should be **able to be extremely challenging**, **self-managing**, not **time-restricted** (guarantee open-endness),
**slow paced** with **elastic time requirements** (good for busy people) and **full of surprises**.

I'm not looking for anybody to help me in programming, but suggestions, bug reports and proposals of bug fixes are welcome.

Plans
-----
The alpha version of the game is available on [dev.exeris.org](https://dev.exeris.org). To login you need to create an account on [users.exeris.org](https://users.exeris.org).

There is no planned release date, but I really hope to have a working Beta (with a dynamic, React-based user interface) in the first quarter of 2017.

Game features
-------------
By playing a character in the world consisting of two continents you can cooperate
or compete with other characters to collect resources and use them to build or craft
more advanced tools, machines, buildings or ships.

The world is split into two main continents, called **The Old** and **The New World**.

**The Old World** is a persistent group of islands where most of the new players start.
It's not very rich, but it's relatively safe to live there and easy to prepare basic tools or to found a town.

The most wealthy and fertile area is **The New World** - a land ready to be explored and settled to get its riches.
The lands of The New World should remain fresh for adventurers no matter when they start the game.
That's why The New World is not durable and, after certain period of time (about a year) **The New World** sinks in the ocean.
After a few days The New New World is generated and emerges from the ocean, ready to be explored and exploited.

Apart of that, almost every entity in the game needs to be built by players and it requires some maintenance to work.
When the environment created by players is abandoned, then it slowly comes back to its original state.
Tools or machines need to be repaired or they degrade until they turn into a pile of rubbish.
Food cannot be stored permanently, it starts to decay some time after it's produced.
When character dies, then their death is permanent and they cannot be revived in any way.

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

Development
-----------
Development progress - [Taiga.io](https://tree.taiga.io/project/greekpl-exeris/).

Development wiki - [Taiga.io](https://tree.taiga.io/project/greekpl-exeris/wiki/home).

Account management for forum, development server and chat - [users.exeris.org](https://users.exeris.org).

Development (test) server - [dev.exeris.org](https://dev.exeris.org).

Forum - [forum.exeris.org](https://forum.exeris.org).

Chat - [chat.exeris.org](https://chat.exeris.org).

Technologies
------------
 - Python
 - Flask + Flask-Socketio (and other Flask extensions)
 - Postgres + PostGIS
 - SQLAlchemy ORM
 - Pyslate i18n library
 - React + Redux frontend
