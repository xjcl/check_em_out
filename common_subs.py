"""Partially based on Groompbot by /u/AndrewNeo
   
   Not really copied but come on how should I
   can't start with an empty page or whatever."""

import sys
import logging
import json
import gdata.youtube.service
import operator
import datetime


def subscription_generator(client, username):
    """(modified) from: http://stackoverflow.com/questions/12826680/
       how-to-get-all-youtube-comments-with-pythons-gdata-module
       Not recommended to use unlimited/at all (takes too long).
       First page usually contains most 'important' subscriptions."""
    sub_feed = client.GetYouTubeSubscriptionFeed(username=username)
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
    


def run(users=["zefrank1","GreaterJan"]):
    
    logging.info("Starting script at "+str(datetime.datetime.now())+".")
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.ssl = True
    
    # ------------------------------
    # get subscriptions of channels
    # ------------------------------
    
    frequency = {}
    j = 0
    for username in users:
        j += 1
        try:
            for entry in subscription_generator(yt_service, username):
                if entry.GetSubscriptionType() == "channel":
                    add_to_dict(frequency, get_channel(entry), 1)
            logging.debug("Subscription feed number "+str(j)+" read successfully.")
        except gdata.service.RequestError:
            logging.error("gdata.service.RequestError"+
            " while counting subscriptions.")
        except:
            logging.error("Unexpected error"+
            " while counting subscriptions:"+str(sys.exc_info()[0])+
            str(sys.exc_info()[1]))
    
    # ------------------------------
    # save / return results
    # ------------------------------
    
    """sort dict by most common answers"""
    sorted_channels = sorted(frequency.iteritems(),
        key=operator.itemgetter(1), reverse=True)
            
    logging.info("Writing results to file.")
    
    try:
        rf = open('results2.json', 'r')
    except IOError:
        logging.info("results2.json doesn't exist. Using null data instead.")
    try:
        results = json.load(rf)
        run_no = results["run_number"] + 1
        rf.close()
    except:
        logging.error("Error while parsing results2.json.")
        results = {}
        run_no = 1
    results["run_number"] = run_no
    results[str(run_no)+": "+"".join(users)] = sorted_channels[:10]
    try:
        rf = open('results2.json', 'w')
        json.dump(results, rf)
        rf.close()
    except:
        logging.error("Error while writing data to results2.json.")
    
    # only makes sense when using subscription_generator()
    #avg_subs = total_subs / float(total_users)
    logging.info("Results saved!")
    return sorted_channels
    
    



if __name__ == "__main__":
    # print to console - lots of errors while printing messages!?
    #logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    # print to log file
    logging.basicConfig(filename='log2.log',level=logging.DEBUG)
    try:
        run()
    except SystemExit:
        logging.info("Exit called.")
    except:
        logging.error("Unexpected error:"+str(sys.exc_info()[0]))
    logging.info("Done!")
    logging.shutdown()

