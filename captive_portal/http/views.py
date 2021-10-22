def template(uri, qps, headers):
    try:
        with open(f"captive_portal/www{uri}", 'rb') as f:
            data = f.read()
    except OSError:
        return 404, f"{uri} not found!"
    try:
        data = data % qps
    except (TypeError, ValueError):
        pass
    return 200, {}, data
