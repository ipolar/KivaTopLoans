#!/usr/bin/python
#
# Calcualte the time taken for a loan to get funded, and dump this into the DB
#
# Version:	0.1
# Author:	Andy Lyon
# Date:		19-05-2011
#

import time
import re
import MySQLdb
import datetime

print "\n*************************"
print "* Kiva Funded Time Taken *"
print "* Author: Andy Lyon      *"
print "* Version: 0.1           *"
print "***************************\n\n"

# DB settings
db_user = 'python_kiva'
db_password = 'python_kiva'
db_name = 'python_kiva'

#
# Entry point
#
if __name__ == "__main__":
	
	# Connect to the DB
	db = MySQLdb.connect(user=db_user, passwd=db_password, db=db_name)
	db_cursor = db.cursor()
	
	print 'Getting data....'
	
	# Grab the current loans stored in the DB we're looking at....
	db_cursor.execute("""SELECT kiva_id FROM tbl_scraped_loans WHERE time_taken_to_fund = '' AND kiva_status = 'funded' AND kiva_id != ''""")
	
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
		
		# Get the start time...
		db_cursor.execute("""SELECT scraped_loans_date_scraped FROM tbl_scraped_loans WHERE kiva_id = (%s)""", (id))
		started_row = db_cursor.fetchone()
		
		# Get the funded time...
		db_cursor.execute("""SELECT scraped_loans_funded FROM tbl_scraped_loans WHERE kiva_id = (%s)""", (id))
		funded_row = db_cursor.fetchone()
		
		# Convert our datetimes into timestamps so we can calculate the time diff in secs
		start_ts = time.mktime(started_row[0].timetuple())
		end_ts = time.mktime(funded_row[0].timetuple())
		diff = round(end_ts-start_ts)
		
		print 'Secs it took to get funded: ', str(diff)
		
		db_cursor.execute("""UPDATE tbl_scraped_loans SET time_taken_to_fund = %s WHERE kiva_id = %s """, (diff, id))
		
		print "done!\n\n"