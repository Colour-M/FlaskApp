from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import itertools

app = Flask(__name__)

con = sqlite3.connect('spells.db', check_same_thread=False)
cur = con.cursor()
con.row_factory = sqlite3.Row

cur.execute('DELETE FROM temp') # Resets the temp table
con.commit()

classes = {
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
  def __init__(self, min_, max_, search, types_):
    self.search = search
    self.types_ = types_
    self.min_ = int(min_)
    self.max_ = int(max_)
    # for i in self.types_:
    #   print(i)
  

  def get_ids(self):
    self.search = f'"{self.search}"'
    temp = []
    for type_ in self.types_:
      if(type_ != "id" and self.types_[type_] == "on"):
        cur.execute(f'SELECT id FROM spells WHERE {type_} LIKE {self.search} AND level > {self.min_ - 1} AND level < {self.max_ + 1}')
        results = list(itertools.chain(*cur.fetchall()))
        
        for i in results:
          temp.append(i)
        

    self.search = temp
    return self.search


  def multi_get_ids(self):
    temp = []
    for type_ in self.types_:
      if(type_ != "id" and self.types_[type_] == "on"):
        for result in self.search:
          result = f'"{result}"'
          cur.execute(f'SELECT id FROM spells WHERE {type_} LIKE {result} AND level > {int(self.min_) - 1} AND level < {int(self.max_) + 1} COLLATE NOCASE')
          result = list(itertools.chain(*cur.fetchall()))
          for id_ in result:
            temp.append(id_)

    self.search = temp

  def insert_id(self):
    cur.execute(f'SELECT spell_id FROM temp')
    spell_ids = cur.fetchall()
    spell_ids = list(itertools.chain(*spell_ids))

    for i in spell_ids:
        if(i == self.search):
          break
    else:
      cur.execute(f'INSERT INTO temp (spell_id) VALUES ({self.search})')
    con.commit()

  def insert_multi_ids(self):
    cur.execute(f'SELECT spell_id FROM temp')
    spell_ids = cur.fetchall()
    spell_ids = list(itertools.chain(*spell_ids))

    for id_ in self.search:
      for i in spell_ids:
        if(i == id_):
          break
      else:
        cur.execute(f'INSERT INTO temp (spell_id) VALUES ({id_})') # Inserts the id's into temp table
    con.commit()



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
  if(request.method == 'POST'):
    search = request.form['search']
    multi = False
    min_ = request.form['min']
    max_ = request.form['max']
    types = {
      "id":"",
      "name":"",
      "class":"",
      "school":"",
      "casting_time":"",
      "range":"",
      "components":"",
      "duration":"",
    }

    # Handle search types
    for i in types:
      item = request.form.get(i)
      types[i] = str(item)


    for l in search: # Splits search into a list if there are | in it meaning the user wants to do multiple searches at once
      if l == "|":
        search = list(search.split("|"))
        multi = True
        break
    
    find = search_obj(min_, max_, search, types)

    if(types["id"] == 'on'): # ------------------ ID SEARCH ---------------------
      try:
        if(multi): # Is multi search is being used e.g. "bard|cleric"?
          for id_ in find.search:# Checks if valid id is given (Throws error if id given is not a number and will break out of the try block)
            int(id_)

          find.insert_multi_ids() # Inserts all the ids given by the user
        else:
          int(find.search) # Checks if valid id is given (Checks if it is a number)

          find.insert_id() # Inserts id given by the user

        return redirect('/multisearch')
      except:
        return redirect('/multisearch')

    else: # --------------------- SCHOOL, NAME, ETC... SEARCH ---------------------
      try:
        if(multi):
          find.multi_get_ids() # Gets the ids from spells table
        else:
          find.get_ids() # Gets ids from spells table

        find.insert_multi_ids() # Inserts ids into the temp table for it to be displayed in the method='GET'

        return redirect('/multisearch')
      except:
        return redirect('/multisearch')
  else: # ------------------------------------------- Displaying Info --------------------------------------------
    try:
      cur.execute(f'SELECT spell_id FROM temp') # Gets spell id's from temp table so the if statement below can check the length of it

      if(len(cur.fetchall()) == 1): # If there is only one spell found

        cur.execute(f'SELECT spell_id FROM temp') # Gets spell id from temp table
        spell_id = cur.fetchone()[0] # Fetches the id from query above

        cur.execute(f"SELECT * FROM spells WHERE id = {spell_id}") # Gathers information on any spells that are stored in temp table
        result = cur.fetchall()
      else: # If multiple results are found in the temp table

        cur.execute(f'SELECT spell_id FROM temp') # Gets spells id's from temp table

        spell_id = cur.fetchall() # Fetches the data in [(id1), (id2)] format
        spell_id = list(itertools.chain(*spell_id)) # Flattens list
        
        result = [] # Initializing results list

        for num in spell_id: # Loops through the list that contains each spell id that needs to be queried
          cur.execute(f"SELECT * FROM spells WHERE id = {num}") # Gathers information on any spells thats ids were stored in temp table
          result.append(cur.fetchone()) # Appends the result from the query as a list to the results list

      # Converts list to html than can be inserted in the table on the webpage
      final = "" 
      i = 0
      for row in result: # Loops through all the spells found in the temp table
        final += "<tr>" # Adds a <tr> to mark the start of a row
        for column in row: # Loops through each aspect of the spell
          final = final + f" <td class='{classes[i]}'>{column}</td>" # Adds <td> tag to mark it as a column and adds a class, using i, so it can be collapsed with jquery
          i += 1 
        i = 0 # resets i
        final += "</tr>" # Closes the row with a </tr> tag

      # Returns render template with the final as the output
      return render_template('multi.html', info = final, results_found = len(result)) # returns render template with the html created above and amount of results taken as variables
    except:
      return render_template('multi.html', info = "There may have been an error while searching", results_found = 0)

@app.route('/clear')
def clear():
  cur.execute('DELETE FROM temp') # Resets the temp table so it is ready to have temporary data to be read by the 'GET' method later stored in it
  con.commit() # commits the removal of the data in temp table
  return redirect('/multisearch')

if __name__ == "__main__":
  app.run(port=25565, debug=True)

