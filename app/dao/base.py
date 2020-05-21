from motor.core import AgnosticCollection


class BaseDao:
    collection: AgnosticCollection

    def __init__(self, collection: AgnosticCollection):
        self.collection = collection
