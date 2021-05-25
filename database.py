import sqlite3

conn = sqlite3.connect('data.db')

c = conn.cursor()



def create_table():
	with conn:
		c.execute("""CREATE TABLE database (
					subreddit text, post_id text,age real, current_time real, rank int,	score int
					)""")

def insert(datum):
	with conn:
		c.execute("INSERT INTO database VALUES (:subreddit,:post_id,:age,:current_time,:rank,:score)", datum)


def print_subreddit(subreddit):
	with conn:
		c.execute("SELECT * FROM database WHERE subreddit = :subreddit", {"subreddit":subreddit})
		items = c.fetchall()
		for item in items:
			print(item)


def print_all():
	print("test")
	with conn:
		print("huh")
		c.execute("SELECT * FROM database")
		items = c.fetchall()
		for item in items:
			print(item)


def clear_all():
	with conn:
		c.execute("DELETE FROM database")

try:
	create_table()
except sqlite3.OperationalError:
	pass


