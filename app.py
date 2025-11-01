import io
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, join_room, emit
from convert import convert_to_paragraphs

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'dev'
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='eventlet')

# Simple in-memory single-run store
ACTIVE = {
    'script': [], # Current script paragraphs
    'position': 0, # Current scroll position
    'font_size': None, # Current font size (None lets prompter use its default)
    'speed': 0, # Default scroll speed
    'scrolling': False, # Is it currently scrolling?
    'font': 'OpenDyslexic', # Default font family
    'uppercase': False # Is text forced to uppercase?
}

# track connected prompter client session ids
PROMPTER_CLIENTS = set()

@app.route('/')
def control():
    return render_template('control.html')

@app.route('/prompter')
def prompter():
    return render_template('prompter.html')

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('file')
    if not f:
        return redirect(url_for('control'))
    data = f.read()
    paragraphs = convert_to_paragraphs(data, f.filename)
    # store
    ACTIVE['script'] = paragraphs
    ACTIVE['position'] = 0
    ACTIVE['scrolling'] = False
    ACTIVE['speed'] = 0
    # autoscale checkbox comes in form data if present
    autoscale = bool(request.form.get('autoscale'))
    # notify connected prompters; include autoscale flag so prompter can auto-fit
    socketio.emit('control_event', {'type': 'load', 'paragraphs': paragraphs, 'autoscale': autoscale}, room='prompter')
    # broadcast status update
    socketio.emit('status', {'prompter_count': len(PROMPTER_CLIENTS), 'script_len': len(paragraphs), 'scrolling': ACTIVE['scrolling']})
    return redirect(url_for('control'))

@app.route('/state')
def state():
    return jsonify({
        'script': ACTIVE['script'],
        'position': ACTIVE['position'],
        'scrolling': ACTIVE['scrolling'],
        'font': ACTIVE['font'],
        'uppercase': ACTIVE['uppercase'],
        'prompter_count': len(PROMPTER_CLIENTS)
    })

@socketio.on('control_event')
def on_control_event(data):
    # Validate minimal shape
    t = data.get('type')
    if not t:
        return
    # Keep server state for position/font if provided
    if t == 'set_position':
        ACTIVE['position'] = data.get('pos', ACTIVE['position'])
    if t == 'set_font_size':
        ACTIVE['font_size'] = data.get('size')
    if t == 'scroll':
        speed = data.get('speed', -1) # Use -1 to distinguish from explicit 0
        if speed >= 0:
            ACTIVE['speed'] = speed
        ACTIVE['scrolling'] = bool(ACTIVE['speed'])
    if t == 'set_font':
        ACTIVE['font'] = data.get('font', 'OpenDyslexic')
    if t == 'set_uppercase':
        ACTIVE['uppercase'] = data.get('enabled', False)

    # Broadcast to prompter clients
    emit('control_event', data, room='prompter')
    # Broadcast status to listening controls too
    socketio.emit('status', {
        'prompter_count': len(PROMPTER_CLIENTS),
        'script_len': len(ACTIVE['script']),
        'scrolling': ACTIVE.get('scrolling', False),
        'speed': ACTIVE.get('speed', 0)
    })


@socketio.on('join')
def on_join(data):
    # single room for now
    join_room('prompter')
    # send current script
    emit('control_event', {'type': 'load', 'paragraphs': ACTIVE['script']}, to=request.sid)
    # track this client
    try:
        PROMPTER_CLIENTS.add(request.sid)
    except Exception:
        pass
    # broadcast updated status to all controls
    emit('status', {
        'prompter_count': len(PROMPTER_CLIENTS),
        'script_len': len(ACTIVE['script']),
        'scrolling': ACTIVE.get('scrolling', False),
        'speed': ACTIVE.get('speed', 0)
    }, broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    # remove if it was a prompter
    try:
        if request.sid in PROMPTER_CLIENTS:
            PROMPTER_CLIENTS.remove(request.sid)
            emit('status', {
                'prompter_count': len(PROMPTER_CLIENTS),
                'script_len': len(ACTIVE['script']),
                'scrolling': ACTIVE.get('scrolling', False),
                'speed': ACTIVE.get('speed', 0)
            }, broadcast=True)
    except Exception:
        pass

if __name__ == '__main__':
    # Use eventlet for SocketIO
    socketio.run(app, host='0.0.0.0', port=5000)