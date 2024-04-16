import mariadb
from rich import print as printc
from rich.console import Console
console = Console()
  
def dbconfig():
  try:
    db = mariadb.connect(
      host ="localhost",
      user ="root",
      passwd ="password"
    )
    printc("Connected to db")
  except Exception as e:
    print("An error occurred while trying to connect to the database")
    console.print_exception(show_locals=True)

  return db