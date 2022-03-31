from django.http import HttpResponse


def get_ip(httpRequest):
    # try to get ip from proxy, if None then get directly
    try:
        ip = httpRequest.META['HTTP_X_FORWARDED_FOR']
        ip = ip.split(",")[0]
    except:
        ip = httpRequest.META['REMOTE_ADDR']
        ip = ip.split(",")[0]

    return ip
