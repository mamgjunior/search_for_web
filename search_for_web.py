from flask import Flask, render_template, request, escape, session, copy_current_request_context
from vsearch import search_for_letters
from time import sleep
from threading import Thread

from DBcm import UseDataBase, ConnectionError, CredentialsError, SQLError
from checker import check_logged_in

app = Flask(__name__)

app.secret_key = 'YouWillNeverGuessMySecretKey'

app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'root',
                          'password': '637485tfs',
                          'database': 'vsearchloDb'}


@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    return 'You are now logged in.'


@app.route('/logout')
def do_logout() -> str:
    session.pop('logged_in')
    return 'You are now logged out.'

@app.route('/search4', methods=['POST'])
def do_search() -> 'html':

    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:
        sleep(15) # This makes log_request really slow...
        with UseDataBase(app.config['dbconfig']) as cursor:
            _SQL = """ insert into log(phrase, letters, ip, browser_string, results) values (%s, %s, %s, %s, %s)"""
            cursor.execute(_SQL, (req.form['phrase'], req.form['letters'], req.remote_addr, req.user_agent.browser, res, ))

    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Here are your results:'
    results = str(search_for_letters(phrase, letters))

    try:
        t = Thread(target=log_request, args=(request, results))
        t.start()
        # log_request(request, results)
    except Exception as err:
        print('Ops, Logging failed with this error:', str(err))

    return render_template('results.html', the_title=title, the_phrase=phrase, the_letters=letters, the_results=results)


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html', the_title='Welcome to search for letters on the web!')


@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    """Display the contents of the log file as a HTML table."""
    try:
        with UseDataBase(app.config['dbconfig']) as cursor:
            _SQL = """SELECT phrase, letters, ip, browser_string, results FROM log"""
            cursor.execute(_SQL)
            contents = cursor.fetchall()     

        titles = ['Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results']
        return render_template('viewlog.html', the_title='View log', the_row_title=titles, the_date=contents)
    except ConnectionError as err:
        print('Is your database switched on? Error:', str(err))
    except CredentialsError as err:
        print('User-id/Password issues. Error:', str(err))   
    except SQLError as err:
        print('Is your query correct? Error:', str(err))
    except Exception as err:
        print('Something went wrong:', str(err))    


if __name__ == '__main__':
    app.run(debug=True)
