import feedparser
import time

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
		return { "artist"   : a[0].strip(),
				 "title"    : a[1].strip(),
				 "datetime" : datetime }
	
	def __strtotime(self, str):
		return time.strptime(str[:-6], "%a, %d %b %Y %H:%M:%S")

	def get_tracks(self):
		return self.__tracks

	def set_tracks(self, value):
		print "read only"

	tracks = property(get_tracks, set_tracks)
