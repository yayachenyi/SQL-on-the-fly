# SQL-on-the-fly
Allow users perform SQL over csv dataset without putting it into SQL database.

1. Put all the .csv files in to the SQL-on-the-file/ folder.

2. Create a new folder index/.

3. Run index.py to create all the index files into the index/ folder. Change the 'flist' and 'nlist' in the index.py script to the .csv files.

3. Start the program and test the queries.
```
python myproject.py
USE review-1m
USE business
USE checkin
USE photos
```
