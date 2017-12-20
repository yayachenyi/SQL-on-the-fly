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
1. SELECT review_id, stars, useful FROM review-1m WHERE stars >= 4 AND useful > 20
Time: 0.147447109222 seconds
RealTime: 0.101026058197 seconds

2. SELECT B__name, B__postal_code, R__review_id, R__stars, R__useful FROM business B, review-1m R WHERE B__city LIKE "Champaign" AND B__state LIKE "IL" AND B__business_id = R__business_id
Time: 0.114972114563 seconds
RealTime: 0.1712911129 seconds

3. SELECT DISTINCT B__name FROM business B, review-1m R, photos P WHERE B__city = Champaign AND B__state = IL AND P__label = inside AND B__business_id = P__business_id AND R__stars = 5 AND B__business_id = R__business_id
Time: 0.565989971161 seconds

SELECT DISTINCT B__name FROM business B, review-1m R, photos P WHERE B__city = Champaign AND B__state = IL AND P__label = inside AND R__stars = 5 AND B__business_id = P__business_id AND B__business_id = R__business_id
Time: 0.144320964813 seconds
RealTime: 0.426993131638 seconds


4. SELECT name, city FROM business WHERE city = Chicago AND state = IL
Time: 0.00670599937439 seconds
RealTime: 0.0112009048462 seconds

5. SELECT R__stars, R__useful FROM business B, review-1m R WHERE B__name = Sushi Ichiban AND B__postal_code = 61820 AND B__business_id = R__business_id
Time: 0.0540008544922 seconds
RealTime: 0.0525069236755 seconds

6. SELECT name, city FROM business WHERE state = IL
RealTime: 0.0473620891571 seconds

7. SELECT B__postal_code, B__city, P__postal_code, P__city FROM business B, business P WHERE B__city = Champaign AND P__city = Champaign AND B__postal_code >= 61822 AND B__city = P__city AND B__postal_code < P__postal_code

8. SELECT B__postal_code, B__city, P__postal_code, P__city FROM business B, business P WHERE B__city LIKE "Champaign" AND B__state LIKE "IL" AND P__city LIKE "Champaign" AND B__postal_code < P__postal_code
