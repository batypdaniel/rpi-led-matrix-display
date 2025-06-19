from flask import Flask, request, render_template_string
from display_state import display_state

app = Flask(__name__)

@app.route('/')
def home():
    html = """
    <h2>Select Display</h2>
    <form method='POST' action='/set_display'>
        <select name='display'>
            <option value='Spotify (With Track/Artist Info)'>Spotify (With Track/Artist Info)</option>
            <option value='Spotify (Full-Screen Album Art'>Spotify (Full-Screen Album Art)</option>
            <option value='Time'>Time</option>
            <option value='ESPN Ticker'>ESPN Ticker</option>
            <option value='Weather'>Weather</option>
        </select>
        <input type='submit' value='Switch'>
    </form>
    <h2>Send Custom Text</h2>
    <form method='POST' action='/set_text'>
        <input type='text' name='custom_text' maxlength='100'/>
        <input type='submit' value='Send'>
    </form>
    <p>Current text: {{ current_text }}</p>
    <p>Current display: {{ current_display }}</p>
    """
    return render_template_string(html, current_text=display_state.custom_text, current_display=display_state.current_app_label)

@app.route('/set_display', methods=['POST'])
def set_display():
    idx = request.form.get('display', 0)
    display_state.current_app_label = idx
    return f"Switched display to {idx}. <a href='/'>Go back</a>"

@app.route('/set_text', methods=['POST'])
def set_text():
    text = request.form.get('custom_text', '')
    display_state.custom_text = text
    display_state.current_app_label = "Custom Text"
    return f"Switched display to Custom Text.  Text set to: {text} <a href='/'>Go back</a>"