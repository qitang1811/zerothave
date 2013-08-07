Project zerothave(www.zerothave.com)
=========

Zerothave is web aggregator that collects latest magazine, and news paper articles in a  widly range. It displays only the title, short discription and image(if it has) of the article in a concise style, then it will redirect
user to the original website by click the cubic. It's written in python and running on Google app engine.


Features
=======
1. Concise masonry grid style UI.
2. Daily updated.
3. Runs excellent under google free quota.
4. Easy to expand with new feed source.


How to customise it ?
======

1. Download the source code 
2. Add a well tested feed handler for the specific feed(view the code for detail) in the Handler file.
3. Add the feed link to dictByLabel, dictBySrc and CACHE.
4. Update xmlDispatcher function with the feed, if necessary.
5. Launch the application through command line or google app engine launcher.
6. Visit url "localhost:8080/SuperAdminQQ", which triggles function runApplication() to parse the feeds.
7. If no error occured, visit url "localhost:8080", you will see the home page.



