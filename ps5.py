
# 6.0001/6.00 Problem Set 5 - RSS Feed Filter
# Name: Naomi Geffken + Minh Quang Vu
# Collaborators:
# Time: ~14 hours


import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz




#-----------------------------------------------------------------------


#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================


def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)


        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
          #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
          #  pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")


        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret


#======================
# Data structure design
#======================


# Problem 1


# TODO: NewsStory

# Establish a New Object
class NewsStory(object):
    def __init__(self, guid, title, description, link, pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate
        
    def get_guid(self):
        return self.guid
    def get_title(self):
        return self.title
    def get_description(self):
        return self.description
    def get_link(self):
        return self.link
    def get_pubdate(self):
        return self.pubdate
#======================
# Triggers
#======================


class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError


# Parent trigger for the title and description triggers
class PhraseTrigger(Trigger):
    def __init__(self, phrase):
        phrase = str.lower(phrase) 
        self.phrase = phrase # set the phrase of object PhraseTrigger to be pharse
    def is_phrase_in(self, text): # checks if phrase is in text
        text = str.lower(text)
        for char in text:       # gets rid of punctuation in text
            if char in string.punctuation:
                text = text.replace(char, " ") 
        text = " ".join(text.split())
        
        text = " " + text + " "
        phrase = " " + self.phrase + " "
        if phrase in text: #check if phrase is in text
            return True
        else:
            return False
        

# Problem 3
# TODO: TitleTrigger
class TitleTrigger(PhraseTrigger): 
# hey future minh, you dont have to initialize every
    # time you create a new class if it does 
    # take any new parameter
    def __init__(self, phrase):
        PhraseTrigger.__init__(self, phrase)
    def evaluate(self, NewsStory):
        text = NewsStory.title
        return self.is_phrase_in(text)
    
# Problem 4
# TODO: DescriptionTrigger
class DescriptionTrigger(PhraseTrigger):
    def __init__(self, phrase):
        PhraseTrigger.__init__(self, phrase)
    def evaluate(self, NewsStory):
        text = NewsStory.description
        return self.is_phrase_in(text)


# TIME TRIGGERS


class TimeTrigger(Trigger):
    def __init__(self, string):
        self.datetime = datetime.strptime(string, "%d %b %Y %H:%M:%S")

# Problem 6
# TODO: BeforeTrigger and AfterTrigger
class BeforeTrigger(TimeTrigger):
    def __init__(self, story):
        TimeTrigger.__init__(self, story)
    def evaluate(self, story):
        return self.datetime.replace(tzinfo=pytz.timezone("EST")) > story.get_pubdate().replace(tzinfo=pytz.timezone("EST"))

# triggered if article occured after specific time
class AfterTrigger(TimeTrigger):
    def __init__(self, story):
        TimeTrigger.__init__(self, story)
    def evaluate(self, story):
        return self.datetime.replace(tzinfo=pytz.timezone("EST")) < story.get_pubdate().replace(tzinfo=pytz.timezone("EST"))



# COMPOSITE TRIGGERS
# Problem 7
# TODO: NotTrigger
class NotTrigger(Trigger):
    def __init__(self, some_trigger):
        self.trigger = some_trigger
    def evaluate(self, NewsStory):
        return not self.trigger.evaluate(NewsStory)
    
# Problem 8
# TODO: AndTrigger
class AndTrigger(Trigger):
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2
    def evaluate(self, NewsStory):
        return self.trigger1.evaluate(NewsStory) and self.trigger2.evaluate(NewsStory) 
    
# Problem 9
# TODO: OrTrigger
class OrTrigger(Trigger):
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2
    def evaluate(self, NewsStory):
        return self.trigger1.evaluate(NewsStory) or self.trigger2.evaluate(NewsStory) 




#======================
# Filtering
#======================


# Problem 10
def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    # TODO: Problem 10
    result = []
    
    for item in stories:
        for trigger in triggerlist:
            if trigger.evaluate(item) and item not in result:
                result.append(item)
    
    return result




#======================
# User-Specified Triggers
#======================
# Problem 11
def helper_read_trigger_config(trig_type, parameters): 
    if trig_type == "TITLE":
        trigger = TitleTrigger(parameters[0])
        return trigger
    elif trig_type == "DESCRIPTION":
        trigger = DescriptionTrigger(parameters[0])
        return trigger
    elif trig_type == "AFTER":
        trigger = AfterTrigger(parameters[0])
        return trigger
    elif trig_type == "BEFORE": 
        trigger = BeforeTrigger(parameters[0])
        return trigger
    elif trig_type == "NOT": 
        trigger = NotTrigger(parameters[0])
        return trigger
    elif trig_type == "AND": 
        trigger = AndTrigger(parameters[0], parameters[1])
        return trigger
    elif trig_type == "OR": 
        trigger = OrTrigger(parameters[0], parameters[1])
        return trigger
    

def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    # We give you the code to read in the file and eliminate blank lines and
    # comments. You don't need to know how it works for now!
    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)

    # TODO: Problem 11
    # line is the list of lines that you need to parse and for which you need
    # to build triggers

    result = []
    trigger_dict = {} # a dictionary of all the triggers called in txt; {name:parameters}
    
    for item in lines: 
        line_list = item.split(", ")
        
        if line_list[0] != "ADD":
            trigger_dict.update({line_list[0]: helper_read_trigger_config(line_list[1], line_list[2:])})
        else: 
            for trigger in line_list[1:]:
                result.append(trigger_dict.get(trigger))
   
    return result 
    



SLEEPTIME = 120 #seconds -- how often we poll


def main_thread(master):
    # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    try:
        t1 = TitleTrigger("election")
        t2 = DescriptionTrigger("Trump")
        t3 = DescriptionTrigger("Clinton")
        t4 = AndTrigger(t2, t3)
        triggerlist = [t1, t4]


        # Problem 11
        # TODO: After implementing read_trigger_config, uncomment this line 
        triggerlist = read_trigger_config('triggers.txt')
        
        # HELPER CODE - you don't need to understand this!
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)


        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())


        while True:


            print("Polling . . .", end=' ')
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/news?output=rss")


            # Get stories from Yahoo's Top Stories RSS news feed
            stories.extend(process("http://news.yahoo.com/rss/topstories"))


            stories = filter_stories(stories, triggerlist)


            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)




            print("Sleeping...")
            time.sleep(SLEEPTIME)


    except Exception as e:
        print(e)




if __name__ == '__main__':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()

