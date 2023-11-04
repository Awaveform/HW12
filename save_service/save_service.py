import json
import pathlib


class SaveAddressBookInLocalFile:

    def __init__(self, address: str):
        super().__init__(address)
        self.store_obj = pathlib.Path(address)
        if not self.store_obj.exists():
            with open(address, "w"):
                print(f"File '{address}' has been created.")

    @staticmethod
    def read_info(path: str) -> dict:
        with open(path, "r") as fh:
            try:
                file_data = json.load(fh)
            except ValueError:
                return {}
            return file_data

    @staticmethod
    def save_info(path: str, data: dict) -> None:
        with open(path, mode="w") as fh:
            json.dump(data, fh)
