#!/usr/bin/python
#
# Grab the 20 newest loans from the Kiva API
# This grabs them in JSON format...
#
# Version: 	0.1
# Author:	Andy Lyon
# Date: 	05-04-2011
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

print "\n************************"
print "* Kiva Latest 20 Loans *"
print "* Version: 0.1         *"
print "* Author: Andy Lyon    *"
print "************************\n\n"

# API URL
newest_loans_url = "http://api.kivaws.org/v1/loans/newest.json"

# App ID
app_id = "?app_id=<YOUR_APP_ID_HERE>"

# Proxy settings, leave proxy_url blank if you don't need it
proxy_url = ""
data = None

# DB settings
db_user = 'kiva_test'
db_password = 'kiva_test'
db_name = 'kiva_test'

#
# Generate header for the request
#
def get_header():
	new_header = {
		'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
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
def get_url(url, proxy):
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
	
	# Generate header
	header = get_header()
	request = urllib2.Request(url, data, header)
	response = urllib2.urlopen(request)
	source = response.read()
	return source

#
# Main function
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
		source = get_url(newest_loans_url, '')
	
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
		# Get the current datetime and update the DB
		now = datetime.datetime.now()
		mysql_timestamp_now = now.strftime("%Y-%m-%d %H:%M:%S")
		db_cursor.execute("""UPDATE tbl_log SET http_request_success_datetime = %s WHERE log_id = %s """, (mysql_timestamp_now, insert_id))
		
		# Parse, and store these intial values in the DB:
		#	<id>287772</id>
		#	<status>fundraising</status>
		#	<loan_amount>900</loan_amount>
		#	<funded_amount>75</funded_amount>
		#	<basket_amount>0</basket_amount>
		#	<posted_date>2011-04-05T08:40:01Z</posted_date>
		
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
			
			# Get the current datetime
			now = datetime.datetime.now()
			mysql_timestamp_now = now.strftime("%Y-%m-%d %H:%M:%S")
			
			# Now insert a new row..
			try:
				db_cursor.execute("""INSERT INTO tbl_scraped_loans (scraped_loans_date_scraped, kiva_id, kiva_loan_amount, kiva_status, kiva_funded_amount, kiva_basket_amount, kiva_posted_date, log_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (mysql_timestamp_now, r['id'], r['loan_amount'], r['status'], r['funded_amount'], r['basket_amount'], kiva_posted_date, insert_id))
			
			except MySQLdb.IntegrityError, message:
				print "error!"
		
		print "done!"