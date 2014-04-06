import os, re
import webapp2
import jinja2
from google.appengine.ext import db
from bestword import getBestWord
import logging

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)
'''
Takes in string; rtns True if valid url, else False
'''
def isValidUrl(s):
	pat = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
	if re.match(pat, s) is not None:
		return True
	else:
		return False	 
def consonants(s):
	amended_s = ""
	for c in s:
		if c not in "aeiou":
			amended_s += c
	return amended_s
		
def compute(s):
	logging.info("see this mesg in the console!")
	limit = 10 # max length of our shorturl path
	custompath = ""
	bestwordslist = getBestWord(s) # gets a list of 5 most-representative words of the input webpage
	if len(bestwordslist) == 0: #validurl that goes to blank page
		return "blankwebpg"
	for wrd in bestwordslist:
		if len(wrd) >= 5:
			wrd = consonants(wrd)
		if limit - len(wrd) >= 0: # crams in as many words as it can in the 10-char-limit. 
			custompath += wrd
			limit -= len(wrd) 
		else:
			break
	return custompath

class URLMap(db.Model):
	longURL = db.StringProperty(required=True)
	shortURL = db.StringProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)

class InputPage(webapp2.RequestHandler):
	'''
	takes in an html pg (with vars) + a dict (var:value), and renders the page
	(plugs in values)
	'''
	def renderwrite(self, template, params={}):
		 templet = jinja_env.get_template(template)
		 self.response.write(templet.render(params))
	'''
	You need a func for every http request-type you use.
	Handling a GET request is the bare minimum you should have. 
	'''	 
	def get(self): 
		self.renderwrite('front.html')
		
	def post(self):
		inpurl = self.request.get('inpurl')	
		if isValidUrl(inpurl):
			result = compute(inpurl) # shorturl
			# if shortURL is not already in the the database table, then add it. 
			if (db.GqlQuery("select * from URLMap where shortURL = :something", something=result).get()) is None:
				a = URLMap(longURL=inpurl, shortURL=result) # creates the db object URLMap
				a.put() # puts the data in the object in the URLMap entity (table)		
			self.renderwrite('processed.html', {'shorty': 'http://huffyrc.appspot.com/'+result})
		else:
			# display page again, but with error mesg
			self.renderwrite('front.html', {'inperr':"That's an invalid url, enter again!", 'inpval':inpurl})

class URLRequestPage(webapp2.RequestHandler):
	def renderwrite(self, template, params={}):
		templet = jinja_env.get_template(template)
		self.response.write(templet.render(params))
		 
	def get(self, shorturl):
		#.get() rtns the first result of query or None
		res = db.GqlQuery("select longURL from URLMap where shortURL = :something", something = shorturl).get()
		self.redirect(str(res.longURL))
	

app = webapp2.WSGIApplication([('/', InputPage), #handling the home page
							   (r'/(\w+)' , URLRequestPage)
								], debug=True)
