"""Partially based on Groompbot by /u/AndrewNeo
   
   Not really copied but come on how should I
   can't start with an empty page or whatever."""

import sys
import logging
import json
import gdata.youtube.service
import operator



def getVideoIdFromEntry(entry):
    """Get video ID from a YouTube entry."""
    return entry.id.text.split("/")[-1]
	



def comment_generator(client, video_id, limit=1):
    """(modified) from: http://stackoverflow.com/questions/12826680/
       how-to-get-all-youtube-comments-with-pythons-gdata-module"""
    # this line doesn't search by publishing order, but by 'relevance'
    comment_feed = client.GetYouTubeVideoCommentFeed(video_id=video_id)
    i = 0 # "[T]he API limits the number of entries that can be retrieved to 1000."
    while (comment_feed is not None and i<limit):
        i += 1
        for comment in comment_feed.entry:
             yield comment
        next_link = comment_feed.GetNextLink()
        if next_link is None:
             comment_feed = None
        else:
             comment_feed = client.GetYouTubeVideoCommentFeed(next_link.href)

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
    


def run(sauce="vlogbrothers"):
    
    logging.info("Starting script.")
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.ssl = True
    
    # ------------------------------
    # get third-to-last video of youtuber
    # ------------------------------
    
    yt_service = gdata.youtube.service.YouTubeService()
    # check if sauce is an actual channel that exists TODO
    # ^handled by big clause at the beginning right?
    uri = "http://gdata.youtube.com/feeds/api/users/"+sauce+"/uploads"
    logging.info("Looking for a video by "+sauce+".")
    feed = yt_service.GetYouTubeVideoFeed(uri)
    uploads = feed.entry
    try:
        video = uploads[2] # the third-newest video should
        # have been around for long enough to be 'average'
    except:
        video = uploads[0] # new channels
    videoid = getVideoIdFromEntry(video)
    logging.info("Got 'typical' video. ["+
        unicode(video.title.text, "utf-8") +"] ("+videoid+").")
    
    # ------------------------------
    # get a list of 'fans' using the commenters
    #
    # in v3, there is an option to get the subscribers
    # directly. see: https://code.google.com/p/
    # gdata-issues/issues/detail?id=300#c129
    # ------------------------------
    
    fan_uris = []
    limit = 2 # times 25 users to scan (~10*limit minutes)
    for comment in comment_generator(yt_service, videoid, limit=limit):
        fan_uris.append(comment.author[0].uri.text)
    logging.info("Got all commenter URIs.")
    
    # ------------------------------
    # get subscriptions of commenters
    # ------------------------------
    
    frequency = {}
    j = 0
    total_subs = 0
    total_users = 0
    for partial_uri in fan_uris:
        if True:
            j += 1
            #userid = getVideoIdFromEntry(uri) # abusing this
            try:
                uri = partial_uri + "/subscriptions"
                subscription_feed = yt_service.GetYouTubeSubscriptionFeed(uri=uri)
                #for entry in subscription_generator(yt_service, uri=uri):
                for entry in subscription_feed.entry:
                    if entry.GetSubscriptionType() == "channel":
                        add_to_dict(frequency, get_channel(entry), 1)
                        total_subs += 1
                logging.debug("Subscription feed number "+str(j)+" read successfully.")
                total_users += 1
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
        results = json.load(rf)
        rf.close()
        run_no = results["run_number"] + 1
        results["run_number"] = run_no
        results[str(run_no)+sauce] = sorted_channels
        rf = open('results.json', 'w')
        json.dump(results, rf)
        rf.close()
    except:
        logging.error("Error while opening/parsing/writing data to results.json.")
    
    # only makes sense when using subscription_generator()
    #avg_subs = total_subs / float(total_users)
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

