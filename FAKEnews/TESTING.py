import requests

from lxml import html
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import re
import ssl

class Paragraph:
    def __init__(self):
        self.attributes = []
        self.text = ""

    def __repr__(self):
        return "text: {}\nAttributes: {}\n".format(self.text, self.attributes)

ssl._create_default_https_context = ssl._create_unverified_context

def pyGoogleSearch(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    phrase_extract = soup.find(id="resultStats")
    print(phrase_extract)

def pyGoogleSearchWORD(word):
    google = 'http://www.google.co.uk/search?q='
    news = '&tbm=nws'
    rankbydate = '&tbs=sbd:1'
    url = google + word + news +rankbydate

    print(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    phrase_extract = soup.find(id="resultStats")


    print("results" + phrase_extract)

'''
def pyfindAuthor(url):
    print(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    phrase_extract = soup.find(id="sdc-news-story-article__byline")
    print(phrase_extract)
'''


url = 'https://news.sky.com/story/how-missing-dubai-princess-practised-her-escape-11572555' #('Paste URL here:') "




req = urllib.request.Request(url)#, data)
resp = urllib.request.urlopen(req)
respData = resp.read()

paragraphs = BeautifulSoup(respData, 'html.parser' ).find_all("p")


'''
for p in paragraphs:
    new_paragraph = Paragraph()
    new_paragraph.text = p.string
    new_paragraph.attributes = p.attrs
    print(new_paragraph)
'''



text = [p.string for p in paragraphs]


'''
message = """Millions of commuters will have to pay an average of 3.1% more for rail tickets from 2 January.

The rise, announced by industry body the Rail Delivery Group, follows a year of disruption on some lines.

There had been calls for a price freeze following the chaos caused by the introduction of new timetables in May.

The rise, which is lower than the 3.4% average rise for fares in 2018, means another £100 for a Manchester to Liverpool annual season ticket.

Anthony Smith, chief executive of independent watchdog Transport Focus, said the rail industry got £10bn a year from passengers, who wanted a reliable railway offering better value for money: "They shouldn't have to wait any longer for that."

Fewer than half (45%) of passengers are satisfied with the value for money of train tickets, according to Transport Focus.

Alex Hayman of consumer group Which? said the new price rises would only add to passengers' misery after a year of timetable chaos, with rail punctuality falling to its lowest level in 12 years.

"Value for money needs to be a key part of the upcoming government review and passengers must receive automatic compensation for delays and cancellations," he said.

Shadow transport secretary Andy McDonald said the increase showed "a government and rail industry out of touch with passenger concerns".

What do the unions say?
Unions also took aim at the price increases, with RMT general secretary Mick Cash calling them "another kick in the teeth for passengers on Britain's rip-off privatised railways".

It meant UK passengers will pay the highest fares in Europe. "That is nothing short of a disgrace," he added.

Transport Salaried Staffs Association general secretary Manuel Cortes said: "A fare freeze would have been appropriate, but once again hard-pressed commuters are being milked like cash cows into paying more money for less."

Watchdog orders Network Rail to improve
'Nobody took charge' in timetable chaos
How to avoid expensive train tickets
What does the rail industry say?
Rail Delivery Group (RDG) chief executive Paul Plummer admitted that no one wanted to pay more to travel, "especially those who experienced significant disruption earlier this year".

"Money from fares is underpinning the improvements to the railway that passengers want and which ultimately help boost the wider economy," he said.

The RDG said train companies would introduce 7,000 new carriages, supporting 6,400 extra services a week by 2021, meaning more seats on more reliable, comfortable and frequent trains.

How can I save money on rail fares?
Buy next year's annual season ticket before 2 January to take advantage of 2018 prices. An annual ticket usually costs about the same as 10 monthly tickets
Transport Focus advises season ticket holders to complain if services are disrupted. Services delayed by an hour attract a 50% refund, but some do the same after delays of just 30 minutes
Book as early as possible for the cheapest fares. Advance tickets go on sale about three months out
Buy tickets directly from a rail operator's website, not a third party, to avoid booking fees
Get a 16-25 railcard if you're under 26 or a full-time student of any age, or the new 26-30 railcard. Both cost £30 for a year and offer a third off tickets for most journeys. Buying an annual London Travelcard offers the same savings on train tickets
Splitting your journey into multiple tickets can cut the overall cost - but your tickets must cover the whole journey and the train must actually stop at that station
Will the politicians change the rail fare system?
By Tom Burridge, BBC transport correspondent

Labour says fares should be frozen when performance isn't up to scratch. Passenger groups agree.

However, the industry and the government point to more fundamental issues.

With so many people now travelling by train, there are many more services operating on ancient infrastructure.

Government funding for expensive upgrade projects to deal with overcrowding is only possible, rail bosses say, if passengers - not taxpayers in general - cover the bulk of everyday running costs.

And they say if rail fares are frozen, rail companies' costs still rise in line with inflation.

Again, the operators argue that taxpayers should not be left to plug that gap.

What's happening with the new 26-30 railcard?
By Kevin Peachey, BBC personal finance reporter

The launch of the new "millennial" railcard, which will be available to four million passengers, is running slightly late.

The Rail Delivery Group had promised that the digital-only 26-to-30 railcard would be available before the end of the year, but that has been put back until midday on 2 January.

For a £30 fee, the new railcard will offer one-third off most leisure fares for 12 months. However, anyone travelling before 10am on a weekday will have to pay a minimum fare of £12. This is the same restriction as on the 16-25 railcard. Unlike the card for younger passengers, that minimum fare will also apply on weekdays throughout July and August.

The launch of the card, which cannot be used for season tickets, was originally announced by the chancellor in the autumn 2017 Budget.

Full details and a savings calculator are available on the railcard website."""
'''
message = ','.join(str(text))
word_freqs = {}

remove_chars = [',', '.', '?', '!', '"', "'", ";"]

for rc in remove_chars:
    message = message.replace(rc, "")

message_words = message.split()

# http://xpo6.com/list-of-english-stop-words/
ignore_words = ["Say", "say", "The", "a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost",
                "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst",
                "amount", "an", "and", "another", "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are",
                "around", "as", "at", "back", "be", "became", "because", "become", "becomes", "becoming", "been",
                "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill",
                "both", "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry",
                "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either",
                "eleven", "else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone",
                "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five",
                "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get",
                "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby",
                "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie",
                "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter",
                "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine",
                "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely",
                "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not",
                "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other",
                "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps",
                "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious",
                "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow",
                "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten",
                "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter",
                "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this",
                "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top",
                "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very",
                "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where",
                "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while",
                "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without",
                "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]

for word in message_words:

    if word not in ignore_words:

        if not word in word_freqs.keys():
            word_freqs[word] = 1

        else:
            word_freqs[word] += 1

sorted_words = sorted(word_freqs.items(), key=lambda x: x[1], reverse=True)

print(sorted_words)
max_words = 5

query_words = sorted_words[:max_words]

query_string = "https://www.google.co.uk/search?q="

for qw in query_words:
    query_string += qw[0] + "+"

query_string += "&tbm=nws&tbs=sbd:1"
print(query_string)

pyGoogleSearch(query_string)


def get_author(paragraphs, author_class_identifier):

    for p in paragraphs:

        if author_class_identifier in str(p):
            return p.text

    return None


def get_headline(paragraphs, headline_class_identifier):

    for p in paragraphs:

        if headline_class_identifier in str(p):
            pyGoogleSearch('http://www.google.co.uk/search?q='+p.text)
            return p.text

    return None
print(paragraphs)
print(get_author(paragraphs, "sdc-news-story-article__byline"))
print(get_headline(paragraphs, "sdc-news-article-header__standfirst"))
#search_text =[p.string for p in paragraphs]



domain = urllib.parse('http://www.google.com/').hostname
print(str(domain))




'''
url = "https://news.sky.com/"

content = urllib2.urlopen(url)#https://www.pythonforbeginners.com/beautifulsoup/beautifulsoup-4-python

mybytes = content.read()



mystr = mybytes.decode("utf8")
content.close()

print(mystr)

soup = BeautifulSoup(content, 'html.parser')
print(soup.body.string)


pyGoogleSearch('Google')
'''

news = open('bbc news example.html', 'r').read()



#html = '''
#<head>
#</head>
#<body>
 # <div id="headline"> hello </div>
 # <div id="text"> hello </div>
 
#</body>





#page = requests.get('https://news.sky.com/story/fog-sparks-cancellations-and-delays-at-airports-as-storm-diana-looms-11565046.html')
#tree = html.fromstring(page.content)
#print(tree)
'''

fp = urllib2.urlopen("http://www.python.org")
mybytes = fp.read()

mystr = mybytes.decode("utf8")
fp.close()

print(mystr)

'''





#print(BeautifulSoup(news, 'html.parser' ).find("p", {'class':'story-body__introduction'}).text)
