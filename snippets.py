import logging
import argparse
import psycopg2

#Setup basic logging
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")

def put(name, snippet):
	"""
	Store a snippet with an associated name

	Returns the name and the snippet
	"""
	try:
		with connection, connection.cursor() as cursor:
			cursor.execute("insert into snippets \
				values (%s, %s)",(name,snippet))
			logging.debug("Snippet stored successfully")
	except psycopg2.IntegrityError as e:
		connection.rollback()
		logging.debug(e)
	return name, snippet

def get(name):
	"""
	Retrieve the snippet with a given name.

	If there is no such snippet, return '404: Snippet Not Found'.

	Returns the snippet.
	"""
	with connection, connection.cursor() as cursor:
		cursor.execute("\
			select message from snippets\
		 	where keyword = %s", (name,))
		details = cursor.fetchone()

	if details:
		return details[0]
	else:
		return "404: Snippet Not Found"

def catalog():
	"""
	Retrieve all keys
	"""
	with connection, connection.cursor() as cursor:
		cursor.execute("\
			select keyword from snippets")
		details = cursor.fetchall()

	return details

def search(snippet):
	with connection, connection.cursor() as cursor:
		cursor.execute("\
			select * from snippets\
			where message like %s",('%' + snippet + '%',))
		details = cursor.fetchall()
	return details

def main():
	"""Main Function"""
	logging.info("Constructing parser")
	parser = argparse.ArgumentParser(description="Store and retrieve \
		snippets of text")

	subparsers = parser.add_subparsers(dest="command", help="Available \
		commandss")

	#Subparser for the put command
	logging.debug("Constructing put subparser")
	put_parser = subparsers.add_parser("put", help="Store a snippet")
	put_parser.add_argument("name", help="Name of the snippet")
	put_parser.add_argument("snippet", help="Snippet text")

	#subparser for the search command
	logging.debug("Constructing search subparser")
	search_parser = subparsers.add_parser("search", help="Search a snippet")
	search_parser.add_argument("snippet", help="Snippet text")

	#Subparser for the get command
	logging.debug("Constructing get command")
	get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
	get_parser.add_argument("name", help="Name of the snippet")

	#Subparser for catalog command
	cat_parser = subparsers.add_parser("catalog", help="Retrieve all names")

	arguments = parser.parse_args()
	arguments = vars(arguments)

	command = arguments.pop("command");

	if command == "put":
		name, snippet = put(**arguments)
		print("Stored {!r} as {!r}".format(snippet, name))
		# Grab repr for whatever it is referencing, for example the above will get repr(snippet), repr(name)
	elif command == "get":
		snippet = get(**arguments)
		print("Retrieved snippet: {!r}".format(snippet))
	elif command == "catalog":
		names = catalog()
		for name in names:
			print(name[0])
	elif command == "search":
		results = search(**arguments)
		if results:
			for result in results:
				print("Found {!r} from {!r}".format(result[1], result[0]))
		else:
			print("Found nothing")

if __name__ == "__main__":
	main()
