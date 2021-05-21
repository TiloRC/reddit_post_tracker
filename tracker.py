import praw
import json
import schedule
import math
from datetime import datetime
import concurrent.futures
import os
import sys

from settings import reddit


class PostTracker:
    def __init__(self, subreddits):
        self.latest_post_id = {sub: "" for sub in subreddits}
        self.posts = {sub: {} for sub in subreddits}
        self.mature_posts = {sub: {} for sub in subreddits}
        self.hot = {sub: {} for sub in subreddits}
        self.subs = [reddit.subreddit(sub) for sub in subreddits]

        try:
            os.mkdir("data")
        except FileExistsError:
            pass
        
    def start_tracking(self):
        print("Tracking started...")

        def update(sub):
            print(str(sub) + " starting update...")
            self.check_for_new_post(sub)
            self.update_hot(sub)
            self.update(sub)

        def update_all():
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(update,self.subs)
            self.update_files()
            self.message()
                
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
                self.posts[sub_name][self.latest_post_id[sub_name]] = []
    
    def update_hot(self,sub):
        sub_name = str(sub)
        try:
            hot = {post.id:post for post in sub.hot(limit = 1000) if not post.stickied }
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
    
    def update(self, sub):
        sub_name = str(sub)
        time = self.get_time()
        for post_id in self.posts[sub_name]:
            rank = self.get_rank(post_id, sub)
            if math.isnan(rank):
                self.mature_posts[sub_name][post_id] = self.posts[sub_name].pop(post_id)
            else:
                try:
                    self.posts[sub_name][post_id]
                except KeyError as e:
                    print("Error 1 at ",sub_name,": ",e)
                try:
                    self.posts[sub_name][post_id].append([time, rank, self.hot[sub_name][post_id].score])
                except KeyError as e:
                    print("Error 2 at ",sub_name,": ",e, "(rank = ", rank,")")

    def message(self):
        message = ""
        for sub in self.subs:
            sub_name = str(sub)
            message += " ||| "+sub_name + " - "
            message += "posts: " + str(len(self.posts[sub_name]))
            message += " mature posts: " + str(len(self.mature_posts[sub_name]))
        print(message)
        #reddit.redditor("myUsername").message("UPDATE", message)

    def update_files(self):
        file = open("data/data.txt","w")
        file.write(str(self.posts))
        file.close()

        file2 = open("data/mature_data.txt","w")
        file2.write(str(self.mature_posts))
        file2.close()

    def load_old_data(self):
        file = open("data/data.txt","r")
        old_data = file.read().replace("'",'"')
        self.posts = json.loads(old_data)
        file.close()

        file2 = open("data/mature_data.txt","r")
        old_mature_data = file2.read().replace("'",'"')
        self.mature_posts = json.loads(old_mature_data)
        file2.close()

    def get_time(self):
        return datetime.now().strftime("%m:%d:%H:%M:%S")

if __name__ == '__main__':
    args = []
    if sys.argv[1] == "load_old":
        print("load_old = True")
        load_old = True
        args = sys.argv[2:]
    else:
        args = sys.argv[1:]
        load_old = False
    pt = PostTracker(args)
    if load_old:
        pt.load_old_data()
    pt.start_tracking()
