"""Partially based on Groompbot by /u/AndrewNeo
   
   Not really copied but come on how should I
   can't start with an empty page or whatever."""

import sys
import logging
import json
import gdata.youtube.service
import operator
import datetime


def getVideoIdFromEntry(entry):
    """Get video ID from a YouTube entry."""
    return entry.id.text.split("/")[-1]
	


def subscription_generator(client, uri):
    """(modified) from: http://stackoverflow.com/questions/12826680/
       how-to-get-all-youtube-comments-with-pythons-gdata-module
       Not recommended to use unlimited/at all (takes too long).
       First page usually contains most 'important' subscriptions."""
    sub_feed = client.GetYouTubeSubscriptionFeed(uri=uri)
    while (sub_feed is not None):
        for sub in sub_feed.entry:
             yield sub
        next_link = sub_feed.GetNextLink()
        if next_link is None:
             sub_feed = None
        else:
             sub_feed = client.GetYouTubeSubscriptionFeed(next_link.href)



def add_to_dict(d, e_key, delta):
    if e_key in d:
        d[e_key] += delta
    else:
        d[e_key] = delta




def get_channel(entry):
    """ 'Corrects channel names:
        'Videos published by: CollegeHumor' ->
        'CollegeHumor' """
    t = entry.title.text
    words = t.split(": ")
    if "http://www.youtube.com/user/" in words[-1]:
        misformatted = list(words[-1])
        formatted = misformatted[28:]
        return "".join(formatted)
    return words[-1]
    


def run(users=["vlogbrothers","zefrank1"]):
    
    logging.info("Starting script at "+str(datetime.datetime.now())+".")
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.ssl = True
    
    # ------------------------------
    # get subscriptions of channels
    # ------------------------------
    
    frequency = []
    for username in users:
        j += 1
        try:
            subscription_feed = yt_service.GetYouTubeSubscriptionFeed(username=username)
            for entry in subscription_generator(yt_service, uri=uri):
                if entry.GetSubscriptionType() == "channel":
                    add_to_dict(frequency, get_channel(entry), 1)
            logging.debug("Subscription feed number "+str(j)+" read successfully.")
        except gdata.service.RequestError:
            logging.error("gdata.service.RequestError"+
            " while counting subscriptions.")
        except:
            logging.error("Unexpected error"+
            " while counting subscriptions:"+str(sys.exc_info()[0]))
    
    # ------------------------------
    # save / return results
    # ------------------------------
    
    logging.info("Printing results.")
    
    """sort dict by most common answers"""
    sorted_channels = sorted(frequency.iteritems(),
        key=operator.itemgetter(1), reverse=True)
            
    logging.info("Writing results to file.")
    
    try:
        rf = open('results.json', 'r')
    except:
        logging.error("Error while opening to results.json.")
    try:
        results = json.load(rf)
        rf.close()
        run_no = results["run_number"] + 1
        results["run_number"] = run_no
        results[str(run_no)+sauce] = sorted_channels[:10]
    except:
        logging.error("Error while parsing to results.json. Is it empty?")
    try:
        rf = open('results.json', 'w')
        json.dump(results, rf)
        rf.close()
    except:
        logging.error("Error while writing data to results.json.")
    
    # only makes sense when using subscription_generator()
    #avg_subs = total_subs / float(total_users)
    logging.info("Results saved!")
    return sorted_channels
    
    



if __name__ == "__main__":
    # print to console - lots of errors while printing messages!?
    #logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    # print to log file
    logging.basicConfig(filename='log.log',level=logging.DEBUG)
    try:
        run()
    except SystemExit:
        logging.info("Exit called.")
    except:
        logging.error("Unexpected error:"+str(sys.exc_info()[0]))
    logging.info("Done!")
    logging.shutdown()

