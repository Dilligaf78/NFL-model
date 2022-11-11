# NFL Points and Spread Models

## Machine learning regression models to predict nfl results

I was lured into joining a football pool.  The pool is composed of more than 100 people who attempt to 
guess which teams will beat the "CBS SPorts" predicted spread.  While the people who talked me into joining 
are not statheads, some of the others in the pool are avid fans and statheads and have set a very high 
bar to compete.

I did not have a lifetime to learn as some of these players had, so I decided to develop a linear regression
algorithm of publically available stats.  I have been using this same algorithm since 2019.  On average, 
I would correctly identify 60% of the games.  This was a enough to keep me in the top ten of the pool.

After taking several computer classes this year, including Harvard's CS50, I decided to try a machine 
learning algorithm and find out if my odds could be improved.

I tried a Watson model, as well as several Python packages.  The most successful package was SKlearn.  Utilizing linear 
and logistical regression with scaling functions to normalize the data and elastic net filter out some of the noise, 
I was able to increase my accuracy to 80%. (At tleast for this week.  Will have to monitor going forward.)

I have scraped data from three sites:
* https://www.pro-football-reference.com/
* http://sonnymoorepowerratings.com/nfl-foot.htm
* https://www.footballoutsiders.com/

All data is imported as dataframes.  The data is combined and reexported as a tab delimited file. 

I explored several different regression models, including, logistical, random forest and linear regression.  I also looked at different
pipe methods incuding elastic net and ridge.

## Installation
Required add-ins:
numpy as np
pandas as pd
sklearn
matplotlib.pyplot
seaborn

## Video Demo
url: https://youtu.be/ORzBJEqHnRg

## Usage
Anyone may use this program.  But it is not intended to be used for monetary betting. The house always wins.

This program is for entertainment purposes only.

## Authors
Sara Estes aka Dilligaf78 
This project could not have been realized without the CS50 teaching staff. 
David Malan has made python and machine learning available to even non-It majors like me.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Please make sure to update tests as appropriate.

## License
MIT
