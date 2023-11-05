import json
from collections import UserDict
from datetime import datetime
from typing import Generator


DATE_FORMAT = "%d-%m-%Y"


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):

    def __init__(self, client_name: str):
        self.name = client_name
        super().__init__(value=self.name)

    @property
    def value(self):
        return self.name

    @value.setter
    def value(self, client_name: str) -> None:
        self.name = client_name


class Phone(Field):
    def __init__(self, phone: str):
        self.phone = phone
        super().__init__(value=self.phone)

    @property
    def value(self):
        return self.phone

    @value.setter
    def value(self, phone: str):
        if not len(phone) == 10 or not phone.isdigit():
            raise ValueError
        self.phone = phone


class Birthday(Field):
    def __init__(self, birthday: str = ""):
        self.bd = birthday
        super().__init__(value=self.bd)

    @property
    def value(self) -> datetime.date:
        return self.bd

    @value.setter
    def value(self, birthday: str = "") -> None:
        if not birthday:
            return
        try:
            birthday_date: datetime.date = \
                datetime.strptime(birthday, DATE_FORMAT).date()
            self.bd = birthday_date
        except ValueError:
            raise (
                f"Birthday '{birthday}' or date's format is not incorrect. "
                f"Expected date format: '{DATE_FORMAT}'."
            )


class Record:
    def __init__(self, username: str, birthday: str = ""):
        self.name = Name(username)
        self.phones = []
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, " \
               f"phones: {'; '.join(p.value for p in self.phones)}"

    def serialize_data(self):
        birthday = self.birthday.value
        birthday_str = birthday.strftime(DATE_FORMAT) if birthday else None
        return json.dumps(
            {
                self.name.value:
                    {
                        "phones": [phone_num.value for phone_num in self.phones],
                        "birthday": birthday_str
                    }
            }
        )

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)
        return f"'{birthday}' was set as a birthday date to a contact with " \
               f"name '{self.name.value}'"

    def days_to_birthday(self):
        if not self.birthday.value:
            raise ValueError("Absent necessary data about birthday.")
        today = datetime.today()
        next_birthday = datetime(
            today.year, self.birthday.value.month, self.birthday.value.day
        )
        if today > next_birthday:
            next_birthday = datetime(
                today.year + 1, self.birthday.value.month,
                self.birthday.value.day
            )
        days_to_next_birthday = (next_birthday - today).days
        return str(days_to_next_birthday)

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))
        return f"Added phone: {phone}."

    def remove_phone(self, phone: str):
        if num := [number for number in self.phones if number.value == phone]:
            self.phones.remove(num[0])
            return f"Deleted phone: {phone}."
        return f"Phone was not found: '{phone}', " \
               f"enter existing phone to delete."

    def edit_phone(self, old_phone: str, new_phone: str):
        if old := [number for number in self.phones if number.value == old_phone]:
            ind = self.phones.index(old[0])
            self.phones[ind] = Phone(new_phone)
            return f"Edited phone: {old_phone} to {new_phone}."
        return f"Phone was not found: '{old_phone}', " \
               f"enter existing phone to edit."

    def find_phone(self, phone: str):
        if [numb for numb in self.phones if numb.value == phone]:
            print(f"The phone was found: {phone}.")
            return Phone(phone)
        return f"The phone wasn't found: {phone}."


class AddressBook(UserDict):

    def __init__(self, data_save_service):
        super().__init__()
        self.data_save = data_save_service
        self.data.update(
            self.data_save.read_data(path=self.data_save.address)
        )

    def iterator(self, number_of_records: int = 1) -> Generator:
        address_book = self.data_save.read_data(path=self.data_save.address)
        contacts = list(address_book.values())
        step = number_of_records or 1
        return (contacts[i:i + step] for i in range(0, len(contacts), step))

    def add_record(self, record_data):
        address_book = self.data_save.read_data(
            path=self.data_save.address)
        if record_data.name.value not in address_book:
            self.data[record_data.name.value] = record_data
            record_data = Record.serialize_data(record_data)
            address_book.update(json.loads(record_data))
            self.data_save.save_data(
                path=self.data_save.address, data=address_book
            )
        else:
            return f"Record with the name '{record_data.name.value}' already " \
                   f"exists in the address book dictionary"

    def update_record(self, record_data):
        address_book = self.data_save.read_data(
            path=self.data_save.address)
        found_record = address_book.get(record_data.name.value)
        if found_record:
            address_book[record_data.name.value] = json.loads(
                Record.serialize_data(record_data))[record_data.name.value]
            self.data_save.save_data(path=self.data_save.address,
                                     data=address_book)
        else:
            return f"The contact with a name '{record_data.name.value}' has " \
                   f"not been found in existing Address Book."

    def find(self, username: str):
        rec = self.data_save.read_data(
            path=self.data_save.address).get(username)
        if rec:
            record_obj = Record(username=username, birthday=rec.get("birthday"))
            for phone in rec["phones"]:
                record_obj.add_phone(phone=phone)
            return record_obj
        else:
            return None

    def search_contact(self, search_phrase: str):
        address_book = self.data_save.read_data(
            path=self.data_save.address)
        for _name, info in address_book.items():
            found_phones = list(
                filter(
                    lambda phone: search_phrase in phone, info["phones"]
                )
            )
            if any([search_phrase.lower() in _name.lower(), found_phones]):
                yield {"name": _name, "info": info}

    def delete(self, username):
        address_book = self.data_save.read_data(
            path=self.data_save.address)
        rec = address_book.get(username)
        if rec:
            self.data.pop(username)
            address_book.pop(username)
            self.data_save.save_data(
                path=self.data_save.address, data=address_book
            )
            return f"The contact with name '{username}' has been deleted."
        return f"Contact with the name '{username}' was not deleted, " \
               f"not found."


if __name__ == "__main__":
    # Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")

    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    # Виведення всіх записів у книзі
    for name, record in book.data.items():
        print(record)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону у записі John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

    # Видалення запису Jane
    book.delete("Jane")
