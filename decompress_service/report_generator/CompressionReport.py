from tabulate import tabulate

from Util import _FILE_DECOMPRESSED_TIME, \
    _DECOMPRESSED_FILE_SIZE, _FIRST_DECOMPRESSION, \
    _SECOND_DECOMPRESSION


def generatev2(compression_report, file_name):
    headers = [
        "Compression Stage",
        "De Compressed File Size (MB)",
        "DeCompression Time (ms)"
    ]

    string_report_content = '''
    <header> 
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous"> 
    </header
    '''

    table_row = []
    string_report_content += f'''
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <p class="lead"> File Name: {file_name}</p>
            </div>
        </div>
    </div>
    '''
    table_row.append([
        "Total Compression",
        compression_report[_SECOND_DECOMPRESSION][_DECOMPRESSED_FILE_SIZE] / (1024 * 1024),
        compression_report[_FIRST_DECOMPRESSION][_FILE_DECOMPRESSED_TIME] + compression_report[_SECOND_DECOMPRESSION][
            _FILE_DECOMPRESSED_TIME],
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
