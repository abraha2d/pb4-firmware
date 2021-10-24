def file_view(path, query_dict, headers):
    try:
        with open(f"{__file__.rsplit('/', 2)[0]}/www{path}", 'rb') as f:
            data = f.read()
    except OSError:
        return 404, {}, f"{path} not found!"
    return 200, {}, data
