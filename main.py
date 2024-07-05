from keypoints_map import convert_kps
import pickle
import numpy as np

with open('./EDGE/SMPL-to-FBX/motions/test_trackA.pkl', 'rb') as f:
    data = pickle.load(f)

keypoints_human, mask = convert_kps(data['full_pose'])

print(keypoints_human)
print(mask)

# keypoints_orig, _ = convert_kps(keypoints_human, src="human_data", dst="smpl")

# print(keypoints_orig)