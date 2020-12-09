from databases import Database


class AsyncPSQLConnector(object):
    def __init__(self, url):
        self.db = Database(url, force_rollback=True)

    def __new__(cls, url):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AsyncPSQLConnector, cls).__new__(cls)
        return cls.instance
