import praw, prawcore
import schedule
from datetime import datetime
import concurrent.futures
import sys
from authentication import reddit
import time
import database


class PostTracker:
    def __init__(self, subreddits):
        self.subs = {sub:5+2*self.count_new_posts(sub) for sub in subreddits}
        print(self.subs)
        for sub in self.subs:
            try:
                database.create_table(sub)
            except database.sqlite3.OperationalError:
                pass

    def start_tracking(self):
        print("Tracking started...")
        def update_all():
            try:
                raw_data = self.fetch_all_data()
                new_data = self.clean_up(raw_data) # Converts to dictionary format {"WritingPrompts": {"opcjb0":...}}
                self.export_to_database(new_data)
            except prawcore.exceptions.BadJSON:
                print("Error: ", prawcore.exceptions.BadJSON)
                print("Script will continue to run.")

        schedule.every().minute.at(":00").do(update_all)
        while True:
            schedule.run_pending()

    def fetch_all_data(self):
        def fetch_new_subreddit_data(sub):
            #print(sub + " fetching data...")
            result = {sub: [post for post in reddit.subreddit(sub).hot(limit = self.subs[sub]) if not post.stickied]}
            #print(sub + " fetching data complete")
            return result

        start = time.time()
        if len(self.subs) > 1:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = {}
                for subreddit in executor.map(fetch_new_subreddit_data,self.subs):
                    result.update(subreddit)
        else:
            result = fetch_new_subreddit_data([sub for sub in self.subs][0])
        end = time.time()
        print("Fetch all time: ", end-start)
        return result

    def clean_up(self,raw_data):
        present_time = time.time()
        new_data = {}
        for subreddit in raw_data:
            subreddit_data = {}
            sub_name = subreddit
            sub_data = raw_data[subreddit]

            rank = 0
            for post in sub_data:
                rank += 1
                subreddit_data[post.id] = {
                    "post_id": post.id,
                    #"subreddit": sub_name,
                    "score": post.score,
                    "rank": rank,
                    "num_comments": post.num_comments,
                    "present_time": present_time
                }
            new_data[sub_name] = subreddit_data
        return new_data

    def export_to_database(self, new_data):
        for subreddit in new_data:
            sub_data = new_data[subreddit]
            sub_data = [sub_data[post_id] for post_id in sub_data]
            database.insert_posts(sub_data, subreddit)

    def count_new_posts(self,subreddit):
        present_time = time.time()
        new = [(present_time-post.created_utc)/60/60 for post in reddit.subreddit(subreddit).new(limit = 150)]
        num_new_posts = 0
        for t in new:
            if t < 12:
                num_new_posts += 1
        if num_new_posts == 150:
            num_new_posts = 250
        return num_new_posts


if __name__ == '__main__':
    subreddits =  sys.argv[1:]
    pt = PostTracker(subreddits)
    pt.start_tracking()
