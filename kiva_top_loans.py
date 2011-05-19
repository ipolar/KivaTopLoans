#!/usr/bin/python
#
# Grab the 20 newest loans from the Kiva API (in JSON format)
#
# Version:	0.2
# Author:	Andy Lyon
# Date:		19-05-2011
#

import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
import time
import re
import random
import MySQLdb
import datetime
import simplejson
import iso8601

print "\n**************************"
print "* Kiva Latest 20 Loans   *"
print "* Author: Andy Lyon      *"
print "* Version: 0.2           *"
print "**************************\n\n"

# Scrape URL
newest_loans_url = "http://api.kivaws.org/v1/loans/newest.json"
app_id = "?app_id=<YOUR_APP_ID_HERE>"

# Proxy settings, leave proxy_url blank if you don't want to use it
proxy_url = ""

# HTTP header settings.
user_agent_array = []
user_agent_array.append('Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)')
user_agent_array.append('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
user_agent_array.append('Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0 )')
user_agent_array.append('Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90)')
user_agent_array.append('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1')
user_agent_array.append('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
user_agent_array.append('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.29 Safari/525.13')
user_agent_array.append('Mozilla/4.8 [en] (Windows NT 6.0; U)')
user_agent_array.append('Mozilla/4.8 [en] (Windows NT 5.1; U)')
user_agent_array.append('Opera/9.25 (Windows NT 6.0; U; en)')
user_agent_array.append('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; en) Opera 8.0')
user_agent_array.append('Opera/7.51 (Windows NT 5.1; U) [en]')
user_agent_array.append('Opera/7.50 (Windows XP; U)')
user_agent_array.append('Avant Browser/1.2.789rel1 (http://www.avantbrowser.com)')
user_agent_array.append('Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.4) Gecko Netscape/7.1 (ax)')
user_agent_array.append('Mozilla/5.0 (Windows; U; Windows XP) Gecko MultiZilla/1.6.1.0a')
user_agent_array.append('Opera/7.50 (Windows ME; U) [en]')
user_agent_array.append('Mozilla/3.01Gold (Win95; I)')
user_agent_array.append('Mozilla/2.02E (Win95; U)')
user_agent_array.append('Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/125.2 (KHTML, like Gecko) Safari/125.8')
user_agent_array.append('Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/125.2 (KHTML, like Gecko) Safari/85.8')
user_agent_array.append('Mozilla/4.0 (compatible; MSIE 5.15; Mac_PowerPC)')
user_agent_array.append('Mozilla/5.0 (Macintosh; U; PPC Mac OS X Mach-O; en-US; rv:1.7a) Gecko/20050614 Firefox/0.9.0+')
user_agent_array.append('Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-US) AppleWebKit/125.4 (KHTML, like Gecko, Safari) OmniWeb/v563.15')
txdata = None
txheaders = {
	'User-Agent': user_agent_array[random.randint(0, len(user_agent_array)-1)],
	'Accept-Language': 'en-us',
	'Accept-Encoding': 'gzip, deflate, compress;q=0.9',
	'Keep-Alive': '300',
	'Connection': 'keep-alive',
	'Cache-Control': 'max-age=0',
}

# DB settings
db_user = 'python_kiva'
db_password = 'python_kiva'
db_name = 'python_kiva'

#
# Generate headers for a request
#
def genHeaders():
	new_header = {
		'User-Agent': user_agent_array[random.randint(0, len(user_agent_array)-1)],
		'Accept-Language': 'en-us',
		'Accept-Encoding': 'gzip, deflate, compress;q=0.9',
		'Keep-Alive': '300',
		'Connection': 'keep-alive',
		'Cache-Control': 'max-age=0',
	}
	return new_header

#
# Get the source code from the web page
#
def fetchSourceProxy(url, proxy):
	if proxy != '':
		print 'Using proxy: ', proxy
		proxy = urllib2.ProxyHandler({'http': proxy})
		opener = urllib2.build_opener(proxy)
		urllib2.install_opener(opener)
	else:
		print 'No proxy in use...'
	
	# Build URL
	url = '%s%s' % (url, app_id)
	print 'Request URL is: ', url
	
	# Generate a new, random header
	txheaders = genHeaders()
	req = urllib2.Request(url, txdata, txheaders)
	response = urllib2.urlopen(req)
	source = response.read()
	return source

#
# Entry point
#
if __name__ == "__main__":
	
	# Connect to the DB
	db = MySQLdb.connect(user=db_user, passwd=db_password, db=db_name)
	db_cursor = db.cursor()
	
	# Get the current datetime
	date_now = datetime.datetime.now()
	mysql_timestamp_now = date_now.strftime("%Y-%m-%d %H:%M:%S")
	
	# At this point, create a new row in our MySQL DB, entering the current datetime
	db_cursor.execute("""INSERT INTO tbl_log (http_request_datetime) VALUES (%s)""", (mysql_timestamp_now))
	insert_id = db_cursor.lastrowid
	
	print 'Current datetime:', str(mysql_timestamp_now)
	
	# Try and grab the URL source. If we get a standard 4xx, 5xx HTTP error or a URL error let us know.
	try:
		source = fetchSourceProxy(newest_loans_url, '')
	
	except HTTPError, e:
		print 'The server couldn\'t fulfill the request.'
		print 'Error code: ', e.code
		
		# We have an error, update this row in the DB with the error code
		db_cursor.execute("""UPDATE tbl_log SET http_error_code = %s WHERE log_id = %s """, (e.code, insert_id))
	
	except URLError, e:
		print 'We failed to reach a server.'
		print 'Reason: ', e.reason
		
		# We have an error, update this row in the DB with the error code
		db_cursor.execute("""UPDATE tbl_log SET url_error_reason = %s WHERE log_id = %s """, (e.reason, insert_id))
	
	else:
		# No errors returned, we should have some JSON!
		# Woohoo, we have a successful request! Now update this systemkey row in the DB with a timestamp
		# Get the current datetime timestamp
		now = datetime.datetime.now()
		mysql_timestamp_now = now.strftime("%Y-%m-%d %H:%M:%S")
		db_cursor.execute("""UPDATE tbl_log SET http_request_success_datetime = %s WHERE log_id = %s """, (mysql_timestamp_now, insert_id))
		
		#Parse, and store these intial values in the DB:
		#	<id>287772</id>
		#	<status>fundraising</status>
		#	<loan_amount>900</loan_amount>
		#	<funded_amount>75</funded_amount>
		#	<basket_amount>0</basket_amount>
		#	<posted_date>2011-04-05T08:40:01Z</posted_date>
		
		#print source
		
		pydata = simplejson.loads(source)
		
		for r in pydata['loans']:
			
			# Now update this row with all the data from the JSON feed..
			#	kiva_id
			#	kiva_status
			#	kiva_loan_amount
			#	kiva_funded_amount
			#	kiva_basket_amount
			#	kiva_posted_date - e.g. <posted_date>2011-04-05T11:20:02Z</posted_date>
			#	log_id
			
			# Convert the ISO 8601 timestamp from Kiva & do the insert into the DB
			kiva_posted_date = iso8601.parse_date(r['posted_date'])
			kiva_posted_date = kiva_posted_date.strftime("%Y-%m-%d %H:%M:%S")
			
			# Get the current datetime timestamp
			now = datetime.datetime.now()
			mysql_timestamp_now = now.strftime("%Y-%m-%d %H:%M:%S")
			
			# Now insert a new row..
			try:
				db_cursor.execute("""INSERT INTO tbl_scraped_loans (scraped_loans_date_scraped, kiva_id, kiva_loan_amount, kiva_status, kiva_funded_amount, kiva_basket_amount, kiva_posted_date, log_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (mysql_timestamp_now, r['id'], r['loan_amount'], r['status'], r['funded_amount'], r['basket_amount'], kiva_posted_date, insert_id))
			
			except MySQLdb.IntegrityError, message:
				print "error!"
		
		print "done!"