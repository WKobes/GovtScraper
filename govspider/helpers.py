def strip_abs_url(raw_url):
    """
    For a given absolute URL, strip the URL and return the full domain (except for www.) and the relative path included.
    In case of an email address, only take the domain
    :param raw_url: The absolute URL to strip
    :return: both the stripped URL as the relative path it was addressing
    """
    final_url = raw_url
    if final_url.startswith('http'):
        final_url = final_url.split('//', maxsplit=1)[1]  # Remove HTTP(S)
    if final_url.startswith('www.'):
        final_url = final_url.replace('www.', '')
    # Some links contain an email address or user@server construction
    if '@' in final_url:
        final_url = final_url.split('@')[1]
    if '/' in final_url:
        final_url, rel_path = final_url.split('/', maxsplit=1)
        final_url = final_url.lower()
        return final_url, '/' + rel_path
    else:
        return final_url.lower(), None
