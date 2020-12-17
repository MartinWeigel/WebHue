from flask import Flask, render_template, redirect, url_for
from requests import Session
from config import HUE_IP, HUE_KEY, EXCLUDED_ROOMS
import json

HUE_URI = 'http://'+HUE_IP+'/api/'+HUE_KEY

app = Flask(__name__)
session = Session()

def get_all_scenes():
    response = session.get(url=HUE_URI+'/scenes/')
    return json.loads(response.text)

def get_scene(scene_id):
    response = session.get(url=HUE_URI+'/scenes/'+scene_id)
    return json.loads(response.text)

def get_all_groups():
    response = session.get(url=HUE_URI+'/groups')
    return json.loads(response.text)

def get_group(group_id):
    response = session.get(url=HUE_URI+'/groups/'+group_id)
    return json.loads(response.text)

def set_light(light_id, light_data):
    return session.put(
            url=HUE_URI+'/lights/'+light_id+'/state',
            data=light_data)

@app.route('/')
def main():
    groups = get_all_groups()
    all_scenes = get_all_scenes()

    # Filter list and only show living room scenes
    data = {}
    for group_id, group_data in groups.items():
        if group_id not in EXCLUDED_ROOMS and group_data['type'] == "Room":
            data[group_id] = {}
            data[group_id]['name'] = group_data['name']
            data[group_id]['scenes'] = {}
    for scene_id, scene_data in all_scenes.items():
        if scene_data['type'] == 'GroupScene' and scene_data['group'] in data:
            data[scene_data['group']]['scenes'][scene_id] = scene_data

    return render_template('index.html', groups=data)


@app.route('/scene/<scene_id>')
def scene(scene_id):
    scene_info = get_scene(scene_id)

    # Send commands
    for k, v in scene_info['lightstates'].items():
        set_light(k, json.dumps(v))

    return redirect(url_for('main'))


@app.route('/off/<group_id>')
def off(group_id):
    group_info = get_group(group_id)

    # Send commands
    for light in group_info['lights']:
        set_light(light, json.dumps({'on': False}))

    return redirect(url_for('main'))


if __name__ == '__main__':
    app.run(debug=True, port=8080)

