# SQL-on-the-fly
Allow users perform SQL over csv dataset without putting it into SQL database.

## Run the program:
1. Put all the .csv files in to the SQL-on-the-fly/ folder.

2. Modify setup.sh to ensure you choose the correct python2.7 version according to your local environment

3. Make sure you have the newest version of all the Python packages listed in the requirements.txt

4. Change the 'flist' and 'nlist' in index.py to the .csv files you use.

5. Change the 'flist' and 'nlist' in disk.py to the .csv files you use.

6. Run setup.sh to create all supporting and indexing folders/files automatically.

```
./setup.sh
```

5. Start the program and you don't need to wait for anything.
```
python myproject.py
```

6. Run the queries. The program will take a query statement and output the result and query time to the console. Some sample queries are listed below.

7. Exit the program.
```
exit
```

## Query Instruction and Formatting
### SELECT basics

#### Single table
Use attribute of the csv file directly inside SELECT and WHERE clasure. For example:
```
SELECT review_id, stars, useful FROM review-1m WHERE useful > 20 AND stars >= 4
```
#### Multi table
Use the abbreviation of the Table and the attribute of the csv file along with a '\__' inside the query.
```
SELECT B\__city, B\__state, R\__business_id, R\__stars, R\__useful FROM business B, review-1m R WHERE B\__city LIKE "Champaign" AND B\__state LIKE "IL" AND B\__business_id = R\__business_id
```
### FROM basics
#### Single table
No abbreviation, just the name of the csv file (without '.csv'). For example:
```
FROM review-1m
```
#### Multi table
Must include abbreviation after the name of the csv file. For example:
```
FROM review-1m R1, review-1m R2
```
### WHERE basics
#### Single table
No quotation mark on string. For example:
```
SELECT review_id, stars, useful FROM review-1m WHERE useful > 20 AND stars >= 4 AND city = Champaign
```
#### Multi table
Join conditions go here. Conditions order matter. Please use your domain knowledge to manipulate the order.
Attribtue must along with there name. For example:
```
WHERE B__city = Urbana
```
LIKE operation must be warpped into a quotation mark. For example:
```
SELECT B\__city, B\__state, R\__business_id, R\__stars, R\__useful FROM business B, review-1m R WHERE B\__city LIKE "Champaign" AND B\__state LIKE "IL" AND B\__business_id = R\__business_id
```
## Sample queries:
1. SELECT * FROM photos

  Time: 0.332295894623 seconds

2. SELECT DISTINCT stars FROM review-1m

  Time: 0.00784993171692 seconds

3. SELECT DISTINCT stars, useful FROM review-1m

  Time: 7.463971138 seconds

4. SELECT review_id, stars, useful FROM review-1m WHERE useful > 20 AND stars >= 4

  Time: 0.159142017365 seconds

5. SELECT review_id, stars, useful FROM review-1m WHERE useful > 20 AND stars >= 4 - 0

  Time: 0.0694561004639 seconds

6. SELECT review_id, stars, useful FROM review-1m WHERE useful > 10 AND (useful < 20 OR stars >= 4)

  Time: 0.17729306221 seconds

7. SELECT B\__city, B\__state, R\__business_id, R\__stars, R\__useful FROM business B, review-1m R WHERE B\__city LIKE "Champaign" AND B\__state LIKE "IL" AND B\__business_id = R\__business_id

  Time: 0.251272916794 seconds

8. SELECT DISTINCT B\__name FROM business B, review-1m R, photos P WHERE B\__city = Champaign AND B\__state = IL AND P\__label = inside AND R\__stars = 5 AND B\__business_id = P\__business_id AND B\__business_id = R\__business_id

  Time: 6.03912496567 seconds

  SELECT DISTINCT B\__name FROM business B, review-1m R, photos P WHERE B\__city = Champaign AND B\__state = IL AND P\__label = inside AND B\__business_id = P\__business_id AND B\__business_id = R\__business_id AND R\__stars = '5'

  Time: 0.423269033432 seconds
