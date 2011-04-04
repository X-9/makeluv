import feedparser
import ConfigParser
import _mysql
import urllib
import time
from datetime import datetime
from hashlib import md5


class GrooveUser(object):
	
	def __init__(self, user, last_sync):
		self.user = user
		self.last_sync = last_sync

		url = "http://api.grooveshark.com/feeds/1.0/users/\
				%s/recent_favorite_songs.rss" % (self.user)
		feed = feedparser.parse(url)
		self.__tracks = list()
	 	for entry in feed.entries:
			if self.__strtotime(self.last_sync) < entry.updated_parsed:
				self.__tracks.append(self.__track(entry.title,
												  entry.updated_parsed))
		print len(self.__tracks)

	def __track(self, str, datetime):
		a = str.split("-")
		return { "artist" 	: a[0].strip(),
				 "title" 	: a[1].strip(),
				 "datetime" : datetime }

	def __strtotime(self, str):
		return time.strptime(str[:-6], "%a, %d %b %Y %H:%M:%S")

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
		request = u''.join(['%s%s' % (key, params[key])
							for key in sorted(params)])
		request += self.api['secret']
		return md5(request.encode('utf-8', 'replace')).hexdigest()

	def luv_track(self, artist, title):
		params = { 'method' 	: 'track.love',
				   'track' 		: title,
				   'artist' 	: artist,
				   'api_key' 	: self.api['key'],
				   'sk' 		: self.session_key }
		params['api_sig'] = self.sign(params)
		
		# encode params structure
		p = dict()
		for key in params:
			p[key.encode('utf-8')] = params[key].encode('utf-8')

		# mark song as favourite
		encode = urllib.urlencode(p)
		f = urllib.urlopen(self.API_URL, encode)
		print f.read()


class Runner(object):
	TABLE = 'luvluvluv'
	
	def __init__(self, config_file):
		cp = ConfigParser.ConfigParser()
		cp.read(config_file)
		
		self.api = { 'key'		: cp.get('application', 'api_key'),
					 'secret' 	: cp.get('application', 'secret') }

		self.db  = { 'host' 	: cp.get('client', 'host'),
				 	 'database' : cp.get('client', 'database'),
					 'user' 	: cp.get('client', 'user'),
					 'password' : cp.get('client', 'password') }
		self.__parse()
	
	def __parse(self):
		inst = _mysql.connect(host=self.db['host'],
							  db=self.db['database'],
							  user=self.db['user'],
							  passwd=self.db['password'])
		inst.query("SELECT * FROM `%s` LIMIT 0, 1000" % (self.TABLE))
		r = inst.store_result()
		for row in r.fetch_row(maxrows=0, how=1):
			gu = GrooveUser(row['grooveshark'], row['sync'])
			lu = LastFm(row['lastfm'], row['session'], self.api)
			for track in gu.tracks:
				lu.luv_track(track['artist'], track['title'])
			del gu, lu

			# update last sync time
			last_sync = time.strftime("%a, %d %b %Y %H:%M:%S +0000",
									  time.gmtime())
			update_query =  "UPDATE `%s` SET sync='%s' \
							WHERE lastfm='%s' AND grooveshark='%s'" % \
					   		(self.TABLE,
							last_sync,
							row['lastfm'], 
							row['grooveshark'])
			inst.query(update_query)


def main():
	run = Runner('./config.ini')
	

if __name__ == "__main__":
	main()

