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
SELECT B__city, B__state, R__business_id, R__stars, R__useful FROM business B, review-1m R WHERE B__city LIKE "Champaign" AND B__state LIKE "IL" AND B__business_id = R__business_id
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
SELECT B__city, B__state, R__business_id, R__stars, R__useful FROM business B, review-1m R WHERE B__city LIKE "Champaign" AND B__state LIKE "IL" AND B__business_id = R__business_id
```
NOTICE: [MODE 0] WHERE conditions in multi table join after the join: Numeric values and string need to be inside the quotation mark. Use [MODE 1] if you don't want to pay attention to the quotation mark. [MODE 0] will be slightly faster than [MODE1] since \[MODE 0\] will not need to tranfer data type.

## Demo queries:
1. SELECT review_id, funny, useful FROM review-1m WHERE funny >= 20 AND useful > 30

  Time: 0.261s

2. SELECT name, city, state FROM business WHERE city = Champaign AND state = IL

  Time: 0.082s

3. SELECT B\__name, B\__postal_code, R\__stars, R\__useful FROM business B, review-1m R WHERE B\__name = Sushi Ichiban AND B\__postal_code = 61820 AND B\__business_id = R\__business_id

  Time: 0.379s

4. SELECT R1\__user_id, R2\__user_id, R1\__stars, R2\__stars FROM review-1m R1, review-1m R2 WHERE R1\__useful > 50 AND R2\__useful > 50 AND R1\__business_id = R2\__business_id AND R1\__stars = '5' AND R2\__stars = '1'
  
  Time: 0.277s

5. SELECT B\__name, B\__city, B\__state, R\__stars, P\__label FROM business B, review-1m R, photos P WHERE B\__city = Champaign AND P\__label = inside AND B\__state = IL AND B\__business_id = P\__business_id AND B\__business_id = R\__business_id AND R\__stars = '5'

  Time: 0.745s

6. SELECT B\__name, R1\__user_id, R2\__user_id, B\__address FROM business B, review-1m R1, review-1m R2 WHERE R1\__useful > 50 AND R2\__useful > 50 AND B\__business_id = R1\__business_id AND R1\__business_id = R2\__business_id AND R1\__stars = '5' AND R2\__stars = '1'

  Time: 0.444s

## Sample queries:
1. SELECT * FROM photos

  Time: 0.359s

2. SELECT DISTINCT stars FROM review-1m

  Time: 0.004s

3. SELECT DISTINCT stars, useful FROM review-1m

  Time: 7.694s

4. SELECT review_id, stars, useful FROM review-1m WHERE useful > 20 AND stars >= 4

  Time: 0.391s

5. SELECT review_id, stars, useful FROM review-1m WHERE useful > 20 AND stars >= 4 - 0

  Time: 0.208s

6. SELECT review_id, stars, useful FROM review-1m WHERE useful > 10 AND (useful < 20 OR stars >= 4)

  Time: 0.306s

7. SELECT B\__city, B\__state, R\__business_id, R\__stars, R\__useful FROM business B, review-1m R WHERE B\__city LIKE "Champaign" AND B\__state LIKE "IL" AND B\__business_id = R\__business_id

  Time: 0.427s

8. SELECT DISTINCT B\__name FROM business B, review-1m R, photos P WHERE B\__city = Champaign AND B\__state = IL AND P\__label = inside AND R\__stars = 5 AND B\__business_id = P\__business_id AND B\__business_id = R\__business_id

  Time: 6.765s

  SELECT DISTINCT B\__name FROM business B, review-1m R, photos P WHERE B\__city = Champaign AND B\__state = IL AND P\__label = inside AND B\__business_id = P\__business_id AND B\__business_id = R\__business_id AND R\__stars = '5'

  Time: 0.745s
