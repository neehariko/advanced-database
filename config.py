import os
import sys
import string
import random
import hashlib
import sys
from getpass import getpass

from utils.dbconfig import dbconfig

from rich import print as printc
from rich.console import Console

console = Console()

def checkConfig():
	db = dbconfig()
	cursor = db.cursor()
	query = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA  WHERE SCHEMA_NAME = 'varigidb'"
	cursor.execute(query)
	results = cursor.fetchall()
	db.close()
	if len(results)!=0:
		return True
	return False


def generateDeviceSecret(length=10):
	return ''.join(random.choices(string.ascii_uppercase + string.digits, k = length))


def make():
	if checkConfig():
		printc("Already Configured!")
		return

	printc("Creating new configuration")

	# Create database
	db = dbconfig()
	cursor = db.cursor()
	try:
		cursor.execute("CREATE DATABASE varigidb")
	except Exception as e:
		printc(" An error occurred while trying to create db. Check if database with name 'varigidb' already exists - if it does, delete it and try again.")
		console.print_exception(show_locals=True)
		sys.exit(0)

	printc("Database 'varigidb' created")

	# Create tables
	query = "CREATE TABLE varigidb.secrets (masterkey_hash TEXT NOT NULL, device_secret TEXT NOT NULL)"
	res = cursor.execute(query)
	printc("[green][+][/green] Table 'secrets' created ")

	query = "CREATE TABLE varigidb.entries (sitename TEXT NOT NULL, siteurl TEXT NOT NULL, email TEXT, username TEXT, password TEXT NOT NULL)"
	res = cursor.execute(query)
	printc("[green][+][/green] Table 'entries' created ")


	mp = ""
	

	while 1:
		mp = getpass("Choose a MASTER PASSWORD: ")
		if mp == getpass("Re-type: ") and mp!="":
			break
		printc(" Please try again.")

	# Hash the MASTER PASSWORD
	hashed_mp = hashlib.sha256(mp.encode()).hexdigest()
	printc("Generated hash of MASTER PASSWORD")


	# Generate a device secret
	ds = generateDeviceSecret()
	printc("Device Secret generated")

	# Add them to db
	query = "INSERT INTO varigidb.secrets (masterkey_hash, device_secret) values (%s, %s)"
	val = (hashed_mp, ds)
	cursor.execute(query, val)
	db.commit()

	printc("Added to the database")

	printc("Configuration done")

	db.close()


def delete():
	printc("Deleting a config clears the device secret and master password")

	while 1:
		op = input("So are you sure you want to continue? (y/N): ")
		if op.upper() == "Y":
			break
		if op.upper() == "N" or op.upper == "":
			sys.exit(0)
		else:
			continue

	printc("Deleting config")


	if not checkConfig():
		printc("[yellow][-][/yellow] No configuration exists to delete!")
		return

	db = dbconfig()
	cursor = db.cursor()
	query = "DROP DATABASE varigidb"
	cursor.execute(query)
	db.commit()
	db.close()
	printc(" Config deleted!")

def remake():
	printc(" Remaking config")
	delete()
	make()


if __name__ == "__main__":

	if len(sys.argv)!=2:
		print("Usage: python config.py <make/delete/remake>")
		sys.exit(0)

	if sys.argv[1] == "make":
		make()
	elif sys.argv[1] == "delete":
		delete()
	elif sys.argv[1] == "remake":
		remake()
	else:
		print("Usage: python config.py <make/delete/remake>")