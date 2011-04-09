import time
import ConfigParser
import _mysql
from datetime import datetime
from grooveuser import GrooveUser
from lastfm import LastFm


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

