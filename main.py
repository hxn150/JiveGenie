from mmhuman3d.core.conventions.keypoints_mapping import convert_kps
import pickle
import numpy as np
import sys
sys.path.append('/home/rgyhuang/private/JiveGenie/EDGE')
import EDGE_api
from mmhuman3d.core.visualization.visualize_keypoints2d import visualize_kp2d

# run generation algorithm
EDGE_api.run_edge_generation(
        feature_type='jukebox',
        out_length=5,
        processed_data_dir="./EDGE/data/dataset_backups/",
        render_dir="./EDGE/renders/",
        checkpoint="./EDGE/checkpoint.pt",
        music_dir="./EDGE/custom_music",
        save_motions=True,
        motion_save_dir="./EDGE/SMPL-to-FBX/motions/",
        cache_features=True,
        no_render=False,
        use_cached_features=True,
        feature_cache_dir="./EDGE/cache_features/"
        )

# load SMPL motion data from model inference
with open('./EDGE/SMPL-to-FBX/motions/test_track-A.pkl', 'rb') as f:
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
background = np.full((150, 1024, 1024, 3), 0)

visualize_kp2d(mapped_coordinates, data_source='smpl', image_array=background, output_path='outputs/test_track-A.mp4', resolution=(1024, 1024), overwrite=True) #remove_raw_file=False)
