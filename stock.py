from security import Security


class Stock(Security):
    def __init__(self, name):
        super().__init__(name)
