#Written By BushMasterJM
#All the imports
import requests
import random
import re
from bs4 import BeautifulSoup
from keep_alive import keep_alive
import praw
import os
import time
from colors import COL
from books import book_list

#Verse Identifier
def verse_identifer(text):
  book, chapter, verse, version, current = "", "", "", "", "" #Making 2 strings
  for letter in text:
    current+=letter #Addes letter to the current string
    if "random verse" in current.lower():
      ran_ver = True
      default = False
    else:
      if "(" in current.lower() and letter == ")":
        chap_ver = (re.findall("[0-9]+", current)) #https://docs.python.org/3/library/re.html
        chapter = (chap_ver[0])
        verse = (chap_ver[1])
        parts = current.rsplit("(", 1) #Splits out first 
        array = [phrase.split() for phrase in parts]
        book+=array[1][0]
        #book = "".join(re.split("[^a-zA-Z]*", str(parts[1])))
        item=len(array[1])
        default = False
        ran_ver = False
        versions = ['nkjv', 'asv', 'kjv'] #Supported version list
        
        if item >= 3: #Figures out version
          version+=array[1][2]
          version=version[0:len(version)-1]
  
          if version not in versions:
            version = "kjv"
            default = True
          else:
            default = False
        else:
          version = "kjv"
  
        current = "" #Resets current
      
  return [book, chapter, verse, version, default, ran_ver]

#Verse Scraper
def verse_scraper(verse_data):
  BOOK = verse_data[0] #Assigns all the data to convient variables
  CHAPTER = verse_data[1]
  VERSE = verse_data[2]
  VERSION = verse_data[3]
  reference = (verse_data[0]+" "+verse_data[1]+":"+verse_data[2])
  reference = reference.title()
  if verse_data[5] == True:
    final_verse = ""
    print(COL.WHITE + "-"*DASH_AMOUNT)
    print(COL.PURPLE + "RANDOM VERSE")
    print(COL.WHITE + "-"*DASH_AMOUNT)
    while final_verse == "":#Random Verse Scraper
      BOOK = random.choice(book_list) #Get random book
      CHAPTER = random.randint(1,151) #Gets random verse number
      VERSE = random.randint(1,177)
      CHAPTER = str(CHAPTER)
      VERSE = str(VERSE)
      VERSION = "kjv"
      print(BOOK, CHAPTER + ":" + VERSE)
      #URL to scrape from Source: https://beautiful-soup-4.readthedocs.io/en/latest/#quick-start
      page = requests.get("https://www.biblegateway.com/passage/?search="+BOOK+CHAPTER+"%3A"+VERSE+"&version="+VERSION) 
      soup = BeautifulSoup(page.content, 'html.parser')
      # Create all_h1_tags as empty list
      all_h1_tags = []
      # Set all_h1_tags to all h1 tags of the soup
      for element in soup.select('h1'):
        all_h1_tags.append(element.text)
      # Create seventh_p_text and set it to 7th p element text of the page
      scraped_data = soup.select('p')[0].text
      final_verse = re.sub('\(.*\)', '', scraped_data)
      reference = (BOOK+" "+CHAPTER+":"+VERSE)
      reference = reference.title()
  else:
    #URL to scrape from Source: https://beautiful-soup-4.readthedocs.io/en/latest/#quick-start
    page = requests.get("https://www.biblegateway.com/passage/?search="+BOOK+CHAPTER+"%3A"+VERSE+"&version="+VERSION) 
    soup = BeautifulSoup(page.content, 'html.parser')
    # Create all_h1_tags as empty list
    all_h1_tags = []
    # Set all_h1_tags to all h1 tags of the soup
    for element in soup.select('h1'):
      all_h1_tags.append(element.text)
    # Create seventh_p_text and set it to 7th p element text of the page
    scraped_data = soup.select('p')[0].text
    final_verse = re.sub('\(.*\)', '', scraped_data) #https://docs.python.org/3/library/re.html
  
  final_verse = final_verse.replace('\xa0', " ") #Takes out special spaces
  final_verse = final_verse.replace(";", "; ") #Formats
  final_verse = final_verse.replace(",", ", ") 
  final_verse=final_verse.replace("[a]", "") #Takes out footnote
  final_verse=final_verse.replace("[b]", "")
  final_verse=final_verse.replace("[c]", "")
  while "  " in final_verse:
    final_verse = final_verse.replace("  ", " ")
  if final_verse == "":
    final_verse = "Heresy! That isn't in the Bible." #Calls you a Heretic
  elif int(VERSE) <= 9: #Spaces everyting correctly at the start of the verse
    final_verse = final_verse[2:len(final_verse)]
  elif int(VERSE) <= 99:
    final_verse = final_verse[3:len(final_verse)]
  elif int(VERSE) >= 100:
    final_verse = final_verse[4:len(final_verse)]
  return [final_verse, reference, VERSION]

#Sign into Reddit Account
#Source: https://praw.readthedocs.io/en/stable/getting_started/quick_start.html
reddit = praw.Reddit(
  client_id = os.environ['client_id'],
  client_secret = os.environ['client_secret'],
  username = os.environ['username'],
  password = os.environ['password'],
  user_agent = "<Forgive70x7>" 
)
#Prints out the bot handle and ID for verification of sign in
username = os.environ['username']
reddit_profile = reddit.redditor(username)
print("Username: "+username)
print("ID: "+reddit_profile.id)

#Variables
BOT_ID = reddit_profile.id
DASH_AMOUNT = 5

keep_alive() #Keeps the bot alive

#Starts looking for comments in a subreddit
#Source: https://praw.readthedocs.io/en/stable/getting_started/quick_start.html
while True:
  try:
    #for comment in reddit.subreddit('all').stream.comments(skip_existing=True):
    for comment in reddit.inbox.stream(skip_existing=True): 
      author_name = str(comment.author.name) # Fetch author name
      author_id = str(comment.author.id) # Fetch author id
      comment_lower = comment.body.lower() # Fetch comment body and convert to lowercase
      redditor = reddit.redditor(author_name) # Gets account associated with username
    
      if "u/bible_man_bot" in comment_lower: #When the bot catches a comment
        verse_data = (verse_identifer(comment_lower)) 
        final_verse = (verse_scraper(verse_data))
        if verse_data[4] == True:
          full_reply = (final_verse[1]+" "+final_verse[2].upper()+" - "+final_verse[0]+"\n\n"+"^Your ^version ^could ^not ^be ^found ^so ^KJV ^was ^used ^instead.")
        else:
          full_reply = (final_verse[1]+" "+final_verse[2].upper()+" - "+final_verse[0])
        comment.reply(full_reply) # Replies to comment 
        # comment.reply(body = full_reply)
        print(COL.WHITE + "-"*DASH_AMOUNT)
        print(COL.PURPLE + "VERSE REPLY")
        print(COL.GREEN + "User:" + COL.WHITE, comment.author)
        print(COL.GREEN + "User ID:" + COL.WHITE, comment.author.id)
        print(COL.GREEN + "Comment:" + COL.WHITE, comment.body.lower())
        print(COL.GREEN + "Reply:" + COL.WHITE, str(full_reply))
        print(COL.GREEN + "Subreddit:" + COL.WHITE, comment.subreddit)
        print(COL.WHITE + "-"*DASH_AMOUNT)
        print(COL.CYAN + "Cooldown Started")
        time.sleep(60)
        print(COL.CYAN + "Cooldown Ended")
        
  except: #If stuff breaks
    print(COL.WHITE + "-"*DASH_AMOUNT)
    print(COL.PURPLE + COL.NEGATIVE + "Failed to reply", COL.END)
    print(COL.WHITE + "-"*DASH_AMOUNT)
    error_comment = comment_lower.replace("u/bible_man_bot", "")
    error_comment = error_comment.replace("(", "")
    error_comment = error_comment.replace(")", "")
    #Gives error reply and example
    comment.reply('''Sorry, I could'nt find "'''+error_comment+'''" in the Bible.'''+"\n"+"Try: (John 3:16) or (random verse)")