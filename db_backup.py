from __future__ import print_function
from OpenOversight.app import config
import os

#db = config['default'].SQLALCHEMY_DATABASE_URI
db = 'postgresql://openoversight:terriblepassword@localhost:5432/openoversight-prod'
os.system("/usr/bin/pg_dump %s -f backup.sql" % db)
print("backup.sql created")
