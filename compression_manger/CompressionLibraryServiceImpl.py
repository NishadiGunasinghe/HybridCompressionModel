from compression_manger import CompressionLibraryOptions
from compression_manger.CompressionLibraryService import CompressionLibraryService, validate


class CompressionLibraryServiceImpl(CompressionLibraryService):

    def __init__(self):
        self.compressed_data = None
        self.decompressed_data = None
        self.compression_libs = []

    def register(self, compression_func, decompression_func, options: CompressionLibraryOptions):
        validate(options)
        name = options.get_attr('name')
        order = options.get_attr('order')
        options.remove_attr('name')
        options.remove_attr('order')
        if options.has_attributes():
            self.compression_libs.append(
                {
                    'name': name,
                    'compression_func': compression_func,
                    'decompression_func': decompression_func,
                    'order': order,
                    'func_options': options
                }
            )
        else:
            self.compression_libs.append(
                {
                    'name': name,
                    'compression_func': compression_func,
                    'decompression_func': decompression_func,
                    'order': order,
                    'func_options': None
                }
            )

    def compress(self, uncompressed_data: bytes):
        compression_libs = sorted(self.compression_libs, key=lambda x: x['order'])
        for compression_libs in compression_libs:
            compression_func = compression_libs['compression_func']
            func_options = compression_libs['func_options'].get_dict()
            if self.compressed_data is None:
                if func_options is None:
                    self.compressed_data = compression_func(uncompressed_data)
                else:
                    self.compressed_data = compression_func(uncompressed_data, **func_options)
            else:
                if func_options is None:
                    self.compressed_data = compression_func(self.compressed_data)
                else:
                    self.compressed_data = compression_func(self.compressed_data, **func_options)
        return self.compressed_data

    def decompress(self, compressed_data: bytes):
        compression_libs = sorted(self.compression_libs, key=lambda x: x['order'], reverse=True)
        for compression_libs in compression_libs:
            if self.decompressed_data is None:
                self.decompressed_data = compression_libs['decompression_func'](compressed_data)
            else:
                self.decompressed_data = compression_libs['decompression_func'](self.decompressed_data)
        return self.decompressed_data
