def get_ip(request):
    # try to get ip from proxy, if None then get directly
    try:
        ip = request.META['HTTP_X_FORWARDED_FOR']
        ip = ip.split(",")[0]
    except:
        ip = request.META['REMOTE_ADDR']
        ip = ip.split(",")[0]

    return ip
