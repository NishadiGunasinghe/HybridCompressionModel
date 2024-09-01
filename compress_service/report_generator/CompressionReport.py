from tabulate import tabulate

from Util import _FILE, _UNCOMPRESSED_FILE_SIZE, _FILE_SUMMARY, _COMPRESSION_NAME, \
    _FILE_COMPRESSED_TIME, \
    _COMPRESSED_FILE_SIZE, _FIRST_COMPRESSION, \
    _SECOND_COMPRESSION
from config.Configuration import Configuration


def generatev2(compression_report):
    if Configuration.COMPRESSED_REPORT:
        headers = [
            "Compression Stage",
            "Original File Size (MB)",
            "Compressed File Size (MB)",
            "Compression Time (ms)",
            "Compression Ratio",
            "Space Saving %",
            "Compression Speed (MB/s)"
        ]
    else:
        headers = [
            "Compression Stage",
            "Compression Name",
            "Original File Size (MB)",
            "Compressed File Size (MB)",
            "Compression Time (ms)",
            "Compression Ratio",
            "Space Saving %",
            "Compression Speed (MB/s)"
        ]

    string_report_content = '''
    <header> 
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous"> 
    </header
    '''
    string_report_content = string_report_content + "<br>"

    for file in compression_report:

        table_row = []
        string_report_content += f'''
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <p class="lead"> File Name: {file[_FILE]} | Actual File Size {file[_UNCOMPRESSED_FILE_SIZE] / (1024 * 1024)} MB </p>
                </div>
            </div>
        </div>
        '''

        first_compression_uncompressed_size = file[_FILE_SUMMARY][_FIRST_COMPRESSION][_UNCOMPRESSED_FILE_SIZE]
        first_compression_compressed_size = file[_FILE_SUMMARY][_FIRST_COMPRESSION][_COMPRESSED_FILE_SIZE]
        first_compression_compression_time = file[_FILE_SUMMARY][_FIRST_COMPRESSION][_FILE_COMPRESSED_TIME]
        if len(file[_FILE_SUMMARY]) > 1:
            second_compression_uncompressed_file = file[_FILE_SUMMARY][_SECOND_COMPRESSION][_UNCOMPRESSED_FILE_SIZE]
            second_compression_compressed_size = file[_FILE_SUMMARY][_SECOND_COMPRESSION][_COMPRESSED_FILE_SIZE]
            second_compression_compression_time = file[_FILE_SUMMARY][_SECOND_COMPRESSION][_FILE_COMPRESSED_TIME]
            if not Configuration.COMPRESSED_REPORT:
                table_row.append([
                    "Step 01",
                    file[_FILE_SUMMARY][_FIRST_COMPRESSION][_COMPRESSION_NAME],
                    first_compression_uncompressed_size / (1024 * 1024),
                    first_compression_compressed_size / (1024 * 1024),
                    first_compression_compression_time,
                    first_compression_uncompressed_size / first_compression_compressed_size,
                    (1 - (first_compression_compressed_size / first_compression_uncompressed_size)) * 100,
                    (first_compression_uncompressed_size - first_compression_compressed_size) /
                    (first_compression_compression_time * (1024 * 1024))
                ])

                table_row.append([
                    "Step 02",
                    file[_FILE_SUMMARY][_SECOND_COMPRESSION][_COMPRESSION_NAME],
                    second_compression_uncompressed_file / (1024 * 1024),
                    second_compression_compressed_size / (1024 * 1024),
                    second_compression_compression_time,
                    second_compression_uncompressed_file / second_compression_compressed_size,
                    (1 - (second_compression_compressed_size / second_compression_uncompressed_file)) * 100,
                    (second_compression_uncompressed_file - second_compression_compressed_size) /
                    (second_compression_compression_time * (1024 * 1024))
                ])
            if Configuration.COMPRESSED_REPORT:
                table_row.append([
                    "Total Compression",
                    first_compression_uncompressed_size / (1024 * 1024),
                    second_compression_compressed_size / (1024 * 1024),
                    second_compression_compression_time + first_compression_compression_time,
                    first_compression_uncompressed_size / second_compression_compressed_size,
                    (1 - (second_compression_compressed_size / first_compression_uncompressed_size)) * 100,
                    (first_compression_uncompressed_size - second_compression_compressed_size) /
                    ((second_compression_compression_time + first_compression_compression_time) * (1024 * 1024))
                ])
            else:
                table_row.append([
                    "Total Compression",
                    file[_FILE_SUMMARY][_SECOND_COMPRESSION][_COMPRESSION_NAME],
                    first_compression_uncompressed_size / (1024 * 1024),
                    second_compression_compressed_size / (1024 * 1024),
                    second_compression_compression_time + first_compression_compression_time,
                    first_compression_uncompressed_size / second_compression_compressed_size,
                    (1 - (second_compression_compressed_size / first_compression_uncompressed_size)) * 100,
                    (first_compression_uncompressed_size - second_compression_compressed_size) /
                    ((second_compression_compression_time + first_compression_compression_time) * (1024 * 1024))
                ])

            if not Configuration.COMPRESSED_REPORT:
                table_row.append([
                    "Improvement",
                    "",
                    "",
                    (second_compression_compressed_size - first_compression_compressed_size) / (1024 * 1024),
                    "",
                    (
                            first_compression_uncompressed_size / first_compression_compressed_size) - (
                            first_compression_uncompressed_size / second_compression_compressed_size),
                    (
                            (1 - (second_compression_compressed_size / first_compression_uncompressed_size)) * 100) - (
                            (1 - (first_compression_compressed_size / first_compression_uncompressed_size)) * 100),
                    ""
                ])

        else:
            table_row.append([
                "Total Compression",
                file[_FILE_SUMMARY][_FIRST_COMPRESSION][_COMPRESSION_NAME],
                first_compression_uncompressed_size / (1024 * 1024),
                first_compression_compressed_size / (1024 * 1024),
                first_compression_compression_time,
                first_compression_uncompressed_size /
                first_compression_compressed_size,
                (1 - (first_compression_compressed_size / first_compression_uncompressed_size)) * 100,
                (first_compression_uncompressed_size - first_compression_compressed_size) /
                (first_compression_compression_time * (1024 * 1024))
            ])

        string_report_content += f'''
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <table class="table table-striped table-bordered table-hover">{tabulate(table_row, headers=headers, tablefmt='html')[7:]}
                    </table>
                </div>
            </div>
        </div>
        '''

    string_report_content += "<br>"
    return string_report_content
