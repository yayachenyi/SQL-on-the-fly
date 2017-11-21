Source code: myproject.py (Python2.7)
Data files: movies.csv, oscars.csv

Team: Panda Panda
Team members: Yichen Feng, Xuan Wang, Fei Ling
Requirement: sqlparse, pandas

To run the code:
1. Start the program: 
python myproject.py

2. Load the datasets:
USE ./movies.csv
USE ./oscars.csv

3. Input queries:
Query1: SELECT movie_title, title_year, imdb_score FROM movies WHERE imdb_score > 7 AND movie_title LIKE “%Kevin%“

Query2: SELECT M__title_year, M__movie_title, A__Award, M__imdb_score, M__movie_facebook_likes FROM movies M, oscars A ON M__movie_title = A__Film WHERE A__Winner = 1 AND (M__imdb_score < 6 OR M__movie_facebook_likes < 10000)

Query3: SELECT M1__director_name, M1__title_year, M1__movie_title, M2__title_year, M2__movie_title, M3__title_year, M3__movie_title FROM movies M1, movies M2, movies M3 ON M1__director_name = M2__director_name AND M1__director_name = M3__director_name WHERE M1__movie_title <> M2__movie_title AND M2__movie_title <> M3__movie_title AND M1__movie_title <> M3__movie_title AND M1__title_year < M2__title_year - 15 AND M2__title_year < M3__title_year - 15

4. Exit the program:
exit


Note:
1. If multiple tables are used, there must be an ‘ON’ connecting all the joining conditions in the FROM clause. The joining conditions must be connected by ‘AND’. All the attributes must be changed into the format ‘tableName__attributeName’.
2. In the WHERE clause, there must be a space between attributes and operators. 
3. If there is an ‘LIKE’ operator in the WHERE clause, it must be put as the last condition.
