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
      for result in self.search:
        result = f'"{result}"'
        cur.execute(f'SELECT id FROM spells WHERE {type_} LIKE {result} AND level > {int(self.min_) - 1} AND level < {int(self.max_) + 1} COLLATE NOCASE')
        self.search = list(itertools.chain(*cur.fetchall()))
        for id_ in self.search:
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
        if(multi):
          for id_ in find.search:# Checks if valid id is given (throws error if invalid breaking out of try block)
            int(id_)

          find.insert_multi_ids()
        else:
          int(find.search) # Checks if valid id is given

          find.insert_id()

        return redirect('/multisearch')
      except:
        return redirect('/multisearch')

    else: # --------------------- SCHOOL, NAME, ETC... SEARCH ---------------------
      try:
        if(multi):
          find.multi_get_ids()
        else:
          find.get_ids()

        find.insert_multi_ids()

        return redirect('/multisearch')
      except:
        return redirect('/multisearch')
  else:
    try:
      cur.execute(f'SELECT spell_id FROM temp') # Gets spell id's from temp table so the if statement below can check the length of it

      if(len(cur.fetchall()) == 1): # If there is only one id found

        cur.execute(f'SELECT spell_id FROM temp') # Gets spell id from temp table
        spell_id = cur.fetchone()[0] # Fetches the id from query above

        cur.execute(f"SELECT * FROM spells WHERE id = {spell_id}") # Gathers information on any spells that are stored in temp table
        result = cur.fetchall()
      else:

        cur.execute(f'SELECT spell_id FROM temp') # Gets spells id's from temp table

        spell_id = cur.fetchall() # Fetches the data in [(id1), (id2)] format
        spell_id = list(itertools.chain(*spell_id)) # Flattens list
        
        result = [] # Initializing results list

        for num in spell_id: # Loops through the list that contains each spell id that needs to be queried
          cur.execute(f"SELECT * FROM spells WHERE id = {num}") # Gathers information on any spells that are stored in temp table
          result.append(cur.fetchone()) # Appends the result from the query as a list to the results list

      # Converts list to table rows
      final = "" 
      i = 0
      for row in result:
        final += "<tr>"
        for column in row:
          final = final + f" <td class='{classes[i]}'>{column}</td>"
          i += 1
        i = 0
        final += "</tr>"

      # Returns render template with the final as the output
      return render_template('multi.html', info = final, results_found = len(result))
    except:
      return render_template('multi.html', info = "There may have been an error while searching", results_found = 0)



@app.route('/clear')
def clear():
  cur.execute('DELETE FROM temp') # Resets the temp table so it is ready to have temporary data to be read by the 'GET' method later stored in it
  con.commit() # commits the removal of the data in temp table
  return redirect('/multisearch')

if __name__ == "__main__":
  app.run(port=25565, debug=True)

