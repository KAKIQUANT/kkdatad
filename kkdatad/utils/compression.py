import lz4.frame

def compress_data(data):
    return lz4.frame.compress(data)

def decompress_data(data):
    return lz4.frame.decompress(data)
