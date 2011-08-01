from rapleafApi import RapleafApi
import urllib, json, sys
import pprint
from time import sleep

""" 
Class is used to calculate average distance between e-mail address
owners which is going to visit some conference with help of Google Distance Matrix API
"""
class BestConferenceLocation(object):
	google_distance = "http://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&sensor=false"
	api = RapleafApi.RapleafApi('876da98701b33ce751e369a7ae647a95')
	# restriction of Google Matrix Distance API
	QUERIES_AT_ONCE = 10

	def __init__(self, emails_file_name):
		""" emails_file_name  - file name with emails list (one per line) """
		self.emails = emails_file_name
		self.answers = []

	def __query_emails(self):
		if len(self.answers):
			return None
		with open(self.emails) as f:
			for i in f.readlines():
				result = self.api.query_by_email(i)
				self.answers.append(result)

	def match(self, dest_file_name):
		""" dest_file_name - file name with list of destinations (one per line) 
			Return value: tuple of 2 elements, where first element is best place's name
						  and second element is average distance from participants
		"""
		self.__query_emails()		
		min_avg_name = ''
		min_avg_dis = sys.float_info.max
		last_idx, total = 0, 0
		dest_str, origin_str = '', ''
		distances = {}		
		
		with open(dest_file_name) as f:
			dest_str = ''.join([i.strip() + '|' for i in f.readlines()])

	
		while last_idx < len(self.answers):
			for idx in xrange(last_idx, len(self.answers)):			
				try:
					last_idx += 1					
					origin_str += self.answers[idx]['country'] + ',' + self.answers[idx]['city'] + '|'
					total += 1
					if last_idx >= self.QUERIES_AT_ONCE - 1: 
						break
				except KeyError, e:
					pass
			print last_idx, total

			google_response = urllib.urlopen(self.google_distance % (origin_str, dest_str))
			self.origin_str = ''
			json_response = json.loads(google_response.read())
			pprint.pprint(json_response)

			for i in xrange(len(json_response['destination_addresses'])):			
				for k in xrange(len(json_response['origin_addresses'])):
					if json_response['rows'][k]['elements'][i]['status'] == 'OK':
					 	dist = float(json_response['rows'][k]['elements'][i]['distance']['value']) / 1000.0
						if distances.has_key(json_response['destination_addresses'][i]):
							distances[json_response['destination_addresses'][i]] += dist	
						else:
							distances[json_response['destination_addresses'][i]] = dist
			print distances
			sleep(10) # Google Matrix API's restriction -- no more than 100 queries per 10 seconds


		for i in distances.iterkeys():
			avg_dis = distances[i] / total
			if avg_dis < min_avg_dis:
				min_avg_dis = avg_dis
				min_avg_name = i
		return (min_avg_name, min_avg_dis)

if __name__ == '__main__':
	if len(sys.argv) < 3:
		sys.exit(-1)

	bc = BestConferenceLocation(sys.argv[1])
	result = bc.match(sys.argv[2])
	print "Best location for conference is %s, average distance is %f kms" % (result[0], result[1])
