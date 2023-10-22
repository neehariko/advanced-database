# ADSD October 16 Lecture -- Essay Form

## Completing the Mongita Example

Hi!

_(Fun fact: at the time of writing this, I am traveling 188.5 miles per hour on a train in southern Italy. As far as I know, that is the fastest I have every traveled on the ground while writing a lecture!)_

## Introduction

In this discussion, we will be finishing up the Mongita/Mongo example in preparation for putting our database program onto a cloud database in our next lecture. For now, we're going to complete and test all of our CRUD operations for our little web application. 

First, since both classes are viewing this activity, I have put this particular chapter in the repo in .../gamma/topic-05-mongita. That is also where this document will be kept, so I'm assuming you have found your way there. 

By the way, this is a Markdown document, so if you're not reading a styled version, try right-clicking on the filename in the side of VSCode and selecting [Open Preview]. 

So, on to the code. 

First, in the `gamma/topic-05-mongita` there is a slightly updated version of `application.py` -- mostly fixed because in one class I was calling the returned value "rows" and in the other I was calling the returned values "items" -- so I settled on "items".

The file looks like this at the moment: 

```
from bottle import route, post, run, template, redirect, request

import database

@route("/")
def get_index():
    redirect("/list")

@route("/list")
def get_list():
    rows = database.get_items()
    return template("list.tpl", shopping_list=rows)

@route("/add")
def get_add():
    return template("add_item.tpl")

@post("/add")
def post_add():
    description = request.forms.get("description")
    database.add_item(description)
    redirect("/list")

@route("/delete/<id>")
def get_delete(id):
    database.delete_item(id)
    redirect("/list")

@route("/update/<id>")
def get_update(id):
    rows = database.get_items(id)
    if len(rows) != 1:
        redirect("/list")
    description = rows[0]['description']
    return template("update_item.tpl", id=id, description=description)

@post("/update")
def post_update():
    description = request.forms.get("description")
    id = request.forms.get("id")
    database.update_item(id, description)
    redirect("/list")

run(host='localhost', port=8080)
```

With the same templates as before, this application seems _almost_ ready to go. 

## Finishing the Database Layer

Now, let's go work on the database layer. 

Let's make sure the database layer has its prerequisites: 

```
from mongita import MongitaClientDisk

client = MongitaClientDisk()

db = client.shopping_list_db
```

Now let's write some code to populate the database and test that code. Because we need to use get_items() without an ID (i.e. to fetch all items) we will also write that much code and test it. 

```
def setup_database():
    shopping_list_db.drop_collection(shopping_list_db.items_collection)
    items_collection = shopping_list_db.items_collection
    for item in ['apples', 'broccoli', 'pizza', 'tangerine', 'potatoes']:
        items_collection.insert_one({"description":item})

def get_items(id=None):
    items_collection = shopping_list_db.items_collection
    if id == None:
        items = items_collection.find({})
    return list(items)

def test_setup_database():
    print("testing setup_database()")
    setup_database()
    items = get_items()
    assert len(items) == 5
    descriptions = [item['description'] for item in items]
    for description in ['apples', 'broccoli', 'pizza', 'tangerine', 'potatoes']:
        assert description in descriptions

if __name__ == "__main__":
    test_setup_database()
```

This seems to work well. Now let's make sure we can get an item by its ID. So we expand `get_item(id)` to pay attention to the ID value. Note that IDs are generally used for search as mongo ObjectId instances, but outside of this database layer we will just use (and store and manipulate, etc.) the ID values as strings. 

_(Side note: Now I'm in a train station in Naples, Italy. Way better food than the train station in Cleveland, Ohio!)_

So to get the ID value of an item to work with, we will convert the ID values to strings before returning them from the `get_item()` function. 

Let's update the `get_items()` function to look like this, where we are adding an "id" value as expected to the returned list. This time, however, it's a string. 

```
def get_items(id=None):
    items_collection = shopping_list_db.items_collection
    if id == None:
        items = items_collection.find({})
    else:
        items = item_collection.find({"_id":id})
    items = list(items)
    for item in items:
        item["id"] = str(item["_id"])
    return items
```

And let's expand the test function to test the returned list. 

```
def test_get_items():
    print("testing get_items()")
    setup_database()
    items = get_items()
    assert type(items) is list
    assert len(items) > 0
    for item in items:
        assert 'id' in item
        assert type(item['id']) is str
        assert 'description' in item
        assert type(item['description']) is str

```

Once we get the returned list, we can get an ID from that list, and use it to test ID-based queries. 

So that adds some code to the test function.

```
    example_id = items[0]['id']
    example_description = items[0]['description']
    items = get_items(example_id)
    assert len(items) == 1
    assert example_id == items[0]['id']
    assert example_description == items[0]['description']
```

It won't yet work, because we are providing a string to the find function, not a Mongo ID object.  So lets change that line in the `get_items()` function. Before we do that, we need to get the ObjectId object definition: 

```
from bson.objectid import ObjectId
```

Then we can convert using something like this: 

```
myObjectId = ObjectId(myStringId)
```

So we will add that code into `get_items`: 

```
        items = items_collection.find({"_id":ObjectId(id)})
```

Here's the entire working part of the database layer so far. You can test this and make sure you're caught up. It's pretty easy from here. 

```
from mongita import MongitaClientDisk
from bson.objectid import ObjectId

client = MongitaClientDisk()

shopping_list_db = client.shopping_list_db

def setup_database():
    shopping_list_db.drop_collection(shopping_list_db.items_collection)
    items_collection = shopping_list_db.items_collection
    for item in ['apples', 'broccoli', 'pizza', 'tangerine', 'potatoes']:
        items_collection.insert_one({"description":item})

def get_items(id=None):
    items_collection = shopping_list_db.items_collection
    if id == None:
        items = items_collection.find({})
    else:
        items = items_collection.find({"_id":ObjectId(id)})
    items = list(items)
    for item in items:
        item["id"] = str(item["_id"])
    return items

def test_setup_database():
    print("testing setup_database()")
    setup_database()
    items = get_items()
    assert len(items) == 5
    descriptions = [item['description'] for item in items]
    for description in ['apples', 'broccoli', 'pizza', 'tangerine', 'potatoes']:
        assert description in descriptions

def test_get_items():
    print("testing get_items()")
    setup_database()
    items = get_items()
    assert type(items) is list
    assert len(items) > 0
    for item in items:
        assert 'id' in item
        assert type(item['id']) is str
        assert 'description' in item
        assert type(item['description']) is str
    example_id = items[0]['id']
    example_description = items[0]['description']
    items = get_items(example_id)
    assert len(items) == 1
    assert example_id == items[0]['id']
    assert example_description == items[0]['description']

if __name__ == "__main__":
    test_setup_database()
    test_get_items()
```

At this point, we can start adding in the other functions, and with TDD we write the tests first. Here's `add_item(description)`

```
def test_add_item():
    print("testing add_item()")
    setup_database()
    items = get_items()
    original_length = len(items)
    add_item("licorice")
    items = get_items()
    assert len(items) == original_length + 1
    descriptions = [item['description'] for item in items]
    assert "licorice" in descriptions
```
 And the implementation: 

 ```
 def add_item(description):
    items_collection = shopping_list_db.items_collection
    items_collection.insert_one({"description":description})
```

Here's the test for `delete_item`:

```
def test_delete_item():
    print("testing delete_item()")
    setup_database()
    items = get_items()
    original_length = len(items)
    deleted_description = items[1]['description']
    deleted_id = items[1]['id']
    delete_item(deleted_id)
    items = get_items()
    assert len(items) == original_length - 1
    for item in items:
        assert item['id'] != deleted_id
        assert item['description'] != deleted_description
```

...and the implementation:

```
def delete_item(id):
    items_collection = shopping_list_db.items_collection
    items_collection.delete_one({"_id":ObjectId(id)})

```

Note that here again we need to accept a string and convert to an ObjectId type. 

By this point, of course, we're including all the tests in the main code: 

```
if __name__ == "__main__":
    test_setup_database()
    test_get_items()
    test_add_item()
    test_delete_item()

```

Finally let's work on `update_item()`. Here's the test:

```
def test_update_item():
    print("testing update_item()")
    setup_database()
    items = get_items()
    original_description = items[1]['description']
    original_id = items[1]['id']
    update_item(original_id,"new-description")
    items = get_items()
    found = False
    for item in items:
        if item['id'] == original_id:
            assert item['description'] == "new-description"
            found = True
    assert found
```

We will need to pay attention to converting to ObjectId when necessary, and using the object ID to select elements and specifying the contents to update. 

```
def update_item(id, description):
    items_collection = shopping_list_db.items_collection
    where = {"_id": ObjectId(id)}
    updates = { "$set": { "description": description } }
    items_collection.update_one(where, updates)
```

The entire file can be found in the repo at `.../gamma/topic-05-mongita/database.py` and you are encouraged to run it to verify the tests. 

## The Web Application Layer

As it turns out, the web layer doesn't really care if you're using integers or strings as keys, as long as they are unique and can be passed as URL contents.  So the application as shown above works fine with no further modifications. Cool, right? 

## Conclusion

Since we have a fairly robust web application layer and our database layer does a good job of isolating database details from the application, this went pretty well. 

In the real world, you might want take a more detailed approach to this kind of information hiding -- there are cases where you can rely on Mongo to do things that you don't have to do manually in code, but in order to use them you have to let the app know you're doing that. Hiding so much of the capability that the app can't tell if you're using a relational or document database isn't playing to the strengths of either method. 

In the coming activities, we will be connecting to Mongo databases in the cloud. The code change to do this initially is only a few lines. 

So grab this code from the repo and try it out. See if you can play with it a bit. We already have homework asking you to get some basic things running. We will be asking for more complex Mongo capabilities in the near future. Getting the code running will help a lot!

As always, please let me know how this lecture-essay format is working for you, and send along any questions you might have!

