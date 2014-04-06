from bs4 import BeautifulSoup, Comment
import urllib2
import re
import math
from operator import itemgetter
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
'''
Explanation of the above 3 lines:
Unicode is a superset of ASCII, able to represent many more special characters,
especially from non-English languages. 
The data you get from a webpage may have these characters, but Python2.7 by
default uses ASCII to represent string data so rather than convert manually where
we have data, above, I've told the environment to simply set the default encoding to UTF-8 (a character
set for Unicode). Python3 uses UTF-8 by default.
'''
#Taken from nltk.corpus.stopwords.words('english')
stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you','your', 'yours', 'yourself', 
 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 
 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 
 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 
 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 
 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 
 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
  'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
   'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
    'can', 'will', 'just', 'don', 'should', 'now']

''' Strips out punctuation in our data, so for eg. "data," is not taken to be a word, 
(which would create problems) but "data" is. 
'''
def replace_punc(s):
	final = ""
	for c in s:
		if c not in """ !"#$%&'()*+,./:;<=>?@[\]^{|}~: """ :
			final += c
		else:
			final += ' '
	return final
    

'''
Takes in a url; rtns a list of five words. We accomodate as many
as we can, within 10 characters. Which is probably just 1 or 2, 
but just in case it is not. 
'''
def getBestWord(url):
	data =  urllib2.urlopen(url).read()
	soup = BeautifulSoup(data)
	# extracting (removing) comments - we only want the article text in the page, not metadata. 
	comments = soup.findAll(text=lambda text:isinstance(text, Comment))
	[comment.extract() for comment in comments]
	'''The above 2 lines have a decidedly odd syntax (it looks like extract() is a custom-
	-generated / lambda function), but rest assured it strips all
	comments out of soup. Test it out yourself. '''
	# removing all script and style tags
	for elem in soup.findAll(['script', 'style']):
		elem.extract()
	# Now that all comments, script and style text is removed...
	allthetext_withpunc = ''.join(soup.findAll(text=True))
	allthetext = replace_punc(str(allthetext_withpunc))
	# create and populating a hashtable to keep word count
	freqD = {}
	for wrd in allthetext.split():
		if wrd.lower() not in stopwords:
			freqD[wrd] = freqD.get(wrd, 0) +1
	# return the top five results
	results = sorted(freqD.items(), key=itemgetter(1), reverse=True) # sort the dict
	return [key for (key, val) in results[:5]] # rtn only the word, not it's count
	
#test url: http://www.cnet.com/news/12000-miles-in-an-electric-vehicle-or-bust/	
