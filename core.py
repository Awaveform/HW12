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
        if not len(phone) == 10 or not phone.isdigit():
            raise ValueError("Phone number can only consist of 10 digits.")
        self.phone = phone
        super().__init__(value=self.phone)

    @property
    def value(self):
        return self.phone

    @value.setter
    def value(self, phone: str):
        if not len(phone) == 10 or not phone.isdigit():
            raise ValueError("Phone number can only consist of 10 digits.")
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

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)
        return f"'{birthday}' was set as a birthday date to a contant with " \
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
        print(f"Added phone: {phone}.")

    def remove_phone(self, phone: str):
        if num := [number for number in self.phones if number.value == phone]:
            self.phones.remove(num[0])
            print(f"Deleted phone: {phone}.")
        else:
            print(
                f"Phone was not found: '{phone}', "
                f"enter existing phone to delete."
            )

    def edit_phone(self, old_phone: str, new_phone: str):
        if old := [number for number in self.phones if number.value == old_phone]:
            ind = self.phones.index(old[0])
            self.phones[ind] = Phone(new_phone)
            print(f"Edited phone: {old_phone} to {new_phone}.")
        else:
            raise ValueError(
                f"Phone was not found: '{old_phone}', "
                f"enter existing phone to edit."
            )

    def find_phone(self, phone: str):
        if [numb for numb in self.phones if numb.value == phone]:
            print(f"The phone was found: {phone}.")
            return Phone(phone)
        else:
            print(f"The phone wasn't found: {phone}.")

    def __str__(self):
        return f"Contact name: {self.name.value}, " \
               f"phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):

    def __init__(self):
        super().__init__()

    def iterator(self, number_of_records: int = 1) -> Generator:
        contacts = list(self.data.values())
        step = number_of_records or 1
        return (contacts[i:i + step] for i in range(0, len(contacts), step))

    def add_record(self, record_row: Record):
        self.data[record_row.name.value] = record_row
        print(f"New record was added: {record_row.name}.")

    def find(self, username: str):
        for rec in self.data.values():
            if rec.name.value == username:
                print(f"The record was found: {username}.")
                return rec
        print(f"The record was not found: {username}.")
        return None

    def delete(self, username):
        for rec in self.data.values():
            if rec.name.value == username:
                del self.data[username]
                print(f"The record was deleted: {username}.")
                break
        else:
            print(f"The record was not found: {username}.")


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
