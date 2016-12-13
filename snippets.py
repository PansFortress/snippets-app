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
		command = "insert into snippets values (%s, %s)"
		cursor = connection.cursor()
		cursor.execute(command, (name, snippet))
		connection.commit()
		logging.debug("Snippet stored successfully")
	except psycopg2.IntegrityError as e:
		connection.rollback()
		logging.debug("Keyword already exists")
	return name, snippet

def get(name):
	"""
	Retrieve the snippet with a given name.

	If there is no such snippet, return '404: Snippet Not Found'.

	Returns the snippet.
	"""
	command = "select * from snippets where keyword = %s"
	cursor = connection.cursor()
	cursor.execute(command,(name,))

	details = cursor.fetchone()
	if details:
		return details
	else:
		return "404: Snippet Not Found"

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

	#Subparser for the get command
	logging.debug("Constructing get command")
	get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
	get_parser.add_argument("name", help="Name of the snippet")

	arguments = parser.parse_args()
	arguments = vars(arguments)

	command = arguments.pop("command");

	if command == "put":
		name, snippet = put(**arguments)
		print("Stored {!r} as {!r}".format(snippet, name))
	elif command == "get":
		snippet = get(**arguments)
		print("Retrieved snippet: {!r}".format(snippet))

if __name__ == "__main__":
	main()
