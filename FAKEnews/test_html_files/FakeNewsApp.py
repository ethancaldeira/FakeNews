import requests, urllib.parse, urllib.request,ssl, sqlite3, random, pickle, numpy as np
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing
from pandas.plotting import scatter_matrix


ssl._create_default_https_context = ssl._create_unverified_context

class DBInterface: #Class that handles the connection to the databases

    DB = sqlite3.connect('FakeNewsDB.sqlite')#Establishes a connection to the database
    DB.row_factory = sqlite3.Row#
    cursor = DB.cursor()#

    @staticmethod#Static Method to be used later
    def get_article_class_identifiers(domain):#Mehtod that gets all the class identifiers from the collection of identifiers so that they can be used later

        domain_classes = {'author':None, 'verified':None}

        domain_data = DBInterface.DB.execute("SELECT verified, authorclassIdentifier, headlineClassIdentifier, datetimeClassIdentifier FROM Domains WHERE Domains.domain=?", [domain]).fetchone()

        if domain_data:

            domain_classes = {
                'author': domain_data['authorClassIdentifier'],
                'verified': True if domain_data['verified'] == 1 else False,
                'headline': domain_data['headlineClassIdentifier'],
                'dateTIME': domain_data['datetimeClassIdentifier'],
            }

        return domain_classes

    @staticmethod
    def add_features(n):
        DBInterface.DB.execute('UPDATE URL_Collection SET author = "{}", wordLength = "{}", noRelatedSearches = "{}", percentEmotiveLang = "{}", headlinetextLength = "{}", processedInd = "{}" WHERE "{}" = url'.format(n.get_features_list()[0],n.get_features_list()[1],n.get_features_list()[2],n.get_features_list()[3],n.get_features_list()[4], "TRUE" ,n.url))
        DBInterface.DB.commit()
    @staticmethod
    def get_features_from_DB(count):
         results =('SELECT author, wordLength, noRelatedSearches, percentEmotiveLang, headlineTextLength FROM URL_Collection WHERE URL_Collection.id="{}"'.format(count))
         #print('RESULTS ' + results)
         values = DBInterface.DB.execute(results).fetchone()
         values = (list(values[:5]))
         #print(values)
         return values

    @staticmethod
    def add_new_news_source(url, label):
        sql = "INSERT INTO 'URL_Collection' (url, fakeOrReal) VALUES ('{}', {})".format(url, label)
        print(sql)
        DBInterface.DB.execute(sql)
        DBInterface.DB.commit()



    @staticmethod
    def get_domains(count):
        domain = DBInterface.DB.execute('SELECT domain FROM Domains WHERE Domains.id=?', [count]).fetchone()
        domain = str(domain[0])
        return domain


    @staticmethod
    def get_urls(count):#Method to get the URLS

        #for url in
        url_data = DBInterface.DB.execute('SELECT url FROM URL_Collection WHERE URL_Collection.id=?', [count]).fetchone()
        urls = url_data[0]

        return urls
    #urls = DBInterface.DB.execute("SELECT url FROM URL_Collection ")

    @staticmethod
    def get_all_rows(table_name):
        row_count = ('SELECT count(*) FROM "{}"'.format(table_name))
        DBInterface.cursor.execute(row_count)
        rows = DBInterface.cursor.fetchone()[0]
        return rows

    @staticmethod
    def count_unprocessed_URLs():
        row_count = ('SELECT count(*) FROM URL_Collection WHERE processedInd = "{}" '.format('FALSE'))
        DBInterface.cursor.execute(row_count)
        rows = DBInterface.cursor.fetchone()[0]
        return rows

    @staticmethod
    def fake_or_real(count):


        fake_or_real_data = DBInterface.DB.execute('SELECT fakeOrReal FROM URL_Collection WHERE URL_Collection.id=?', [count]).fetchone()
        fake_or_real = fake_or_real_data[0]
        return fake_or_real
    #urls = DBInterface.DB.execute("SELECT url FROM URL_Collection ")

class NewsItem:
    def __init__(self, url, Fake_OR_real ):
        self.__url = url

        self.__fake_or_real = Fake_OR_real
        self.__domain = self.__generate_domain()

        self.__paragraphs, self.__headlines, self.__textContents = self.__generate_textContents()

        domain_data = DBInterface.get_article_class_identifiers(self.__domain)

        self.__headlineText = self.__generate_headlineText(domain_data['headline'])

        self.__author = self.__generate_author(domain_data['author'])

        self.__verified = domain_data['verified']

        self.__dateTime = self.__generate_dateTime(domain_data['dateTIME'])

        self.__mostFreqWords = WordFreqAnalysis.generateSorted_Words(self.__textContents)
        print("Most frequent Words: " + str(self.mostFreqWords))

        self.__word_length = self.__generate_word_length()

        self.__percentageOfEmotiveLang = self.__generate_percentageOfEmotivelang()

        self.__NoOfrelatedSearches = self.__generate_NoOfrelatedSearches()


    @property
    def url(self):
        return self.__url

    @property
    def fake_or_real(self):
        return self.__fake_or_real
    @property
    def domain(self):
        return self.__domain

    @property
    def headlineText(self):
        return self.__headlineText

    @property
    def author(self):
        return self.__author

    @property
    def verified(self):
        return self.__verified

    @property
    def dateTime(self):
        return self.__dateTime

    @property
    def mostFreqWords(self):
        return self.__mostFreqWords

    @property
    def word_length(self):
        return self.__word_length

    @property
    def percentageOfEmotiveLang(self):
        return self.__percentageOfEmotiveLang

    @property
    def NoOfrelatedSearches(self):
        return self.__NoOfrelatedSearches
#IMPROVE
    def __generate_textContents(self):
        req = urllib.request.Request(self.__url)
        resp = urllib.request.urlopen(req)
        respData = resp.read()
        #self.__paragraphs = BeautifulSoup(respData, 'html.parser').find_all("p")
        paragraphs = BeautifulSoup(respData, 'html.parser').find_all("p")
        # H1 NEEDED FOR HEADLINE
        #self.__headlines = BeautifulSoup(respData, 'html.parser').find_all("h1")
        headlines = BeautifulSoup(respData, 'html.parser').find_all("h1")
        #self.__textContents = [p.string for p in self.__paragraphs]
        textContents = [p.string for p in paragraphs]
        return paragraphs, headlines, textContents




    def __generate_domain(self):
        self.__domain = urlparse(self.__url).netloc
        return self.__domain

    def __generate_headlineText(self, headline_class_identifier):
        for h in self.__headlines:
            if headline_class_identifier in str(h):
                return h.text

            return None

    @staticmethod # TODO: DOES THIS NEED TO BE STATIC
    def __extract_number_from_string(s):
        """ Utility function created to remove digits from strings so that they do not interfere with word frequency
        analysis of news article """

        digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

        number_string = ""

        for c in s: # for character c in string s
            if c in digits:
                number_string += c

        return int(number_string)

#ADD number of wordsFreq and also add the ability to search data time(be sure that it is valid) if none do not use date time specification
    def __generate_NoOfrelatedSearches(self):


        url = WordFreqAnalysis.generate_related_query_url(WordFreqAnalysis.generateSorted_Words(self.__textContents))
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        results_stats = soup.find(id="resultStats")


        return self.__extract_number_from_string(results_stats.text)

    def __generate_author(self, author_class_identifier):

        if not author_class_identifier:
            return None

        for p in self.__paragraphs:

            if author_class_identifier in str(p):
                return p.text

        return None

    def __generate_dateTime(self, datetime_class_identifier):
        for p in self.__paragraphs:

            if datetime_class_identifier in str(p):
                return p.text

    def __generate_word_length(self):
        self.__word_length = 0
        for t in self.__textContents:
            if t is not None:
                self.__word_length += len(t.split(" "))
        return self.__word_length

    def __generate_percentageOfEmotivelang(self):

        emotivelang = []#https://cpb-ap-se2.wpmucdn.com/global2.vic.edu.au/dist/5/3744/files/2011/01/Persuasive-Language-Word-Bank-1e3i059.pdf

        TextFile = open('emtovielang.txt', 'r')
        for w in TextFile:
            emotivelang.append(w.strip().upper())
        TextFile.close()


        Emotivelang_Count = 0

        for textblock in self.__textContents:
            if textblock is not None:
                words_in_block = textblock.upper().split(" ")
                for word in words_in_block:
                    if word in emotivelang:
                        Emotivelang_Count =+ 1
        if self.__word_length == 0:
            return 0
        return  ((Emotivelang_Count/self.__word_length))

        # DO THIS too


    def get_features_list(self):
        f_list = []
        f_list.append(1 if self.author else 0)
        if self.author:
            auth=True
        else:
            auth=False
        print("Author found: " + str(auth))
        print("Date and Time: " + str(self.dateTime))
        f_list.append(self.word_length)
        f_list.append(self.NoOfrelatedSearches)
        print("No of related searches: " + str(self.NoOfrelatedSearches))
       #f_list.append(1 if self.verified == True else 0)
        f_list.append(self.percentageOfEmotiveLang)
        emotiveWords = self.percentageOfEmotiveLang*100
        print("Percentage of emotive words: " + str(emotiveWords) + "%")
        f_list.append(len(self.headlineText) if  self.headlineText else 0)
        print("Headline Text is: " + str(self.headlineText))
        print("Headline Length is: " + str(len(self.headlineText)))


        return f_list


    def __repr__(self):
        return "<NewsItem object -\nURL: {}\nDomain:{}\nHeadline:{}\nAuthor:{}\nDate_Time:{}\nNumber Of Realted Searches:{}\nWord Count:{}\nPercentage of Emotive Language:{}\nVerified:{}\nHas headline: {}\nHas author: \nHas Datetime: ".format(
            self.__url, self.__domain, self.__headlineText, self.__author, self.__dateTime, self.__NoOfrelatedSearches,
            self.__word_length, self.__percentageOfEmotiveLang ,self.__verified, self.__headlineText != None, self.__author != None,  self.__dateTime != None)

class WordFreqAnalysis:

    @staticmethod
    def generateSorted_Words(stringlist):
        word_freqs = {}

        articleText = ""
        for word in stringlist:
            if word:
                articleText += word
        #articleText = ','.join(str(stringlist))
        ignore_words = ["I", "Say", "say", "The", "a", "about", "above", "above", "across", "after", "afterwards",
                               "again",
                               "against", "all", "almost",
                               "alone", "along", "already", "also", "although", "always", "am", "among", "amongst",
                               "amoungst",
                               "amount", "an", "and", "another", "any", "anyhow", "anyone", "anything", "anyway",
                               "anywhere",
                               "are",
                               "around", "as", "at", "back", "be", "became", "because", "become", "becomes", "becoming",
                               "been",
                               "before", "beforehand", "behind", "being", "below", "beside", "besides", "between",
                               "beyond",
                               "bill",
                               "both", "bottom", "but", "by", "call", "can", "cannot", "cant","can't", "co", "con", "could",
                               "couldnt", "contact",
                               "cry",
                               "de", "describe", "detail", "do", "done", "don't", "down", "due", "during", "each", "eg", "eight",
                               "either",
                               "eleven", "else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every",
                               "everyone",
                               "everything", "everywhere", "except", "few", "fifteen", "fifty", "fill", "find", "fire",
                               "first",
                               "five",
                               "for", "former", "formerly", "forty", "found", "four", "from", "front", "full",
                               "further",
                               "get",
                               "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter",
                               "hereby",
                               "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however",
                               "hundred",
                               "ie",
                               "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep",
                               "last",
                               "latter",
                               "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might",
                               "mill", "man",
                               "mine",
                               "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name",
                               "namely",
                               "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone",
                               "nor",
                               "not",
                               "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto",
                               "or",
                               "other",
                               "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own", "part", "per",
                               "perhaps",
                               "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems",
                               "serious",
                               "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so",
                               "some", "said",
                               "somehow",
                               "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system",
                               "take",
                               "ten",
                               "than", "that", "the", "their", "them", "themselves", "then", "thence", "there",
                               "thereafter",
                               "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin",
                               "third",
                               "this",
                               "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together",
                               "too",
                               "top",
                               "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon",
                               "us",
                               "very",
                               "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever",
                               "where",
                               "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether",
                               "which",
                               "while",
                               "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within",
                               "without",
                               "would", "yet", "you", "your", "yours", "yourself", "yourselves", "&",
                               "the"]  # http://xpo6.com/list-of-english-stop-words/
        remove_chars = [',', '.', '?', '!', '"', "'", ";"]

        for rc in remove_chars:
            if rc == "'":
                articleText = articleText.replace(rc, "")
            else:
                articleText = articleText.replace(rc, " ")

        message_words = articleText.split()

        for word in message_words:

            if word not in ignore_words:

                if not word in word_freqs.keys():
                    word_freqs[word] = 1

                else:
                    word_freqs[word] += 1

        sorted_words = sorted(word_freqs.items(), key=lambda x: x[1], reverse=True)


        max_words = 5

        query_words = sorted_words[:max_words]

        return query_words


    @staticmethod
    def generate_related_query_url(freq_words):

        query_string = "https://www.google.co.uk/search?q="

        for qw in freq_words:
            query_string += qw[0] + "+"


        query_string = query_string[:-1] #Removes the extra +
        #query_string += "&tbm=nws&tbs=sbd:1" #news = '&tbm=nws' rankbydate = '&tbs=sbd:1'
        return query_string

class NewsItemDataset:

    def __init__(self):
        self.__newsItems = []
        self.__labels = []
        self.__non_normalised_dataset = []
        self.__model = KNeighborsClassifier(n_neighbors=1)
        # When generating from URLs, run next two lines
        self.__read_urls_from_DB()

        # When using saved NewItems data
        # self.read_dumped_data()
        #self.__dataset = self.__generate_Dataset()



    def read_data_from_DB(self):
        count = 1
        while count <= DBInterface.get_all_rows("URL_Collection"):
            self.__non_normalised_dataset.append((DBInterface.get_features_from_DB(str(count))))
            #print(('Appending to dataset ' + str(count)))
            self.__labels.append(DBInterface.fake_or_real(count))
            #print(('Appending to labels ' + str(count)))
            count = count +1
        #print(self.__non_normalised_dataset)


    def __read_urls_from_DB(self):

        count = ((int(DBInterface.get_all_rows('URL_Collection')) - int(DBInterface.count_unprocessed_URLs()))+1)

        #print(count)
        print('Unprocessed URLS ' + str(int(DBInterface.count_unprocessed_URLs())))

        for i in range(int(DBInterface.count_unprocessed_URLs())):
            x = NewsItem(DBInterface.get_urls(count), DBInterface.fake_or_real(count))
            print(x.get_features_list())
            DBInterface.add_features(x)
            #print('{0}\r'.format('On article ' + str(count)))
            count = count + 1
        self.read_data_from_DB()

    def normalise(self, data):


        data_scaler = preprocessing.MinMaxScaler(feature_range = (0, 1))
        data_scaled = data_scaler.fit_transform(data)
        #print('Scaling Data....' + str(data_scaled))
        dataset = preprocessing.normalize(data_scaled, norm='l1')
        return dataset

    def __generate_Dataset(self):
        data = self.normalise(self.__non_normalised_dataset)
        self.predicted_value = data[-1]
        data = np.delete(data, data[-1], 0)
        #plt = scatter_matrix(data)
        #plt.show()
        self.train_and_test_Data(0.7, data)# Only for spefic testing
        return data

    def train_and_test_Data(self, split, dataset):

        self.XtrainingSet = []
        self.YtrainingSet = []

        self.XtestSet = []
        self.YtestSet = []
        count = 0
        while count < len(dataset):
            if random.random() < split:
                self.XtrainingSet.append(dataset[count])

                self.YtrainingSet.append(self.__labels[count])

            else:
                self.XtestSet.append(dataset[count])
                self.YtestSet.append(self.__labels[count])

            count = count + 1
        print("Training set contains " + str(len(self.XtrainingSet)))
        fakevalues = 0
        for x in self.YtrainingSet:
            if x == 0:
                fakevalues = fakevalues+1
        print('of those values ' + str(fakevalues) + ' are fake' '\n')
        print("Test set contains " + str(len(self.XtestSet)))
        fakevalues = 0
        for x in self.YtestSet:
            if x == 0:
                fakevalues = fakevalues + 1
        print('of those values ' + str(fakevalues) + ' are fake' '\n')
        self.__model.fit(np.array(self.XtrainingSet), self.YtrainingSet)
        y_pred = self.__model.predict(np.array(self.XtestSet))

        self.Accuracy = np.mean(y_pred == self.YtestSet)
        print('With an Accuracy score:' "{:.2f}".format(self.Accuracy))



    def predict(self, n:NewsItem):
        values = n.get_features_list()
        print(values)
        self.__non_normalised_dataset.append(values)
        self.__generate_Dataset()
        return self.__model.predict(self.predicted_value.reshape(1, -1))


    def run_prediction(self):
        url = input('What article would you like to check?')
        url = (url[:-1])

        #if str('www.' +urlparse(url).netloc) != DBInterface.get_domains(2):
        found = False
        for x in range(DBInterface.get_all_rows('Domains')):
            x = x+1
            if str(DBInterface.get_domains(x)) in url:
                found = True

        if found:
            print("That website IS in my database")
            n = NewsItem(url, ' ')
            predict = self.predict(n)
            if predict == [0]:
                print('\n')
                print('The model predicts that the article is classified as fake')
                print('\n')

                yesORno = input('Is that Correct? Y/N')
                if yesORno.upper() == 'N':
                    DBInterface.add_new_news_source(url, 0)
                else:
                    self.run_prediction()


            else:
                print('The model predicts that the article is classified as real')
                print('\n')
                yesORno = input('Is that Correct? Y/N')
                if yesORno.upper() == 'Y':
                    DBInterface.add_new_news_source(url, 1)
                else:
                    self.run_prediction()

        else:
            print("That website is NOT in my database. Please try again!")
            self.run_prediction()



dataset = NewsItemDataset()
dataset.run_prediction()



