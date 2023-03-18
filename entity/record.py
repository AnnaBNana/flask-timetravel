class Record:
    def __init__(self, id: int, data: dict[str, str]) -> None:
        self.id = id
        self.data = data

    def update_data(self, changes: dict[str, str]) -> None:
        for key, value in changes.items():
            if value:
                self.data[key] = value
            else:
                self.data.pop(key, None)
