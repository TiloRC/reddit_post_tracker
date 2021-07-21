# Reddit Post Tracker (WIP)
This is a reddit bot that tracks the growth of reddit upvote counts over time. I'm building it to collect data for a blog post I'm writing about how reddit posts grow over time.

### Database
- subreddits
  - subreddit
    -post



#### Post
Object that holds a post's data
- id
- title
- created_utc
- data []
  - score 
  - rank
  - num_comments
  - present_time

#### Subreddit
Object that holds a subreddit's data
- posts []
- num_growing_posts
-

#### PostTracker
Collects current upvote counts every minute and stores them in SQLite database.
- 
