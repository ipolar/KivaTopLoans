# Kiva Top 20 loans

A Python script to grab the most recent 20 loans added to the Kiva.org site, and then stick them into a MySQL DB.
This queries the Kiva JSON API.


## Requirements

1) MySQLdb (http://mysql-python.sourceforge.net/)
2) SimpleJSON (http://pypi.python.org/pypi/simplejson/)
3) iso8601 (http://pypi.python.org/pypi/iso8601/)


## Usage

First off, the script needs some variables configured.

1) Don't forget to add in your APPI_ID to the top of the Python script. This isn't actually needed by the Kiva API, but helps them see whose doing what etc.
2) You'll need to add in your MySQL DB connection details.
3) If you need to connect via a proxy, add this in as well. Leave blank if not.

Once you've configured the above, you'll need to setup the DB structure. Check out the 'python_kiva.sql' file which you can import into a MySQL DB to setup the structure.

Once that's all done, fire off a 'python kiva_top_loans.py' and you're away!
