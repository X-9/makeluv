import feedparser

class GrooveUser(object):
	
	def __init__(self, user, last_sync):
		self.user = user
		self.last_sync = last_sync

		url = "http://api.grooveshark.com/feeds/1.0/users/" + \
	   		  "%s/recent_favorite_songs.rss" % (self.user)
		feed = feedparser.parse(url)
		self.__tracks = list()
	 	for entry in feed.entries:
			self.__tracks.append(self.__track(entry.title))


	def __track(self, str):
		a = str.split("-")
		return { "artist" : a[0], "title" : a[1] }

	def get_tracks(self):
		return self.__tracks

	def set_tracks(self, value):
		print "read only"

	tracks = property(get_tracks, set_tracks)


class LastFm(object):
	API_URL = "http://ws.audioscrobbler.com/2.0/"

	def __init__(self, user, session_key):
		self.user = user
		self.session_key = session_key

	def sign(self, params):
		request = u''.join(["%s%s" % (key, params[key] \
							for key in sorted(params)])
		return md5("%s%s" % (request, self.secret)).hexdigest()

def main():
	gu = GrooveUser("testuser", "haha")
	for entry in gu.tracks:
		print entry


if __name__ == "__main__":
	main()

