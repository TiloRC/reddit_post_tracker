import praw
import json
import schedule
import math
import statistics as stats
from datetime import datetime
import concurrent.futures
import os
import sys

from settings import reddit
import time
import database



class PostTracker:
    def __init__(self, subreddits):
        self.subs = {}
        for sub in subreddits:
            self.subs[sub] = {
                "name": sub,
                # Holds hot data after it is requested
                "hot" : {},
                # Data is stored here during multithreading and then sent to the database
                "database_queue":[],
                # An estimate of the number of active posts in each subreddit updated in real time
                "num_active_posts": 300,
                # Stores the post id of the newest post in each subreddit
                "latest_post_id" : "",
                # Stores the current hot rank of the newest post id for each subreddit. Used to estimate num_active_posts.
                "latest_post_rank": []
            }

        self.database_queue = []
        
    def start_tracking(self):
        print("Tracking started...")
        def update(sub):
            print(str(sub) + " starting update...")
            self.check_for_new_post(sub)
            self.update_hot(sub)
            self.update(sub)
            self.update_active_posts(sub)

        def update_all():
            start = time.time()
            if len(self.subs) > 1:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.map(update,self.subs)
            else:
                update([sub for sub in self.subs][0])
            for item in self.database_queue:
                #print(item)
                database.insert(item,"database")
            self.database_queue = []
                
            self.message()
            end = time.time()
            print("number of datapoints: ",database.get_size())
            print("Update Time: ",end-start, " sec")
                
        schedule.every().minute.at(":00").do(update_all)
        while True:
            schedule.run_pending()

    def check_for_new_post (self,sub):
        try:
            new = reddit.subreddit(sub).new(limit=1)
        except Exception as e:
            #time = self.get_time()
            #print("Error: Check for new post (", time,") ",sub_name)
            #print(e,"\n")
            pass
        else:
            self.subs[sub]["latest_post_id"] = [submission.id for submission in new][0]
    
    def update_hot(self,sub):
        limit = self.subs[sub]["num_active_posts"]
        try:
            hot = {post.id:post for post in reddit.subreddit(sub).hot(limit = limit) if not post.stickied }
        except Exception as e:
            time = self.get_time()
            print("Error: Update Hot (", time,")")
            print(e,"\n")
        else:
            self.subs[sub]["hot"] = hot
    
    def get_rank(self,post_id, sub):
        ar = [post for post in self.subs[sub]["hot"]]
        try:
            return ar.index(post_id)+1
        except:
            return math.nan

    def get_post_by_rank(self,rank,sub):
        ar = [post for post in self.subs[sub]["hot"]]
        return ar[rank-1]
    
    def update(self, sub):
        for post_id in self.subs[sub]["hot"]:
            rank = self.get_rank(post_id, sub)
            post = self.subs[sub]["hot"][post_id]
            self.database_queue.append({"subreddit":sub,
                                        "post_id":post_id,
                                        "age":time.time()-post.created_utc,
                                        "current_time":time.time(), 
                                        "rank":rank,
                                        "score": post.score})



    def message(self):
        message = ""
        for sub in self.subs:
            message += " ||| "+sub + " - "
            message += "estimated active posts: " + str(self.subs[sub]["num_active_posts"])
        print(message)
        #reddit.redditor("myUsername").message("UPDATE", message)

    def update_active_posts(self, sub):
        post_id = self.subs[sub]["latest_post_id"]
        self.subs[sub]["latest_post_rank"].append(self.get_rank(post_id,sub))
        rank_history = [rank for rank in self.subs[sub]["latest_post_rank"] if not math.isnan(rank)]
        if len(rank_history) > 0:
            num_active_posts = 10 + 2*int(stats.mean(rank_history))

            if math.isnan(num_active_posts) and self.subs[sub]["num_active_posts"] < 1000:
                self.subs[sub]["num_active_posts"] += 100
                #print("nan. ",self.num_active_posts[sub])
            else:
                self.subs[sub]["num_active_posts"] = num_active_posts 
                #print(sub," # active_posts: ",num_active_posts,end =" - ")
                #try:
                #	print(sub+"/comments/"+str(self.get_post_by_rank(num_active_posts,sub)))
                #except IndexError:
                #	print("index error")



if __name__ == '__main__':
    pt = PostTracker(sys.argv[1:])
    pt.start_tracking()
