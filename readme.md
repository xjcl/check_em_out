check\_em\_out
=========

A bot that takes a channel name and looks for other channels that are popular with popular commentators (!=subscribers) of that channel. An intro to what the bot does can be found [here](http://www.reddit.com/r/nerdfighters/comments/22mhxr/i_wrote_a_bot_that_takes_a_youtube_channel_and/).

Usage
-----

Just run `python ceo_bot.py`

The bot is already looped within that file.

Configuration
-------------

The configuration file is "settings.json" and should be copied from "settings.json.default". It should contain the reddit bot username (without /u/), password, the subreddits to check and comment in, an approperate useragent (a name under which the bot communicates with reddit - see default file for an example).

Dependencies
------------

check\_em\_out depends on the following external libraries:

* [praw](https://github.com/praw-dev/praw/) - Reddit library
* [gdata](http://code.google.com/p/gdata-python-client/) - Google Data API

Some parts of the code are copied from [groompbot](https://github.com/AndrewNeo/groompbot).

License
-------

check\_em\_out is free to use under the MIT License.

