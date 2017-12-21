# SQL-on-the-fly
Allow users perform SQL over csv dataset without putting it into SQL database.

## Run the program:
1. Put all the .csv files in to the SQL-on-the-file/ folder.

2. Create a new folder index/ and a new folder row_references/.

3. Change the 'flist' and 'nlist' in index.py to the .csv files you use. Run index.py to create all the index files into the index/ folder.
```
python index.py
```

4. Change the 'flist' and 'nlist' in disk.py to the .csv files you use. Run disk.py to create all the row reference files into the row_reference/ folder.
```
python disk.py
```

5. Start the program and load the index files.
```
python myproject.py
USE review-1m
USE business
USE checkin
USE photos
```

6. Run the queries. The program will take a query statement and output the result and query time to the console. Some sample queries are listed below.

7. Exit the program.
```
exit
```

## Sample queries:
1. SELECT * FROM photos

  Time: 0.332295894623 seconds

2. SELECT DISTINCT stars FROM review-1m

  Time: 0.00784993171692 seconds

3. SELECT review_id, stars, useful FROM review-1m WHERE stars >= 4 AND useful > 20

  Time: 0.159142017365 seconds

4. SELECT review_id, stars, useful FROM review-1m WHERE useful > 20 AND stars >= 4 - 1

  Time: 0.315785884857 seconds

5. SELECT review_id, stars, useful FROM review-1m WHERE useful > 10 AND (useful < 20 OR stars >= 4)

  Time: 0.27635383606 seconds

6. SELECT B\__city, B\__state, R\__business_id, R\__stars, R\__useful FROM business B, review-1m R WHERE B\__city LIKE "Champaign" AND B\__state LIKE "IL" AND B\__business_id = R\__business_id

  Time: 0.251272916794 seconds

7. SELECT DISTINCT B\__name FROM business B, review-1m R, photos P WHERE B\__city = Champaign AND B\__state = IL AND P\__label = inside AND R\__stars = 5 AND B\__business_id = P\__business_id AND B\__business_id = R\__business_id

  Time: 6.03912496567 seconds

  SELECT DISTINCT B\__name FROM business B, review-1m R, photos P WHERE B\__city = Champaign AND B\__state = IL AND P\__label = inside AND B\__business_id = P\__business_id AND B\__business_id = R\__business_id AND R\__stars = '5'

  Time: 0.423269033432 seconds
