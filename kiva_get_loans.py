#!/usr/bin/python
#
# Qeries any Kiva loans in the DB and grabs their current loan stats via the Kiva API (in JSON format)
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
print "* Get Kiva Loans         *"
print "* Author: Andy Lyon      *"
print "* Version: 0.2           *"
print "************************\n\n"

# Scrape URL
loans_url = "http://api.kivaws.org/v1/loans/"
app_id = "?app_id=com.bluefroglondon"

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
def fetchSourceProxy(url, loans_id, proxy):
	if proxy != '':
		print 'Using proxy: ', proxy
		proxy = urllib2.ProxyHandler({'http': proxy})
		opener = urllib2.build_opener(proxy)
		urllib2.install_opener(opener)
	else:
		print 'No proxy in use...'
	
	# Build URL
	url = '%s%s%s%s' % (url, loans_id, '.json', app_id)
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
	
	# Grab the current loans stored in the DB we're looking at....
	db_cursor.execute("""SELECT kiva_id FROM tbl_scraped_loans WHERE scraped_loans_funded = '0000-00-00 00:00:00' AND kiva_id != ''""")
	
	# Loop through all the current loans from the DB...
	my_data_set = db_cursor.fetchall()
	
	# Convert from long int and tuple into ints as a list
	# http://stackoverflow.com/questions/2432402/python-lits-containg-tuples-and-long-int
	my_data_set = [int(e[0]) for e in my_data_set]
	
	for id in my_data_set:
		
		# Get the current datetime
		date_now = datetime.datetime.now()
		mysql_timestamp_now = date_now.strftime("%Y-%m-%d %H:%M:%S")
		
		print 'Current datetime:', str(mysql_timestamp_now)
		print 'Current ID:', str(id)
		
		# Insert a request row into the tbl_scraped_loans_items table...
		db_cursor.execute("""INSERT INTO tbl_scraped_loans_items (http_request_datetime, kiva_id) VALUES (%s, %s)""", (mysql_timestamp_now, id))
		loans_items_insert_id = db_cursor.lastrowid
		
		# Try and grab the URL source. If we get a standard 4xx, 5xx HTTP error or a URL error let us know.
		try:
			source = fetchSourceProxy(loans_url, id, '')
		
		except HTTPError, e:
			print 'The server couldn\'t fulfill the request.'
			print 'Error code: ', e.code
			
			# We have an error, update this row in the DB with the error code
			db_cursor.execute("""UPDATE tbl_scraped_loans_items SET http_error_code = %s WHERE scraped_loans_items_id = %s """, (e.code, loans_items_insert_id))
		
		except URLError, e:
			print 'We failed to reach a server.'
			print 'Reason: ', e.reason
			
			# We have an error, update this row in the DB with the error code
			db_cursor.execute("""UPDATE tbl_scraped_loans_items SET url_error_reason = %s WHERE scraped_loans_items_id = %s """, (e.reason, loans_items_insert_id))
		
		else:
			# No errors returned, we should have some JSON!
			# Woohoo, we have a successful request! Now update this systemkey row in the DB with a timestamp
			# Get the current datetime timestamp
			now = datetime.datetime.now()
			mysql_timestamp_now = now.strftime("%Y-%m-%d %H:%M:%S")
			db_cursor.execute("""UPDATE tbl_scraped_loans_items SET http_request_success_datetime = %s WHERE scraped_loans_items_id = %s """, (mysql_timestamp_now, loans_items_insert_id))
			
			#print source
			
			pydata = simplejson.loads(source)
			
			for r in pydata['loans']:
				
				# Now update this row with all the data from the JSON feed for this specific loan
				#	kiva_id
				#	kiva_status
				#	kiva_funded_amount
				#	kiva_basket_amount
				
				# Get the current datetime timestamp
				now = datetime.datetime.now()
				mysql_timestamp_now = now.strftime("%Y-%m-%d %H:%M:%S")
				
				if (r['status'] == 'funded' or r['status'] == 'in_repayment' or r['status'] == 'paid' or r['status'] == 'defaulted' or r['status'] == 'refunded'):
					# This loan is now funded! So set our funded timestamp...
					db_cursor.execute("""UPDATE tbl_scraped_loans_items SET kiva_id = %s, kiva_status = %s, kiva_funded_amount = %s, kiva_basket_amount = %s WHERE scraped_loans_items_id = %s """, (r['id'], r['status'], r['funded_amount'], 0, loans_items_insert_id))
					db_cursor.execute("""UPDATE tbl_scraped_loans SET scraped_loans_funded = %s, kiva_status = %s WHERE kiva_id = %s """, (mysql_timestamp_now, r['status'], r['id']))
				else:
					db_cursor.execute("""UPDATE tbl_scraped_loans_items SET kiva_id = %s, kiva_status = %s, kiva_funded_amount = %s, kiva_basket_amount = %s WHERE scraped_loans_items_id = %s """, (r['id'], r['status'], r['funded_amount'], r['basket_amount'], loans_items_insert_id))
			
			print "done!"