from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('streamdeck.db')
    conn.row_factory = sqlite3.Row
    return conn

def execute_db_query(query, args=()):
    conn = get_db_connection()
    conn.execute(query, args)
    conn.commit()
    conn.close()

def get_connected_device():
    try:
        response = requests.get('http://localhost:5001/api/device_info')
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching device info: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
    return None

@app.route('/')
def index():
    conn = get_db_connection()
    device_info = get_connected_device()
    if device_info:
        button_count = device_info['button_count']
        styles = conn.execute('SELECT * FROM styles').fetchall()
        button_configs = conn.execute('SELECT * FROM button_config WHERE key < ?', (button_count,)).fetchall()
        parameters = conn.execute('SELECT * FROM parameters').fetchall()
    else:
        button_count = 0
        styles = []
        button_configs = []
        parameters = []
    conn.close()
    return render_template('index.html', device=device_info, button_count=button_count, styles=styles, button_configs=button_configs, parameters=parameters)

@app.route('/add_style', methods=('GET', 'POST'))
def add_style():
    if request.method == 'POST':
        name = request.form['name']
        normal_bg_color = request.form['normal_bg_color']
        normal_text_color = request.form['normal_text_color']
        normal_font_size = request.form['normal_font_size']
        short_press_bg_color = request.form['short_press_bg_color']
        short_press_text_color = request.form['short_press_text_color']
        short_press_font_size = request.form['short_press_font_size']
        long_press_bg_color = request.form['long_press_bg_color']
        long_press_text_color = request.form['long_press_text_color']
        long_press_font_size = request.form['long_press_font_size']

        execute_db_query('INSERT INTO styles (name, normal_bg_color, normal_text_color, normal_font_size, short_press_bg_color, short_press_text_color, short_press_font_size, long_press_bg_color, long_press_text_color, long_press_font_size) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                         (name, normal_bg_color, normal_text_color, normal_font_size, short_press_bg_color, short_press_text_color, short_press_font_size, long_press_bg_color, long_press_text_color, long_press_font_size))
        return redirect(url_for('index'))

    return render_template('add_style.html')

@app.route('/edit_style/<int:id>', methods=('GET', 'POST'))
def edit_style(id):
    conn = get_db_connection()
    style = conn.execute('SELECT * FROM styles WHERE id = ?', (id,)).fetchone()
    conn.close()

    if request.method == 'POST':
        normal_bg_color = request.form['normal_bg_color']
        normal_text_color = request.form['normal_text_color']
        normal_font_size = request.form['normal_font_size']
        short_press_bg_color = request.form['short_press_bg_color']
        short_press_text_color = request.form['short_press_text_color']
        short_press_font_size = request.form['short_press_font_size']
        long_press_bg_color = request.form['long_press_bg_color']
        long_press_text_color = request.form['long_press_text_color']
        long_press_font_size = request.form['long_press_font_size']

        execute_db_query('UPDATE styles SET normal_bg_color = ?, normal_text_color = ?, normal_font_size = ?, short_press_bg_color = ?, short_press_text_color = ?, short_press_font_size = ?, long_press_bg_color = ?, long_press_text_color = ?, long_press_font_size = ? WHERE id = ?',
                         (normal_bg_color, normal_text_color, normal_font_size, short_press_bg_color, short_press_text_color, short_press_font_size, long_press_bg_color, long_press_text_color, long_press_font_size, id))
        return redirect(url_for('index'))

    return render_template('edit_style.html', style=style)

@app.route('/delete_style/<int:id>', methods=('POST',))
def delete_style(id):
    conn = get_db_connection()
    style = conn.execute('SELECT * FROM styles WHERE id = ?', (id,)).fetchone()
    default_style = conn.execute('SELECT name FROM styles WHERE name = "Default"').fetchone()['name']
    conn.execute('UPDATE button_config SET style = ? WHERE style = ?', (default_style, style['name']))
    conn.execute('DELETE FROM styles WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/add_button_config', methods=('GET', 'POST'))
def add_button_config():
    if request.method == 'POST':
        device_id = request.form['device_id']
        key = request.form['key']
        text = request.form['text']
        style = request.form['style']
        short_press = request.form['short_press']
        long_press = request.form['long_press']
        ack_action = request.form['ack_action']

        try:
            execute_db_query('INSERT INTO button_config (device_id, key, text, style, short_press, long_press, ack_action) VALUES (?, ?, ?, ?, ?, ?, ?)',
                             (device_id, key, text, style, short_press, long_press, ack_action))
        except sqlite3.IntegrityError:
            execute_db_query('UPDATE button_config SET text = ?, style = ?, short_press = ?, long_press = ?, ack_action = ? WHERE device_id = ? AND key = ?',
                             (text, style, short_press, long_press, ack_action, device_id, key))
        return redirect(url_for('index'))

    conn = get_db_connection()
    styles = conn.execute('SELECT name FROM styles').fetchall()
    conn.close()
    return render_template('add_button_config.html', styles=styles)

@app.route('/edit_button_config/<int:id>', methods=('GET', 'POST'))
def edit_button_config(id):
    conn = get_db_connection()
    button_config = conn.execute('SELECT * FROM button_config WHERE id = ?', (id,)).fetchone()
    styles = conn.execute('SELECT name FROM styles').fetchall()
    conn.close()

    if request.method == 'POST':
        text = request.form['text']
        style = request.form['style']
        short_press = request.form['short_press']
        long_press = request.form['long_press']
        ack_action = request.form['ack_action']

        execute_db_query('UPDATE button_config SET text = ?, style = ?, short_press = ?, long_press = ?, ack_action = ? WHERE id = ?',
                         (text, style, short_press, long_press, ack_action, id))
        return redirect(url_for('index'))

    return render_template('edit_button_config.html', button_config=button_config, styles=styles)

@app.route('/edit_parameter/<int:id>', methods=('GET', 'POST'))
def edit_parameter(id):
    conn = get_db_connection()
    parameter = conn.execute('SELECT * FROM parameters WHERE id = ?', (id,)).fetchone()
    conn.close()

    if request.method == 'POST':
        value = request.form['value']
        execute_db_query('UPDATE parameters SET value = ? WHERE id = ?', (value, id))
        return redirect(url_for('index'))

    return render_template('edit_parameter.html', parameter=parameter)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)