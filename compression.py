import lz4.frame

def compress_data(data):
    return lz4.frame.compress(data.encode('utf-8'))

def decompress_data(data):
    return lz4.frame.decompress(data).decode('utf-8')
