# Reddit Post Tracker (WIP)
This is a reddit bot that tracks the growth of reddit upvote counts over time. I'm building it to collect data for a blog post I'm writing about how reddit posts grow over time.

## How to Get Started (WIP)

You'll need to have a reddit developer acount and authentication information to run this code. I'll be assuming you already went through the process of setting that up (it's completely free). After cloning this repository, create a new file called "authentication.py." Fill it in so it looks something like this:

```
import praw
reddit = praw.Reddit(client_id='your id', \
                     client_secret='your secret', \
                     user_agent='your app name', \
                     username='your username ', \
                     password="your password")
```
