import feedparser

class GrooveUser(object):
	
	def __init__(self, user, last_sync):
		self.user = user
		self.last_sync = last_sync

		url = "http://api.grooveshark.com/feeds/1.0/users/" + \
	   		  "%s/recent_favorite_songs.rss" % (self.user)
		feed = feedparser.parse(url)
		self.__tracks = list()
		self.__tracks.append([self.__track(entry.title) \
								for entry in feed.entries])
		print self.tracks

	def __track(self, str):
		a = str.split("-")
		return { "artist" : a[0], "title" : a[1] }

	def get_tracks(self):
		return self.__tracks

	def set_tracks(self, value):
		print "read only"

	tracks = property(get_tracks, set_tracks)


def main():
	gu = GrooveUser("testuser", "haha")

if __name__ == "__main__":
	main()

