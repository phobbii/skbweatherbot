import re, os, urllib.request


class Checks(object):
    def __init__(self) -> None:
        pass

    def get_public_ip(self, ip_services):
        for service in ip_services:
            try:
                webhook_host = re.sub('^\s+|\n|\r|\s+$', '',
                                    urllib.request.urlopen(service).read().decode('utf8'))
                return webhook_host
            except Exception as error:
                print(f'Checks get public ip unsuccessful, unexpected error occurred: {error}')
                return False

    def get_ssl_data(self, dir='.', file_types = ['pem', 'key']):
        ssl = {}
        for file in os.listdir(dir):
            for type in file_types:
                if file.endswith(type):
                    ssl[type] = os.path.abspath(file)
        if ssl:
            if len([k for k in ssl.keys()]) == 2:
                return ssl
            else:
                print(f'Checks get ssl data unsuccessful, '
                      f'{[type for type in file_types if type not in ssl.keys()][0]} not found')
                return False
        else:
            print(f'Checks get ssl data unsuccessful, no ssl data found')
            return False