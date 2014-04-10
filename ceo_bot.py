"""Partially based on Groompbot by /u/AndrewNeo
   
   Not really copied but come on how should I
   can't start with an empty page or whatever."""

import sys
import logging
import json
import praw
import time
import ceo_local
import logging


def getReddit(settings):
    """Get a reference to Reddit."""
    r = praw.Reddit(user_agent=settings["reddit_ua"])
    try:
        r.login(settings["reddit_username"], settings["reddit_password"])
    except:
        logging.exception("Error logging into Reddit.")
        sys.exit(1)
    return r



def format_message(tuple_array, sauce):
    """Format a tuple_array (each entry: (number, string))
       and then some into a message printable by reddit."""
    logging.info("Formatting message.")
    lmsg = ("People who had a popular comment on "+ sauce +
        " were also subscribed to:")
    lmsg += "\n\n| Subs | Channel name |"
    lmsg += "\n|-----:|:-------------|"
    for tulpa in tuple_array:
        if tulpa[1] > 2:
            try:
                lmsg += "\n| "+str(tulpa[1])+" | "+tulpa[0]
            except IndexError:
                pass
    #lmsg += ("\n\nAverage number of subscriptions: "+str(avg_subs))
    lmsg += ("\n\n~~--------------------------------------------------~~"+
    "\n\nI am a bot. | [About](http://www.reddit.com/r/altnames/comments"+
    "/22lldb/ucheck_em_out_vlogbrothers_limit4/) | [Source]"+
    "(https://github.com/xjcl/check_em_out)")
    return lmsg



def get_sauce_from_comment(comment):
    lines = comment.body.split("\n")
    try:
        if lines[0] != "/u/check_em_out":
            assert lines[0].startswith("/u/check_em_out")
            return lines[0][16:]
        else:
            if lines[1] != "":
                return lines[1]
            else:
                return lines[2]
    except:
        logging.error("Error getting source channel from comment "+comment.id+".")
        return None


def parse_comment(comment):
    """Check if comment meets conditions and iff it does,
       run the program and comment on it (with output or error msg)"""
    if "/u/check_em_out" in comment.body:
        sauce = get_sauce_from_comment(comment)
        if sauce:
            try:
                sorted_channels = ceo_local.run(sauce=sauce)
                assert len(sorted_channels) > 0
                msg = format_message(sorted_channels, sauce)
            except:
                msg = "Unexpected error:"+str(sys.exc_info()[0])
                logging.error(msg)
            try:
                logging.info("Responding to '"+sauce+"' ("+comment.id+")")
                comment.reply(msg)
                logging.info("Comment succeeded!")
                return comment.id
            except praw.errors.RateLimitExceeded:
                logging.error("Comment failed (RateLimitExceeded)."+
                    " /r/FreeKarma?")
            except:
                logging.error("Unexpected error:"+str(sys.exc_info()[0]))
    return None


    
def listen(reddit, answered_coms, subreddits=["all"], limit=10000):
    """Check newest comments for bot calls."""
    subreddit = "+".join(subreddits)
    logging.debug("Searching through these subreddits: "+subreddit)
    # the only way to reverse the list would be to store it locally -
    # which would be painful.
    for comment in reddit.get_subreddit(subreddit).get_comments(limit=limit):
        if comment.id not in answered_coms:
            new_id = parse_comment(comment)
            if new_id:
                answered_coms.append(new_id)
    return answered_coms




def loadSettings():
    """Load settings from file."""
    try:
        settingsFile = open("settings.json", "r")
    except IOError:
        logging.exception("Error opening settings.json.")
        sys.exit(1)
    try:
        settings = json.load(settingsFile)
        settingsFile.close()
    except ValueError:
        logging.exception("Error parsing settings.json.")
        sys.exit(1)
    
    # Check integrity
    for variable in ["reddit_username", "reddit_password", "reddit_ua", "subreddits"]:
        if (len(settings[variable]) == 0):
            logging.critical(variable+" not set.")
            sys.exit(1)
    return settings



def runBot():
    """Start a run of the bot."""
    logging.info("Starting bot.")
    settings = loadSettings()
        
    logging.info("Logging into Reddit.")
    reddit = getReddit(settings)
        
    # Search comments and post
    # answered_coms prevents responding to the
    # same comment twice
    answered_coms = []
    try:
        of = open('answered_coms.json', 'r')
        answered_coms = json.load(of)
        of.close()
    except IOError:
        logging.info("answered_coms.json doesn't exits / data is not readable."
            +" Using empty list instead.")
        
    while True:
        logging.info("Looking for new comments.")
        answered_coms = listen(reddit, answered_coms, settings["subreddits"], 10000)
        logging.info("Writing comment ids to file.")
        sf = open('answered_coms.json', 'w')
        json.dump(answered_coms, sf)
        sf.close()
        logging.info("Done!")
        time.sleep(2)



if __name__ == "__main__":
    # print to console - lots of errors while printing messages!?
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    # print to log file
    #logging.basicConfig(filename='log.log',level=logging.DEBUG)
    try:
        runBot()
    except SystemExit:
        logging.info("Exit called.")
    except:
        logging.exception("Uncaught exception.")
    logging.shutdown()
    

