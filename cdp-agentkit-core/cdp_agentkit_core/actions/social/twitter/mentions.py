from multiprocessing import Manager


class Mentions():
    collection: any
    manager: any

    def list() -> any:
        if self.manager is None:
            self.manager = Manager()

        if self.collection is None:
            self.collection = self.manager.list()

        return self.collection
