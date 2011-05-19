#!/usr/bin/python
#
# Create an ARFF file for use with Weka...
#
# Version:	0.1
# Author:	Andy Lyon
# Date:		19-05-2011
#

import time
import re
import MySQLdb
import datetime

print "\n***************************"
print "* Kiva Generate ARFF File *"
print "* Author: Andy Lyon       *"
print "* Version: 0.1            *"
print "***************************\n\n"

# DB settings
db_user = 'python_kiva'
db_password = 'python_kiva'
db_name = 'python_kiva'

#
# Replace chars in our strings
#
def replace_chars(rep_string):
	rep_string = rep_string.replace('&','')
	rep_string = rep_string.replace('/','')
	rep_string = rep_string.replace(' ','-')
	return rep_string

#
# Entry point
#
if __name__ == "__main__":
	
	# Connect to the DB
	db = MySQLdb.connect(user=db_user, passwd=db_password, db=db_name)
	db_cursor = db.cursor()
	
	print 'Getting data....'
	
	# Grab the data from the DB we need....
	db_cursor.execute("""SELECT loan_activity, loan_sector, loan_country_code, loan_gender, time_taken_to_fund FROM tbl_scraped_loans WHERE tbl_scraped_loans.kiva_status = 'funded' AND tbl_scraped_loans.kiva_funded_amount = 0""")
	
	# Loop through all the current loans from the DB...
	my_data_set = db_cursor.fetchall()
	
	print 'Building ARFF file...'
	
	# Get the current datetime
	date_now = datetime.datetime.now()
	file_timestamp_now = date_now.strftime("%Y-%m-%d_%H-%M-%S")
	
	# Initially set some empty arrays
	loan_activity = []
	loan_sector = []
	loan_country_code = []
	loan_gender = []
	
	for r in my_data_set:
		loan_activity.append((r[0]))
		loan_sector.append((r[1]))
		loan_country_code.append((r[2]))
		loan_gender.append((r[3]))
	
	# Build some strings!
	loan_activity_string = replace_chars("{%s}" % ','.join(set(loan_activity)))
	loan_sector_string = replace_chars("{%s}" % ','.join(set(loan_sector)))
	loan_country_code_string = replace_chars("{%s}" % ','.join(set(loan_country_code)))
	loan_gender_string = replace_chars("{%s}" % ','.join(set(loan_gender)))
	output_filename = 'kiva_'+file_timestamp_now+'.arff'
	
	with open(output_filename,"w") as fp:
		fp.write("@RELATION " + 'kiva_'+file_timestamp_now + "\n\n")
		fp.write("@ATTRIBUTE loan_activity " + loan_activity_string + "\n")
		fp.write("@ATTRIBUTE loan_sector " + loan_sector_string + "\n")
		fp.write("@ATTRIBUTE loan_country_code " + loan_country_code_string + "\n")
		fp.write("@ATTRIBUTE loan_gender " + loan_gender_string + "\n")
		fp.write("@ATTRIBUTE time_taken_to_fund numeric\n\n")
		fp.write("@DATA\n")
		
		for r in my_data_set:
			# Write out our data, this should be as per the ARFF format on...
			# http://weka.wikispaces.com/ARFF+%28book+version%29
			# E.g.
			# Cloth-Dressmaking-Supplies,Retail,TJ,F,1052127
			
			fp.write("%s,%s,%s,%s,%s\n" % (replace_chars(r[0]), replace_chars(r[1]), replace_chars(r[2]), replace_chars(r[3]), r[4]))
	
	print "done!"