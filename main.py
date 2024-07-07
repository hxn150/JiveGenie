from mmhuman3d.core.conventions.keypoints_mapping import convert_kps
import pickle
import numpy as np
import sys
sys.path.append('/home/rgyhuang/private/JiveGenie/EDGE')
import EDGE_api
from mmhuman3d.core.visualization.visualize_keypoints2d import visualize_kp2d
from flask import Flask, jsonify, request, session
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import os
import moviepy.editor as mpe

UPLOAD_FOLDER = './EDGE/custom_music'
MODEL_OUTPUT_FOLDER = './EDGE/SMPL-to-FBX/motions'
RESULT_OUT_FOLDER = 'outputs/'
ALLOWED_EXTENSIONS = {'.wav'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
@cross_origin()
def upload():
     # check if the post request has the file part
    target=os.path.join(UPLOAD_FOLDER)
    if not os.path.isdir(target):
        os.mkdir(target)
    file = request.files['file'] 
    filename = secure_filename(file.filename)
    destination="/".join([target, filename])
    file.save(destination)
    return jsonify({'reply':'success'})


@app.route('/generate_dance', methods=['POST'])
@cross_origin()
def main():
    if(os.listdir(UPLOAD_FOLDER) == 0):
        return jsonify({'reply': 'Error: No music files in directory!'})
    # run generation algorithm
    EDGE_api.run_edge_generation(
            feature_type='jukebox',
            out_length=10,
            processed_data_dir="./EDGE/data/dataset_backups/",
            render_dir="./EDGE/renders/",
            checkpoint="./EDGE/checkpoint.pt",
            music_dir=UPLOAD_FOLDER,
            save_motions=True,
            motion_save_dir="./EDGE/SMPL-to-FBX/motions/",
            cache_features=True,
            no_render=False,
            use_cached_features=False,
            feature_cache_dir="./EDGE/cache_features/"
            )

    # load SMPL motion data from model inference
    
    for filename in os.listdir(MODEL_OUTPUT_FOLDER):
        with open(f'./EDGE/SMPL-to-FBX/motions/{filename}', 'rb') as f:
            data = pickle.load(f)

        # scale from 3d to 2d coordinates
        frames, n, _ = np.shape(data['full_pose'])
        mapped_coordinates = np.zeros((frames, n, 2))

        for i in range(frames):
            for j in range(n):
                [x, y, z] = data['full_pose'][i][j]
                mapped_coordinates[i][j] = np.array([y, -z])

        # shifting and scaling size
        mapped_coordinates = 500 * mapped_coordinates + np.array([512, 1520])

        # black background
        # background = np.full((150, 1024, 1024, 3), 0)
        

        visualize_kp2d(mapped_coordinates, data_source='smpl', output_path=f'outputs/{filename[:-4]}.mp4', resolution=(1024, 1024), overwrite=True) #remove_raw_file=False)
        audio = mpe.AudioFileClip(f"{UPLOAD_FOLDER}/{filename[5:-4]}.wav")
        video1 = mpe.VideoFileClip(f'outputs/{filename[:-4]}.mp4')
        final = video1.set_audio(audio)
        final.write_videofile(f'outputs/{filename[:-4]}_sound.mp4')



    return jsonify({'reply':'success'})