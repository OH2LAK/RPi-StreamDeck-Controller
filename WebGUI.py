from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from PIL import ImageFont

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('streamdeck.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    styles = conn.execute('SELECT * FROM styles').fetchall()
    button_configs = conn.execute('SELECT * FROM button_config').fetchall()
    conn.close()
    return render_template('index.html', styles=styles, button_configs=button_configs)

@app.route('/add_style', methods=('GET', 'POST'))
def add_style():
    if request.method == 'POST'):
        name = request.form['name']
        bg_color = request.form['bg_color']
        text_color = request.form['text_color']
        font_path = request.form['font_path']
        font_size = request.form['font_size']
        highlight_bg_color = request.form['highlight_bg_color']
        highlight_text_color = request.form['highlight_text_color']

        conn = get_db_connection()
        conn.execute('INSERT INTO styles (name, bg_color, text_color, font_path, font_size, highlight_bg_color, highlight_text_color) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (name, bg_color, text_color, font_path, font_size, highlight_bg_color, highlight_text_color))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_style.html')

@app.route('/add_button_config', methods=('GET', 'POST'))
def add_button_config():
    if request.method == 'POST':
        key = request.form['key']
        text = request.form['text']
        style = request.form['style']

        conn = get_db_connection()
        conn.execute('INSERT INTO button_config (key, text, style) VALUES (?, ?, ?)', (key, text, style))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn = get_db_connection()
    styles = conn.execute('SELECT name FROM styles').fetchall()
    conn.close()
    return render_template('add_button_config.html', styles=styles)

if __name__ == '__main__':
    app.run(debug=True)