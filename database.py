import sqlite3
import sys
import time

conn = sqlite3.connect('data.db')

c = conn.cursor()

default_table = "database"

def create_table(table_name):
	with conn:
		c.execute("CREATE TABLE "+ table_name +""" (
					subreddit text, post_id text,age real, current_time real, rank int,	score int
					)""")

def insert(datum, table = default_table):
	with conn:
		c.execute("INSERT INTO " +table +" VALUES (:subreddit,:post_id,:age,:current_time,:rank,:score)", datum)


def print_subreddit(subreddit, table = default_table):
	with conn:
		c.execute("SELECT * FROM "+ table+" WHERE subreddit = :subreddit", {"subreddit":subreddit})
		items = c.fetchall()
		for item in items:
			print(item)


def print_all(table = default_table):
	print("test")
	with conn:
		print("huh")
		c.execute("SELECT * FROM "+table)
		items = c.fetchall()
		for item in items:
			print(item)

def rename_table(old_name, new_name):
	with conn:
		c.execute("ALTER TABLE " + old_name + " RENAME TO " +new_name)

def get_size(table = default_table):
	start = time.time()
	result = "error"
	with conn:
		c.execute("SELECT * FROM " +table)
		result = len(c.fetchall())
	end = time.time()
	if end - start > 1:
		print("get_size time: ", end-start)
	return result 


def clear_all(table = default_table):
	with conn:
		c.execute("DELETE FROM "+table)

try:
	create_table(default_table)
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



