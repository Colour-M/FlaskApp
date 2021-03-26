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

def get_ids(search, type_, min_, max_):
  search = f'"{search}"'
  cur.execute(f'SELECT id FROM spells WHERE {type_} = {search} AND level > {int(min_) - 1} AND level < {int(max_) + 1}')
  ids_ = list(itertools.chain(*cur.fetchall()))
  return ids_

def multi_get_ids(search, type_, min, max):
  final = []
  for result in search:
    result = f'"{result}"'
    cur.execute(f'SELECT id FROM spells WHERE {type_} = {result} AND level > {int(min_) - 1} AND level < {int(max_) + 1}')
    ids_ = list(itertools.chain(*cur.fetchall()))
    for id_ in ids_:
      final.append(id_)
  

  return final



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
    search_type = request.form['type']
    multi = False
    min_ = request.form['min']
    max_ = request.form['max']

    for l in search:
      if l == "|":
        search = list(search.split("|"))
        multi = True
        break

    if(request.form['type'] == 'id'): # ------------------ ID SEARCH ---------------------
      try:
        if(multi == False):
          int(search) # throws error if user inputs any letters so it will break out of try except
        else:
          for id_ in search:
            int(id_)

        if(multi):
          for id_ in search:
            cur.execute(f'INSERT INTO temp (spell_id) VALUES ({id_})') # Inserts the id's into temp table
        else:
          cur.execute(f'INSERT INTO temp (spell_id) VALUES ({search})') # Inserts the id's into temp table
        
        con.commit() # Commits data to temp table
        return redirect('/multisearch') # Redirects back to the same address so 'GET' method will be called and data will be displayed

      except:
        return redirect('/multisearch')

    else: # --------------------- SCHOOL, NAME, ETC... SEARCH ---------------------
      try:

        if(multi == False):
          ids = get_ids(search, search_type, min_, max_)
        else:
          ids = multi_get_ids(search, search_type, min_, max_)


        for id_ in ids:
          cur.execute(f'INSERT INTO temp (spell_id) VALUES ({id_})') # Inserts the id's into temp table

        con.commit()

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

