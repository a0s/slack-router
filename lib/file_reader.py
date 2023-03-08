class FileReader:
    def read(self, name: str) -> str:
        with open(name, 'r') as reader:
            return reader.read()
