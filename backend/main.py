from mmhuman3d.core.conventions.keypoints_mapping import convert_kps
from mmhuman3d.core.visualization.visualize_keypoints2d import visualize_kp2d
import pickle
import numpy as np
import sys
sys.path.append('/home/rghuang/JiveGenie/backend/EDGE')
import EDGE_api
from flask import Flask, jsonify, request, Response, render_template
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import os
import moviepy.editor as mpe
import json
from pathlib import Path
import wave
import contextlib
import shutil
import io
import zipfile
import time

UPLOAD_FOLDER = './EDGE/custom_music'
MODEL_OUTPUT_FOLDER = './EDGE/SMPL-to-FBX/motions'
RESULT_OUT_FOLDER = '../frontend/outputs'
FEATURE_CACHE_DIR = './EDGE/cache_features' 
ALLOWED_EXTENSIONS = {'.wav'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@cross_origin()
def index():
    return render_template('index.html')

@app.route('/get_songs', methods=['GET'])
@cross_origin()
def getSongs():
    songs = os.listdir(UPLOAD_FOLDER)

    return Response(json.dumps(songs), mimetype='application/json')

@app.route('/delete_song', methods=['POST'])
@cross_origin()
def deleteSong():
    song_name = json.loads(request.data)['name']
    print(song_name)
    file = Path(f"{UPLOAD_FOLDER}/{song_name}/{song_name}.wav")
    if file.is_file():
        file.unlink()
    file = Path(f"{UPLOAD_FOLDER}/{song_name}")
    if file.rmdir():
        file.unlink()
    file = Path(f"{MODEL_OUTPUT_FOLDER}/{song_name}/test_{song_name}.pkl")
    if file.is_file():
        file.unlink()
    file = Path(f"{MODEL_OUTPUT_FOLDER}/{song_name}")
    if file.is_dir():
        file.rmdir()
    file = Path(f".EDGE/renders/test_{song_name}.mp4")
    if file.is_file():
        file.unlink()
    file = Path(f".EDGE/renders/test_{song_name}.wav")
    if file.is_file():
        file.unlink()
    file = Path(f"{RESULT_OUT_FOLDER}/test_{song_name}_sound.mp4")
    if file.is_file():
        file.unlink()
    file = Path(f"{FEATURE_CACHE_DIR}/{song_name}")
    if file.is_dir():
        shutil.rmtree(f"{FEATURE_CACHE_DIR}/{song_name}")
    
    return jsonify({'reply':'success'})
    

@app.route('/upload', methods=['POST'])
@cross_origin()
def upload():
     # check if the post request has the file part
    file = request.files['file'] 
    target=os.path.join(UPLOAD_FOLDER+f"/{file.filename[:-4]}")
    if not os.path.isdir(target):
        os.mkdir(target)
    filename = secure_filename(file.filename)
    destination="/".join([target, filename])
    file.save(destination)
    return jsonify({'reply':'success'})


@app.route('/generate_dance', methods=['POST'])
@cross_origin()
def main():
    if(os.listdir(UPLOAD_FOLDER) == 0):
        return jsonify({'reply': 'Error: No music files in directory!'})
    
    song = json.loads(request.data)['name']
    with contextlib.closing(wave.open(UPLOAD_FOLDER+f"/{song}/{song}.wav",'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames // rate
        print(duration)
    # run generation algorithm
    file = Path(f"./EDGE/cache_features/{song}")
    use_cache_features = True if file.is_dir() else False

    EDGE_api.run_edge_generation(
            feature_type='jukebox',
            out_length=duration,
            processed_data_dir="./EDGE/data/dataset_backups/",
            render_dir="./EDGE/renders/",
            checkpoint="./EDGE/checkpoint.pt",
            music_dir=f"{UPLOAD_FOLDER}/{song}",
            save_motions=True,
            motion_save_dir=f"{MODEL_OUTPUT_FOLDER}/{song}",
            cache_features=True,
            no_render=False,
            use_cached_features=use_cache_features,
            feature_cache_dir=f"./EDGE/cache_features/{song}"
            )

    # load SMPL motion data from model inference
    for filename in os.listdir(f"{MODEL_OUTPUT_FOLDER}/{song}"):
        with open(f"{MODEL_OUTPUT_FOLDER}/{song}/test_{song}.pkl", 'rb') as f:
            data = pickle.load(f)

        # scale from 3d to 2d coordinates
        frames, n, _ = np.shape(data['full_pose'])
        mapped_coordinates = np.zeros((frames, n, 2))

        for i in range(frames):
            for j in range(n):
                [x, y, z] = data['full_pose'][i][j]
                mapped_coordinates[i][j] = np.array([x, -z])

        # shifting and scaling size
        mapped_coordinates = 400 * mapped_coordinates + np.array([512, 1300])

        # black background
        # background = np.full((150, 1024, 1024, 3), 0)
        

        visualize_kp2d(mapped_coordinates, data_source='smpl', output_path=f'{RESULT_OUT_FOLDER}/{filename[:-4]}.mp4', resolution=(1024, 1024), overwrite=True) #remove_raw_file=False)
        audio = mpe.AudioFileClip(f"{UPLOAD_FOLDER}/{song}/{song}.wav")
        video1 = mpe.VideoFileClip(f'{RESULT_OUT_FOLDER}/{filename[:-4]}.mp4')
        final = video1.set_audio(audio)
        final.write_videofile(f'{RESULT_OUT_FOLDER}/{filename[:-4]}_sound.mp4')
        # remove redundant soundless file
        os.remove(f'{RESULT_OUT_FOLDER}/{filename[:-4]}.mp4')


    return jsonify({'reply':'success'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8080', debug=True)