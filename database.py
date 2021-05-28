import sqlite3
import sys
import time
import pandas as pd

conn = sqlite3.connect('data.db')

c = conn.cursor()

def create_table(table_name):
	with conn:
		c.execute("CREATE TABLE "+ table_name +""" (
					subreddit text, post_id text,age real, current_time real, rank int,	score int
					)""")

def insert(datum, table):
	with conn:
		c.execute("INSERT INTO " +table +" VALUES (:subreddit,:post_id,:age,:current_time,:rank,:score)", datum)

def insert_many(data, table):
	with conn:
		for datum in data:
			c.execute("INSERT INTO " +table +" VALUES (:subreddit,:post_id,:age,:current_time,:rank,:score)", datum)


def print_subreddit(subreddit, table):
	with conn:
		c.execute("SELECT * FROM "+ table+" WHERE subreddit = :subreddit", {"subreddit":subreddit})
		items = c.fetchall()
		for item in items:
			print(item)

def get_post(table,post_id):
	df = pd.read_sql_query("SELECT DISTINCT * FROM "+table+" WHERE post_id = '" +post_id +"' ORDER BY age ASC",conn)
	df["age"] = pd.to_numeric(df["age"])
	df["rank"] = pd.to_numeric(df["rank"])
	df["score"] = pd.to_numeric(df["score"])
	df = df.sort_values(by = ["age"])
	return df

def get_subreddit(table,subreddit):
	df = pd.read_sql_query("SELECT DISTINCT * FROM "+table+" WHERE subreddit = '" +subreddit+"' ORDER BY age ASC",conn)
	print(df)
	df["age"] = pd.to_numeric(df["age"])
	df["rank"] = pd.to_numeric(df["rank"])
	df["score"] = pd.to_numeric(df["score"])
	df = df.sort_values(by = ["age"])
	return df

def get_distinct_post_ids(table,subreddit ="", min_upvotes = 1):
	if subreddit == "":
		return pd.read_sql_query("SELECT DISTINCT post_id FROM "+table+" WHERE score >= " +str(min_upvotes),conn)["post_id"]
	else:
		return pd.read_sql_query("SELECT DISTINCT post_id FROM "+table+" WHERE subreddit = '"+ subreddit+"' AND score >= " +str(min_upvotes),conn)["post_id"]

def get_distinct_subreddits(table):
	return pd.read_sql_query("SELECT DISTINCT subreddit FROM " +table,conn)["subreddit"]

def get_all(table):
	with conn:
		c.execute("SELECT DISTINCT * FROM "+table)
		return list(c.fetchall())

def rename_table(old_name, new_name):
	with conn:
		c.execute("ALTER TABLE " + old_name + " RENAME TO " +new_name)

def get_size(table):
	start = time.time()
	result = "error"
	with conn:
		c.execute("SELECT * FROM " +table)
		result = len(c.fetchall())
	end = time.time()
	if end - start > 1:
		print("get_size time: ", end-start)
	return result 

def clear_all(table):
	with conn:
		c.execute("DELETE FROM "+table)


def filter_out_incomplete_posts():
	with conn:
		c.execute("SELECT DISTINCT post_id FROM raw_data WHERE age < 3000")
		complete_post_ids = ["'"+post[0]+"'" for post in c.fetchall()]
		end = "post_id = " +" OR post_id = ".join(complete_post_ids)
		c.execute("SELECT * FROM raw_data WHERE " + end)
		return c.fetchall()

def update_filtered_data():
	print(len(get_all("filtered_data")))
	clear_all("filtered_data")
	for x in filter_out_incomplete_posts():
		insert(x, "filtered_data")
	print(len(get_all("filtered_data")))

def copy_table_to_table(source,destination):
	with conn:
		c.execute("INSERT INTO "+ destination+" SELECT * FROM "+source)

#update_filtered_data()

try:
	create_table("filtered_data")
	create_table("raw_data")
except sqlite3.OperationalError:
	pass

if __name__ == '__main__':
		if len(sys.argv) < 2:
			pass
		elif sys.argv[1] == "print_all":
			print_all()
		elif sys.argv[1] == "print_subreddit":
			print_subreddit(sys.argv[2])
		elif sys.argv[1] == "clear_all":
			clear_all()



