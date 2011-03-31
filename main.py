import feedparser
import ConfigParser
import _mysql
import urllib
from hashlib import md5


class GrooveUser(object):
	
	def __init__(self, user, last_sync):
		self.user = user
		self.last_sync = last_sync
		print user, last_sync

		url = "http://api.grooveshark.com/feeds/1.0/users/" + \
	   		  "%s/recent_favorite_songs.rss" % (self.user)
		feed = feedparser.parse(url)
		self.__tracks = list()
	 	for entry in feed.entries:
			self.__tracks.append(self.__track(entry.title))


	def __track(self, str):
		a = str.split("-")
		return { "artist" : a[0].strip(), \
				 "title" : a[1].strip() }

	def get_tracks(self):
		return self.__tracks

	def set_tracks(self, value):
		print "read only"

	tracks = property(get_tracks, set_tracks)


class LastFm(object):
	API_URL = "http://ws.audioscrobbler.com/2.0/"

	def __init__(self, user, session_key, api):
		self.user = user
		self.session_key = session_key
		self.api = api

	def sign(self, params):
		print params
		request = u''.join(['%s%s' % (key, params[key]) \
							for key in sorted(params)])
		request += self.api['secret']
		print type(request)
		return md5(request.encode('utf-8', 'replace')).hexdigest()

	def luv_track(self, artist, title):
		params = { 'method' : 'track.love',
				   'track' : title,
				   'artist' : artist,
				   'api_key' : self.api['key'],
				   'sk' : self.session_key }
		params['api_sig'] = self.sign(params)
		p = dict()
		for key in params:
			p[key.encode('utf-8')] = params[key].encode('utf-8')

		encode = urllib.urlencode(p)
		print encode
		f = urllib.urlopen(self.API_URL, encode)
		print f.read()


class Runner(object):
	TABLE = 'luvluvluv'
	
	def __init__(self, config_file):
		cp = ConfigParser.ConfigParser()
		cp.read(config_file)
		
		self.api = { 'key' : cp.get('application', 'api_key'),
					 'secret' : cp.get('application', 'secret') }

		self.db = { 'host' : cp.get('client', 'host'),
					'database' : cp.get('client', 'database'),
					'user' : cp.get('client', 'user'),
					'password' : cp.get('client', 'password') }
		self.__parse()
	
	def __parse(self):
		inst = _mysql.connect(host=self.db['host'],
							  db=self.db['database'],
							  user=self.db['user'],
							  passwd=self.db['password'])
		inst.query("SELECT * FROM `%s` LIMIT 0, 1000" % (self.TABLE))
		r = inst.store_result()
		row = r.fetch_row(maxrows=0, how=1)[1]
		gu = GrooveUser(row['grooveshark'], row['sync'])
		lu = LastFm(row['lastfm'], row['session'], self.api)
		for track in gu.tracks:
			lu.luv_track(track['artist'], track['title'])


def main():
	run = Runner('./config.ini')
	

if __name__ == "__main__":
	main()

