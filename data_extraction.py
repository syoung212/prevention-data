import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
import getpass
# %matplotlib inline
plt.style.use('ggplot') 

user = 'postgres'
host = 'localhost'
dbname = 'mimic'
schema = 'mimiciii_demo'

con = psycopg2.connect(dbname=dbname, user=user, host=host, 
                       password=getpass.getpass(prompt='Password:'.format(user)))
cur = con.cursor()
cur.execute('SET search_path to {}'.format(schema))

query = \
"""
SELECT i.subject_id, i.hadm_id, i.los
FROM icustays i;
"""

data = pd.read_sql_query(query,con)

data.head()