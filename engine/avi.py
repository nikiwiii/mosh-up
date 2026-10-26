import struct

# MPEG-4 Video Object Plane (VOP) header start code
VOP_START_CODE = b'\x00\x00\x01\xb6'

# MPEG-4 VOP Types
VOP_TYPE_I = 0  # Intra-frame (Keyframe)
VOP_TYPE_P = 1  # Predicted frame (Motion delta)
VOP_TYPE_B = 2  # Bidirectional frame
VOP_TYPE_S = 3  # Sprite / GMC frame


def find_video_frames(data):
    """
    Scans raw bytearray for AVI video stream chunks ('00dc').
    Returns a list of tuples: (pos, chunk_size).
    """
    frames = []
    pos = 0
    data_len = len(data)
    while True:
        pos = data.find(b'00dc', pos)
        if pos == -1:
            break
        if pos + 8 <= data_len:
            chunk_size = struct.unpack('<I', data[pos+4:pos+8])[0]
            frames.append((pos, chunk_size))
            pos += 8 + chunk_size
        else:
            pos += 4
    return frames


def find_vop(payload):
    """
    Finds MPEG-4 VOP start code in payload.
    Returns (vop_idx, vop_type) or (-1, None) if not found.
    vop_type: 0 = I-frame, 1 = P-frame, 2 = B-frame, 3 = S-frame.
    """
    vop_idx = payload.find(VOP_START_CODE)
    if vop_idx != -1 and vop_idx + 4 < len(payload):
        vop_type = (payload[vop_idx + 4] & 0xC0) >> 6
        return vop_idx, vop_type
    return -1, None


def is_iframe(payload):
    """Returns True if the MPEG-4 payload contains an I-frame VOP."""
    _, vop_type = find_vop(payload)
    return vop_type == VOP_TYPE_I


def is_pframe(payload):
    """Returns True if the MPEG-4 payload contains a P-frame VOP."""
    _, vop_type = find_vop(payload)
    return vop_type == VOP_TYPE_P


def parse_avi_chunks(data):
    """
    Parses chunks inside LIST movi and finds idx1 position.
    Returns (movi_pos, idx1_pos, frames), where frames is a list of (chunk_id, pos, chunk_size).
    """
    frames = []
    movi_pos = data.find(b'LIST')
    while movi_pos != -1:
        if movi_pos + 12 <= len(data) and data[movi_pos+8:movi_pos+12] == b'movi':
            break
        movi_pos = data.find(b'LIST', movi_pos + 4)

    pos = movi_pos + 12 if movi_pos != -1 else 0
    idx1_pos = data.find(b'idx1')
    limit = idx1_pos if idx1_pos != -1 else len(data)

    while pos < limit:
        chunk_id = data[pos:pos+4]
        if chunk_id in (b'00dc', b'01wb', b'00db'):
            if pos + 8 <= len(data):
                c_size = struct.unpack('<I', data[pos+4:pos+8])[0]
                frames.append((chunk_id, pos, c_size))
                pos += 8 + c_size + (c_size % 2)
            else:
                break
        else:
            pos += 1

    return movi_pos, idx1_pos, frames


def update_avi_headers(modified_data, movi_pos, total_video_frames):
    """
    Patches avih dwTotalFrames, LIST movi size, and RIFF header length in modified AVI bytearray.
    """
    # Update avih dwTotalFrames
    avih_pos = modified_data.find(b'avih')
    if avih_pos != -1 and avih_pos + 24 <= len(modified_data):
        struct.pack_into('<I', modified_data, avih_pos + 20, total_video_frames)

    # Update LIST movi size
    if movi_pos != -1 and movi_pos + 8 <= len(modified_data):
        new_movi_size = len(modified_data) - (movi_pos + 8)
        struct.pack_into('<I', modified_data, movi_pos + 4, new_movi_size)

    # Update RIFF header size
    if len(modified_data) >= 8:
        struct.pack_into('<I', modified_data, 4, len(modified_data) - 8)
