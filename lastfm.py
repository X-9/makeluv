import urllib
from hashlib import md5

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
