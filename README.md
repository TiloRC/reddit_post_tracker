# Reddit Post Tracker (WIP)
This bot tracks the growth of post upvote counts, hot rankings, and comments over time using PRAW. I'm building it to collect data for a blog post I'm writing.

## How to Get Started

You'll need to have a reddit developer acount and authentication information to run this code. If you don't already have such an account you can follow [this guide](https://towardsdatascience.com/how-to-use-the-reddit-api-in-python-5e05ddfd1e5c)  (it's completely free). After cloning this repository, create a new file called "authentication.py" and add your authentication information to the file. It should look something like this:

```
import praw
reddit = praw.Reddit(client_id='your id', \
                     client_secret='your secret', \
                     user_agent='your app name', \
                     username='your username ', \
                     password="your password")
```

## Using Reddit Post Tracker

Using Reddit Post Tracker is as simple as navigating to folder where it is located and running a command through the command line with the subreddits you want to track.
    
    python3 tracker.py subreddit1 subreddit2 etc.
    
At the start of every minute data is collected from aproximately all the active posts for each subreddit and automatically stored in an SQLite database in a file called "data.db." Here's an example of what some of the data might look like:

| post_id        | score           | rank  | num_comments  | present_time (utc time) |
| ------------- |:-------------:|:-------------:|:-------------:| -----:| 
| ooj686         | 19              | 146 |6       | 1626925094
| oojteo         | 17              |   147 |1     | 1626925094
| ooiid9         | 20              |    148 |1    | 1626925094

Present time is the present time immediately after all the data has been requested and obtained. Because of this, the present time will have a possibly large positive error for each post no more than the fetch all time. 
