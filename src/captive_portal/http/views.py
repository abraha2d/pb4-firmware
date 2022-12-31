from errno import ENOENT


# noinspection PyUnusedLocal
async def file_view(path, query_dict, headers):
    try:
        with open(f"{__file__.rsplit('/', 2)[0]}/www{path}", "rb") as f:
            data = f.read()
    except OSError as e:
        if e.errno == ENOENT:
            return 404, {}, f"{path} not found!"
        raise
    return 200, {}, data
