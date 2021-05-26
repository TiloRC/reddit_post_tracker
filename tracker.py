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
        self.latest_post_id = {sub: "" for sub in subreddits}
        self.active_posts = {sub: {} for sub in subreddits}
        self.inactive_posts = {sub: {} for sub in subreddits}
        self.hot = {sub: {} for sub in subreddits}
        self.subs = [reddit.subreddit(sub) for sub in subreddits]
        self.database_queue = []
        self.num_active_posts = {sub: 300 for sub in subreddits}
        self.latest_post_rank = {sub: [] for sub in subreddits}
        
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
                update(self.subs[0])
            self.update_database()
            self.message()
            end = time.time()
            print("Update Time: ",end-start, " sec")
                
        schedule.every().minute.at(":00").do(update_all)
        while True:
            schedule.run_pending()

    def check_for_new_post (self,sub):
        try:
            sub_name = str(sub)
            new = sub.new(limit=1)
        except Exception as e:
            time = self.get_time()
            print("Error: Check for new post (", time,") ",sub_name)
            print(e,"\n")
        else:
            new_post_id = [submission.id for submission in new][0]

            if self.latest_post_id[sub_name] != new_post_id:
                self.latest_post_id[sub_name] = new_post_id
                self.active_posts[sub_name][self.latest_post_id[sub_name]] = []
    
    def update_hot(self,sub):
        sub_name = str(sub)
        limit = self.num_active_posts[sub_name]
        try:
            hot = {post.id:post for post in sub.hot(limit = limit) if not post.stickied }
        except Exception as e:
            time = self.get_time()
            print("Error: Update Hot (", time,")")
            print(e,"\n")
        else:
            self.hot[sub_name] = hot
    
    def get_rank(self,post_id, sub):
        sub_name = str(sub)
        ar = [post for post in self.hot[sub_name]]
        try:
            return ar.index(post_id)+1
        except:
            return math.nan

    def get_post_by_rank(self,rank,sub):
        sub_name = str(sub)
        ar = [post for post in self.hot[sub_name]]
        return ar[rank-1]
    
    def update(self, sub):
        sub_name = str(sub)
        for post_id in self.active_posts[sub_name].copy():
            rank = self.get_rank(post_id, sub)
            if math.isnan(rank):
                self.inactive_posts[sub_name][post_id] = self.active_posts[sub_name].pop(post_id)
            else:
                post = self.hot[sub_name][post_id]
                #self.active_posts[sub_name][post_id].append([date_time, rank, post.score]) 
                self.database_queue.append({"subreddit":sub_name,
                                            "post_id":post_id,
                                            "age":time.time()-post.created_utc,
                                            "current_time":time.time(), 
                                            "rank":rank,
                                            "score": post.score})

    def message(self):
        message = ""
        for sub in self.subs:
            sub_name = str(sub)
            message += " ||| "+sub_name + " - "
            message += "active posts: " + str(len(self.active_posts[sub_name]))
            message += " inactive posts: " + str(len(self.inactive_posts[sub_name]))
        print(message)
        #reddit.redditor("myUsername").message("UPDATE", message)

    def update_database(self):
        for item in self.database_queue:
            database.insert(item)
        self.database_queue = []

    def update_active_posts(self, sub):
        sub = str(sub)
        post_id = self.latest_post_id[sub]
        self.latest_post_rank[sub].append(self.get_rank(post_id,sub))
        num_active_posts = 10 + 2*int(stats.mean(self.latest_post_rank[sub]))

        if math.isnan(num_active_posts):
            self.num_active_posts[sub] += 100
            print("nan. ",self.num_active_posts[sub])
        else:
            self.num_active_posts[sub] = num_active_posts 
            #print(sub," # active_posts: ",num_active_posts,end =" - ")
            #try:
            #	print(sub+"/comments/"+str(self.get_post_by_rank(num_active_posts,sub)))
            #except IndexError:
            #	print("index error")



if __name__ == '__main__':
    pt = PostTracker(sys.argv[1:])
    pt.start_tracking()
