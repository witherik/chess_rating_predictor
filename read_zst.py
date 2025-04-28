import zstandard as zstd
import parameters
def read_zst_file_chunkwise(file_path, chunk_size=16384):
    with open(file_path, 'rb') as compressed:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(compressed) as reader:
            while True:
                chunk = reader.read(chunk_size)
                if not chunk:
                    break
                # Process the chunk
                yield chunk

if __name__ == '__main__':
    for chunk in read_zst_file_chunkwise(parameters.file_path):
        print(chunk)