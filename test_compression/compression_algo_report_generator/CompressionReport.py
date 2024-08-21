from tabulate import tabulate
from test_compression.Util import _FILE, _UNCOMPRESSED_FILE_SIZE, _FILE_SUMMARY, _COMPRESSION_NAME, \
    _FILE_COMPRESSED_TIME, \
    _COMPRESSED_CHUNK_SIZE, _UNCOMPRESSED_CHUNK_SIZE, _CHUNK_COMPRESSED_TIME, _COMPRESSED_FILE_SIZE, _FIRST_COMPRESSION, \
    _SECOND_COMPRESSION, _FILE_CHUNK_SUMMARY


def generatev2(compression_report):
    headers = [
        "Compression Stage",
        "Compression Name",
        "File Size (MB)",
        "Compressed File Size (MB)",
        "Compression Time (ms)",
        "Compression Ratio",
        "Space Saving %",
        "Compression Speed"
    ]

    string_report_content = "\n\n**************** Start Report ****************"
    for file in compression_report:

        table_row = []
        string_report_content += f"\n\n**************** File Name: {file[_FILE]} | Actual File Size {file[_UNCOMPRESSED_FILE_SIZE] / (1024 * 1024)} MB ****************"

        first_compression_uncompressed_size = file[_FILE_SUMMARY][_FIRST_COMPRESSION][_UNCOMPRESSED_FILE_SIZE]
        first_compression_compressed_size = file[_FILE_SUMMARY][_FIRST_COMPRESSION][_COMPRESSED_FILE_SIZE]
        first_compression_compression_time = file[_FILE_SUMMARY][_FIRST_COMPRESSION][_FILE_COMPRESSED_TIME]
        if len(file[_FILE_SUMMARY]) > 1:
            table_row.append([
                "Step 01",
                file[_FILE_SUMMARY][_FIRST_COMPRESSION][_COMPRESSION_NAME],
                first_compression_uncompressed_size / (1024 * 1024),
                first_compression_compressed_size / (1024 * 1024),
                first_compression_compression_time,
                first_compression_uncompressed_size / first_compression_compressed_size,
                (1 - (first_compression_compressed_size / first_compression_uncompressed_size)) * 100,
                (first_compression_uncompressed_size - first_compression_compressed_size) /
                first_compression_compression_time
            ])

            second_compression_uncompressed_file = file[_FILE_SUMMARY][_SECOND_COMPRESSION][_UNCOMPRESSED_FILE_SIZE]
            second_compression_compressed_size = file[_FILE_SUMMARY][_SECOND_COMPRESSION][_COMPRESSED_FILE_SIZE]
            second_compression_compression_time = file[_FILE_SUMMARY][_SECOND_COMPRESSION][_FILE_COMPRESSED_TIME]
            table_row.append([
                "Step 02",
                file[_FILE_SUMMARY][_SECOND_COMPRESSION][_COMPRESSION_NAME],
                second_compression_uncompressed_file / (1024 * 1024),
                second_compression_compressed_size / (1024 * 1024),
                second_compression_compression_time,
                second_compression_uncompressed_file / second_compression_compressed_size,
                (1 - (second_compression_compressed_size / second_compression_uncompressed_file)) * 100,
                (second_compression_uncompressed_file - second_compression_compressed_size) /
                second_compression_compression_time
            ])

            table_row.append([
                "Total Compression",
                file[_FILE_SUMMARY][_SECOND_COMPRESSION][_COMPRESSION_NAME],
                first_compression_uncompressed_size / (1024 * 1024),
                second_compression_compressed_size / (1024 * 1024),
                second_compression_compression_time + first_compression_compression_time,
                first_compression_uncompressed_size / second_compression_compressed_size,
                (1 - (second_compression_compressed_size / first_compression_uncompressed_size)) * 100,
                (first_compression_uncompressed_size - second_compression_compressed_size) /
                (second_compression_compression_time + first_compression_compression_time)
            ])

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
                first_compression_compression_time
            ])

        string_report_content += tabulate(table_row, headers=headers, tablefmt="grid")

    string_report_content += "\n\n**************** End Report ****************"
    return string_report_content
