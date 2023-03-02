from flask import Flask, render_template, request
from main import main
import os

app = Flask(__name__)

@app.route('/search4', methods=['POST'])
def create_map():
    name = request.form['name']
    title = 'Here are your results:'
    results = main(name)
    return render_template('vlad.html', the_name = name, the_title = title, the_results = results)

def remover():
    os.remove('templates/vlad.html')

@app.route('/')
@app.route('/entry')
def entry_page():
    return render_template('entry.html', the_title = 'Welcome to my web')

if __name__ == '__main__':
    app.run(debug=True)