from mmhuman3d.core.conventions.keypoints_mapping import convert_kps
import pickle
import numpy as np
# from EDGE.test import run_edge_generation
from mmhuman3d.core.visualization.visualize_keypoints3d import visualize_kp3d
from mmhuman3d.core.visualization.visualize_keypoints2d import visualize_kp2d
# from mmhuman3d.core.visualization.visualize_smpl import visualize_smpl_pose

# run_edge_generation(
#         feature_type='jukebox',
#         out_length=5,
#         processed_data_dir="data/dataset_backups/",
#         render_dir="renders/",
#         checkpoint="checkpoint.pt",
#         music_dir="custom_music/",
#         save_motions=True,
#         motion_save_dir="motions/",
#         cache_features=True,
#         no_render=False,
#         use_cached_features=True,
#         feature_cache_dir="cache_features/"
#         )

with open('./EDGE/SMPL-to-FBX/motions/test_track-A.pkl', 'rb') as f:
    data = pickle.load(f)

print(np.shape(data['smpl_poses']))
print(np.shape(data['smpl_trans']))
print(np.shape(data['full_pose']))
# keypoints_coco, mask = convert_kps(data['full_pose'], src='smpl', dst='coco')

# print(data['full_pose'])
frames, n, _ = np.shape(data['full_pose'])
mapped_coordinates = np.zeros((frames, n, 2))

for i in range(frames):
    for j in range(n):
        [x, y, z] = data['full_pose'][i][j]
        mapped_coordinates[i][j] = np.array([y, -z])

mapped_coordinates = 500 * mapped_coordinates + np.array([512, 1520])


# print(keypoints_coco)
print(mapped_coordinates)
# # print(keypoints_human)
# # print(mask)
background = np.full((150, 1024, 1024, 3), 0)

visualize_kp2d(mapped_coordinates, data_source='smpl', image_array=background, output_path='test_track-A.mp4', resolution=(1024, 1024), overwrite=True, remove_raw_file=False)
# visualize_kp3d(data['full_pose'], data_source='smpl', output_path='some_video.mp4', resolution=(1024, 1024))
# body_model_config = dict(
#     type='smpl', model_path='./SMPL_NEUTRAL.pkl')
# visualize_smpl_pose(
#     poses=data['smpl_poses'],
#     output_path='smpl.mp4',
#     resolution=(1024, 1024))