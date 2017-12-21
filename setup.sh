echo "The preprocessing time will take about 10 to 20 mins"
mkdir disk
mkdir row_references
mkdir index
/usr/bin/python2.7 disk.py
/usr/bin/python2.7 index.py
echo SQL-on-the-fly is now on the fly! Please enjoy!
