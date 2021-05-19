from flask import Flask, render_template, request, redirect, url_for # Importing flask and methods from the module that are used
import sqlite3 # Importing sqlite3
import itertools # Importing itertools for flattening lists

app = Flask(__name__)

con = sqlite3.connect('spells.db', check_same_thread=False) # Connecting to the .db file that contains all the database
con.execute("PRAGMA foreign_keys = 1")
cur = con.cursor()
con.row_factory = sqlite3.Row

cur.execute('DELETE FROM temp') # Resets the temp table
con.commit()

classes = { # Dictionary create to allow the correct class to be given to html elements when they are inserted into the table shown
  0:"id",
  1:"class",
  2:"level",
  3:"name",
  4:"school",
  5:"casting_time",
  6:"range",
  7:"component",
  8:"duration",
  9:"description",
}

class search_obj:
  def __init__(self, min_, max_, search, types_): # Sets variables search, types, min and max
    self.search = search
    self.types_ = types_
    self.min_ = int(min_)
    self.max_ = int(max_)
  

  def get_ids(self): # This method is used for getting specific ids from the spells table --------------- Carries out one iteration of the method below ----------
    self.search = f'"{self.search}"' 
    temp = []
    for type_ in self.types_:
      if(type_ != "id" and type_ != "class" and self.types_[type_] == "on"):
        cur.execute(f'SELECT id FROM spells WHERE {type_} LIKE {self.search} AND level > {self.min_ - 1} AND level < {self.max_ + 1}')
        results = list(itertools.chain(*cur.fetchall()))
        for i in results:
          temp.append(i)

    self.search = temp
    return self.search


  def multi_get_ids(self): # Gets ids based on multiple searches
    temp = []
    for type_ in self.types_: # Loops through all the types that are used in the search and carries out a search using that type
      if(type_ != "id" and type_ != "class" and self.types_[type_] == "on"): # Makes sure it is not an id search
        for result in self.search: # Loops through each item in the current search and checks if it is in the spells table
          result = f'"{result}"' # Adds quotes to the search so the sql will be (SELECT * FROM table WHERE type LIKE "search") with the quote otherwise it will not work
          cur.execute(f'SELECT id FROM spells WHERE {type_} LIKE {result} AND level > {int(self.min_) - 1} AND level < {int(self.max_) + 1}')
          result = list(itertools.chain(*cur.fetchall())) # Gets the results and then flattens the list
          for id_ in result: # Loops through all the current ids and appends them to the temp table
            temp.append(id_)
    self.search = temp # Sets the self.search to the results in the temp table so it is ready to be inserted into the temp table.


  def insert_id(self): # Inserts 1 id to the temp table
    cur.execute(f'SELECT spell_id FROM temp') #---- Gets current ids ----
    spell_ids = cur.fetchall()
    spell_ids = list(itertools.chain(*spell_ids))

    for i in spell_ids: # Loops through current ids
        if(i == self.search): # Checks if current id is already been searched for.
          break
    else:
      cur.execute(f'INSERT INTO temp (spell_id) VALUES ({self.search})') # Inserts id into temp table
    con.commit()


  def insert_multi_ids(self): # Inserts multiple ids
    cur.execute(f'SELECT spell_id FROM temp')
    spell_ids = cur.fetchall()
    spell_ids = list(itertools.chain(*spell_ids))

    for id_ in self.search: # Loops through all the ids in the search
      for i in spell_ids:# Checks if the current id is already the temp table and if it is it will break out of loop not allowing cur.execute to be called
        if(i == id_):
          break
      else:
        cur.execute(f'INSERT INTO temp (spell_id) VALUES ({id_})') # Inserts the id into temp table
    con.commit()

  def get_ids_from_class(self):
    
    temp = []
    self.search = f'"{self.search}"' 
    cur.execute(f'SELECT id FROM classes WHERE class LIKE {self.search}')
    
    id___ = cur.fetchone()[0]
    print("debug2")
    cur.execute(f'SELECT spell_id FROM class_spell_link WHERE class_id = {id___}')
    print("debug1")
    results = list(itertools.chain(*cur.fetchall()))
    self.search = results
      
@app.route('/')
def index():
  return redirect('/home')

# ----------------- https://blank/home --------------

@app.route('/home')
def home():
  return render_template('home.html')

#--------------- MULTI SEARCH -------------------


@app.route('/multisearch', methods=['POST', 'GET'])
def multisearch():
  if(request.method == 'POST'): #--------------------- RECEIVING INPUT (POST) --------------------
    search = request.form['search'] # Gets the input form the user
    multi = False # creates multi variable that will detirmine if someone has used "|" in their search
    min_ = request.form['min'] # Gets min level
    max_ = request.form['max'] # Gets max level
    types = { # A dictionary is created that will store what search types are to be used
      "id":"",
      "name":"",
      "class":"",
      "school":"",
      "casting_time":"",
      "range":"",
      "components":"",
      "duration":"",
    }

    # Handles search types (The value of a key in the dictionary will be set to off or on)
    for i in types:
      item = request.form.get(i)
      types[i] = str(item)


    for l in search: # Splits search into a list if there are "|" in it which means the user wants to do multiple searches at once
      if l == "|":
        search = list(search.split("|")) # Splits the search into a list using "|" to seperate items
        multi = True
        break

    find = search_obj(min_, max_, search, types) # creates the find object that stores all the variables above and contains methods to handle the data

    if(types["id"] == 'on'): # ------------------ ID SEARCH ---------------------
      try:
        if(multi): # Is multi search is being used e.g. "bard|cleric"?
          for id_ in find.search:# Checks if valid id is given (Throws error if id given is not a number and will break out of the try block)
            try:
              int(id_)
              
            except:
              find.search.remove(id_) # removes id from the search so it can be the list can be used in the find.insert_multi_ids()

          find.insert_multi_ids() # Inserts all the ids given by the user
        else:
          try:
            int(find.search) # Checks if valid id is given (Checks if it is a number)
            find.insert_id() # Inserts id given by the user
          except:
            print("Invalid id")

        #return redirect('/multisearch')
      except:
        print("Id Search failed")
        #return redirect('/multisearch')

    find.search = request.form['search']

    for l in find.search: # Resets the search back to include searches that are not just id's
      if l == "|":
        find.search = list(find.search.split("|"))
        multi = True
        break

    if(types["class"] == "on"):
      try:
        
        if(multi):
          for id_ in find.search:
            find.search = id_
            find.get_ids_from_class()
            find.insert_multi_ids()
        else:
          
          find.get_ids_from_class()
          find.insert_multi_ids()
      except:
        print("FAILED CLASS SEARCH")
          
    # --------------------- SCHOOL, NAME, ETC... SEARCH ---------------------
    

    find.search = request.form['search']

    for l in find.search: # Resets the search back to include searches that are not just id's
      if l == "|":
        find.search = list(find.search.split("|"))
        multi = True
        break

    try:
      if(multi):
        find.multi_get_ids() # Gets the ids from spells table
      else:
        find.get_ids() # Gets ids from spells table

      find.insert_multi_ids() # Inserts ids into the temp table for it to be displayed in the method='GET'

      return redirect('/multisearch')
    except:
      print("DEBUG")
      return redirect('/multisearch')

  else: # ------------------------------------------- Displaying Info (GET) --------------------------------------------
    result = []
    try:
      cur.execute(f'SELECT spell_id FROM temp') # Gets spell id's from temp table so the if statement below can check the length of it

      if(len(cur.fetchall()) == 1): # If there is only one spell found

        cur.execute(f'SELECT spell_id FROM temp') # Gets spell id from temp table
        spell_id = cur.fetchone()[0] # Fetches the id from query above

        cur.execute(f"SELECT * FROM spells WHERE id = {spell_id}") # Gathers information on any spells that are stored in temp table
        spell__ = list(itertools.chain(*cur.fetchall()))
        spell__.insert(1, "CLASS")
        result.append(spell__)
      else: # If multiple results are found in the temp table

        cur.execute(f'SELECT spell_id FROM temp') # Gets spells id's from temp table

        spell_id = cur.fetchall() # Fetches the data in [(id1), (id2)] format
        spell_id = list(itertools.chain(*spell_id)) # Flattens list
        
        result = [] # Initializing results list

        for num in spell_id: # Loops through the list that contains each spell id that needs to be queried
          cur.execute(f"SELECT * FROM spells WHERE id = {num}") # Gathers information on any spells thats ids were stored in temp table
          spell = list(itertools.chain(*cur.fetchall()))
          spell.insert(1, "CLASS")
          result.append(spell) # Appends the result from the query as a list to the results list

      # Converts list to html than can be inserted in the table on the webpage
      final = "" 
      i = 0

      #print(result)
      for row in result: # Loops through all the spells found in the temp table
        
        #print("done")
        final += "<tr>" # Adds a <tr> to mark the start of a row
        for column in row: # Loops through each aspect of the spell e.g. name, class, level

          if(classes[i] == "class"):
            # Get class of current spell
            column = ""
            cur.execute(f'SELECT class_id FROM class_spell_link WHERE spell_id = {row[0]}')
            ids___ = list(itertools.chain(*cur.fetchall()))
            
            for id___ in ids___:
              cur.execute(f'SELECT class FROM classes WHERE id = {id___}')

              column += f"{cur.fetchone()[0]}, "
                
          final = final + f" <td class='{classes[i]}'>{column}</td>" # Adds <td> tag to mark it as a column and adds a class, using i, so it can be collapsed with jquery
          i += 1 
        i = 0 # resets i
        final += "</tr>" # Closes the row with a </tr> tag

      # Returns render template with the final as the data to be put into the table len(result) as the amount of results and status as nothing
      return render_template('multi.html', info = final, status = "", results_found = len(result)) # returns render template with the html created above and amount of results taken as variables
    except:
      return render_template('multi.html', info = "", status = "There may have been an error while searching", results_found = 0)

@app.route('/clear')
def clear():
  cur.execute('DELETE FROM temp') # Resets the temp table so it is ready to have temporary data to be read by the 'GET' method later stored in it
  cur.execute('DELETE FROM sqlite_sequence WHERE name = "temp"')
  con.commit() # Commits the removal of the data in temp table
  return redirect('/multisearch') # Redirects back to "/multisearch"

if __name__ == "__main__":
  app.run(port=25565, debug=True)

