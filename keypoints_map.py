from collections import defaultdict
from typing import List, Tuple, Union

import numpy as np
import torch

import openpose, smpl, human_data

KEYPOINTS_FACTORY = {
    'human_data': human_data.HUMAN_DATA,
    'smpl': smpl.SMPL_KEYPOINTS,
    'openpose_137': openpose.OPENPOSE_137_KEYPOINTS,
}

__KEYPOINTS_MAPPING_CACHE__ = defaultdict(dict)

def convert_kps(
    keypoints: Union[np.ndarray, torch.Tensor],
    src: str = 'smpl',
    dst: str = 'openpose_137',
    approximate: bool = False,
    mask: Union[np.ndarray, torch.Tensor] = None,
    keypoints_factory: dict = KEYPOINTS_FACTORY,
    return_mask: bool = True
) -> Tuple[Union[np.ndarray, torch.Tensor], Union[np.ndarray, torch.Tensor]]:
    """Convert keypoints following the mapping correspondence between src and
    dst keypoints definition. Supported conventions by now: agora, coco, smplx,
    smpl, mpi_inf_3dhp, mpi_inf_3dhp_test, h36m, h36m_mmpose, pw3d, mpii, lsp.
    Args:
        keypoints [Union[np.ndarray, torch.Tensor]]: input keypoints array,
            could be (f * n * J * 3/2) or (f * J * 3/2).
            You can set keypoints as np.zeros((1, J, 2))
            if you only need mask.
        src (str): source data type from keypoints_factory.
        dst (str): destination data type from keypoints_factory.
        approximate (bool): control whether approximate mapping is allowed.
        mask (Union[np.ndarray, torch.Tensor], optional):
            The original mask to mark the existence of the keypoints.
            None represents all ones mask.
            Defaults to None.
        keypoints_factory (dict, optional): A class to store the attributes.
            Defaults to keypoints_factory.
        return_mask (bool, optional): whether to return a mask as part of the
            output. It is unnecessary to return a mask if the keypoints consist
            of confidence. Any invalid keypoints will have zero confidence.
            Defaults to True.
    Returns:
        Tuple[Union[np.ndarray, torch.Tensor], Union[np.ndarray, torch.Tensor]]
            : tuple of (out_keypoints, mask). out_keypoints and mask will be of
            the same type.
    """
    assert keypoints.ndim in {3, 4}
    if isinstance(keypoints, torch.Tensor):

        def new_array_func(shape, value, device_data, if_uint8):
            if if_uint8:
                dtype = torch.uint8
            else:
                dtype = None
            if value == 1:
                return torch.ones(
                    size=shape, dtype=dtype, device=device_data.device)
            elif value == 0:
                return torch.zeros(
                    size=shape, dtype=dtype, device=device_data.device)
            else:
                raise ValueError

        def to_type_uint8_func(data):
            return data.to(dtype=torch.uint8)

    elif isinstance(keypoints, np.ndarray):

        def new_array_func(shape, value, device_data, if_uint8):
            if if_uint8:
                dtype = np.uint8
            else:
                dtype = None
            if value == 1:
                return np.ones(shape=shape)
            elif value == 0:
                return np.zeros(shape=shape, dtype=dtype)
            else:
                raise ValueError

        def to_type_uint8_func(data):
            return data.astype(np.uint8)

    else:
        raise TypeError('Type of keypoints is neither' +
                        ' torch.Tensor nor np.ndarray.\n' +
                        f'Type of keypoints: {type(keypoints)}')

    if mask is not None:
        assert type(mask) == type(keypoints)
    else:
        mask = new_array_func(
            shape=(keypoints.shape[-2], ),
            value=1,
            device_data=keypoints,
            if_uint8=True)

    if src == dst:
        if return_mask:
            return keypoints, mask
        else:
            return keypoints

    src_names = keypoints_factory[src.lower()]
    dst_names = keypoints_factory[dst.lower()]
    extra_dims = keypoints.shape[:-2]
    keypoints = keypoints.reshape(-1, len(src_names), keypoints.shape[-1])

    out_keypoints = new_array_func(
        shape=(keypoints.shape[0], len(dst_names), keypoints.shape[-1]),
        value=0,
        device_data=keypoints,
        if_uint8=False)

    original_mask = mask
    if original_mask is not None:
        original_mask = original_mask.reshape(-1)
        assert original_mask.shape[0] == len(
            src_names), f'The length of mask should be {len(src_names)}'

    mask = new_array_func(
        shape=(len(dst_names), ),
        value=0,
        device_data=keypoints,
        if_uint8=True)

    dst_idxs, src_idxs, _ = \
        get_mapping(src, dst, approximate, keypoints_factory)
    out_keypoints[:, dst_idxs] = keypoints[:, src_idxs]
    out_shape = extra_dims + (len(dst_names), keypoints.shape[-1])
    out_keypoints = out_keypoints.reshape(out_shape)
    mask[dst_idxs] = to_type_uint8_func(original_mask[src_idxs]) \
        if original_mask is not None else 1.0

    if return_mask:
        return out_keypoints, mask
    else:
        return out_keypoints


def get_mapping(src: str,
                dst: str,
                approximate: bool = False,
                keypoints_factory: dict = KEYPOINTS_FACTORY):
    """Get mapping list from src to dst.

    Args:
        src (str): source data type from keypoints_factory.
        dst (str): destination data type from keypoints_factory.
        approximate (bool): control whether approximate mapping is allowed.
        keypoints_factory (dict, optional): A class to store the attributes.
            Defaults to keypoints_factory.

    Returns:
        list:
            [src_to_intersection_idx, dst_to_intersection_index,
             intersection_names]
    """
    if src in __KEYPOINTS_MAPPING_CACHE__ and \
        dst in __KEYPOINTS_MAPPING_CACHE__[src] and \
            __KEYPOINTS_MAPPING_CACHE__[src][dst][3] == approximate:
        return __KEYPOINTS_MAPPING_CACHE__[src][dst][:3]
    else:
        src_names = keypoints_factory[src.lower()]
        dst_names = keypoints_factory[dst.lower()]

        dst_idxs, src_idxs, intersection = [], [], []
        unmapped_names, approximate_names = [], []
        for dst_idx, dst_name in enumerate(dst_names):
            matched = False
            try:
                src_idx = src_names.index(dst_name)
            except ValueError:
                src_idx = -1
            if src_idx >= 0:
                matched = True
                dst_idxs.append(dst_idx)
                src_idxs.append(src_idx)
                intersection.append(dst_name)
            # approximate mapping
            if approximate and not matched:

                try:
                    part_list = human_data.APPROXIMATE_MAP[dst_name]
                except KeyError:
                    continue
                for approximate_name in part_list:
                    try:
                        src_idx = src_names.index(approximate_name)
                    except ValueError:
                        src_idx = -1
                    if src_idx >= 0:
                        dst_idxs.append(dst_idx)
                        src_idxs.append(src_idx)
                        intersection.append(dst_name)
                        unmapped_names.append(src_names[src_idx])
                        approximate_names.append(dst_name)
                        break

        if unmapped_names:
            warn_message = \
                f'Approximate mapping {unmapped_names}' +\
                f' to {approximate_names}'

        mapping_list = [dst_idxs, src_idxs, intersection, approximate]

        if src not in __KEYPOINTS_MAPPING_CACHE__:
            __KEYPOINTS_MAPPING_CACHE__[src] = {}
        __KEYPOINTS_MAPPING_CACHE__[src][dst] = mapping_list
        return mapping_list[:3]






