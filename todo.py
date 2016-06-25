import sqlite3
from bottle import route, run, debug, template, request, static_file, error, response, redirect

# only needed when you run Bottle on mod_wsgi
from bottle import default_app

def verify_user(func):
    def wrapper(*args, **kwargs):
        if not request.get_cookie('username'):
            return '<p style="color:red">You must have a username.</p>'
        return func(*args, **kwargs)
    return wrapper

@route('/todo')
def todo_list():

    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    # If the last_edited_by column has not been made yet
    try:
        c.execute("SELECT id, task, last_edited_by FROM todo WHERE status LIKE '1';")
    except sqlite3.OperationalError:
        c.execute("SELECT id, task FROM todo WHERE status LIKE '1';")
    result = c.fetchall()
    c.close()

    output = template('make_table', rows=result)
    return output

@route('/new', method='GET')
@verify_user
def new_item():

    if request.GET.get('save','').strip():
        username = request.get_cookie('username')
        new = request.GET.get('task', '').strip()
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        # If the column in the table has not been made yet
        try:
            c.execute("ALTER TABLE todo ADD last_edited_by character(20)")
        except sqlite3.OperationalError:
            pass
        c.execute("INSERT INTO todo (task,status,last_edited_by) VALUES (?,?,?)", (new,1,username))
        new_id = c.lastrowid

        conn.commit()
        c.close()

        return '<p>The new task was inserted into the database, the ID is %s</p>' % new_id

    else:
        return template('new_task.tpl')

@route('/edit/<no:int>', method='GET')
@verify_user
def edit_item(no):
    if request.GET.get('save','').strip():
        edit = request.GET.get('task','').strip()
        status = request.GET.get('status','').strip()

        conn = sqlite3.connect('todo.db')
        c = conn.cursor()

        if status == 'delete':
            c.execute("DELETE FROM todo WHERE id LIKE ?", (no,))
            conn.commit()

            return '<p>The item number %s was successfully deleted</p>' %no
        else:
            username = request.get_cookie('username')
            if status == 'open':
                status = 1
            else:
                status = 0

            # If the column in the table has not been made yet
            try:
                c.execute("ALTER TABLE todo ADD last_edited_by character(20)")
            except sqlite3.OperationalError:
                pass
            c.execute(
                "UPDATE todo SET task = ?, status = ?, last_edited_by = ? WHERE id LIKE ?", (edit,status,username,no))
            conn.commit()

            return '<p>The item number %s was successfully updated</p>' %no

    else:
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", (str(no)))
        cur_data = c.fetchone()

        return template('edit_task', old = cur_data, no = no)

@route('/item<item:re:[0-9]+>', method='GET')
def show_item(item):

    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT task FROM todo WHERE id LIKE ?", (item))
    result = c.fetchall()
    c.close()

    if request.GET.get('format','').strip() == 'json':
        if not result:
            return {'task':'This item number does not exist!'}
        else:
            return {'Task': result[0]}
    elif request.GET.get('format','').strip() == '':
        if not result:
            return 'This item number does not exist!'
        else:
            return 'Task: %s' %result[0]
    else:
        return 'The format can either be "json" or blank'

@route('/', method='GET')
def login():
    if request.GET.get('login', ''):
        username = request.GET.get('username', '')
        if not username:
            return template('login', err='You must provide a username')
        else:
            response.set_cookie('username', username)
            return redirect('/todo')
    else:
        return template('login', err='')

@route('/help')
def help():

    static_file('help.html', root='.')

@error(403)
def mistake403(code):
    return 'There is a mistake in your url!'

@error(404)
def mistake404(code):
    return 'Sorry, this page does not exist!'

debug(True)
run(reloader=True)
#remember to remove reloader=True and debug(True) when you move your application from development to a productive environment
