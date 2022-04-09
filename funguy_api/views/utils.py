def get_ip(Request):
    # try to get ip from proxy, if None then get directly
    try:
        ip = Request.META['HTTP_X_FORWARDED_FOR']
        ip = ip.split(",")[0]
    except:
        ip = Request.META['REMOTE_ADDR']
        ip = ip.split(",")[0]

    return ip
