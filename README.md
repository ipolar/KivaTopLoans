# Kiva Top Loans

A Python script to grab the most recent 20 loans added to the Kiva.org site, and then stick them into a MySQL DB. (This queries the Kiva JSON API)

Also, I've added the following scripts to capture more data over a timeframe and export it for some analysis!



### kiva_get_loans.py

This will query any loans you have stored from the kiva_top_loans.py script and store a snapshot of each loans current funding stage.
Once a loan has been funded, don't query this loan any more.


### kiva_data_cal_time_taken.py

This will look at all the current loans and see which ones are actually fully funded. It'll then calcualte the time taken for a loan to get funded, and dump this into the DB.


### kiva_data_get_loan_details.py

Initially I didn't log anything other than the Kiva ID of a loan, but since I want to start looking at a loans attributes, I needed a script to go back and query out some more info from the Kiva API. This script does that and logs it into the DB.
I should really amalgamate this into the main kiva_top_loans.py script....


### kiva_data_create_arff.py

One of the main reasons for adding in all of the above scripts was to get some attribute data ready to be exported for some datamining. This script gets the data out of the DB and writes it to an ARFF file, which is a format used by the Weka datamining software (http://www.cs.waikato.ac.nz/ml/weka/).



## Requirements

1. MySQLdb (http://mysql-python.sourceforge.net/)
2. SimpleJSON (http://pypi.python.org/pypi/simplejson/)
3. iso8601 (http://pypi.python.org/pypi/iso8601/)
4. Python-dateutil (http://pypi.python.org/pypi/python-dateutil/1.5)



## Usage

First off, the script needs some variables configured.

1. Don't forget to add in your APPI_ID to the top of each of the scraping Python scripts. This isn't actually needed by the Kiva API, but helps them see whose doing what etc.
2. You'll need to add in your MySQL DB connection details.
3. If you need to connect via a proxy, add this in as well. Leave blank if not.

Once you've configured the above, you'll need to setup the DB structure. Check out the 'python_kiva.sql' file which you can import into a MySQL DB to setup the structure.

Once the above is all done, follow this sequence of steps!

1. Fire off a 'python kiva_top_loans.py'. This will populate the DB with the inital 20 top loans on the Kiva.org site.
2. Fire off a 'python kiva_get_loans.py'. This will get the 20 loans from above and get their current status. You should query this as often as you want (within reason) to gather some data.
3. Once you have some loans that are funded in the DB, you can fire off a 'python kiva_data_get_loan_details.py' to get all the attributes for your loans. Also a 'python kiva_data_cal_time_taken.py' to calcualte the time any loans that have been funded have taken. Once you have a good number of funded loans (100+) then you can run 'python kiva_data_create_arff.py' to create your ARFF file ready to be imported into Weka.
4. Go and have a beer after all your hard work!
