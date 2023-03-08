from io import StringIO

import yaml


class ConfigParser:
    def __init__(self, raw: str):
        self.raw = raw
        self.parsed = yaml.load(StringIO(raw), yaml.FullLoader)
        if not isinstance(self.parsed['routes'], list):
            raise Exception('routes should be list')
        if self.parsed['routes'] == []:
            raise Exception('routes should not be empty')
