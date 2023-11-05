import json

from core import AddressBook, Record
from save_service.save_service import SaveAddressBookInLocalFile

contacts = AddressBook(
    data_save_service=SaveAddressBookInLocalFile(address="address_book.json")
)


mandatory_data = {
    "name": ["add", "change", "phone"],
    "phone": ["add", "change"],
}


def input_error(func) -> callable:
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except KeyError:
            return f"Entered name '{args[0]}' was not found. " \
                   f"Type help() for details."
        except (IndexError, TypeError):
            return f"Missing command part, entered data: '{args, kwargs}', type " \
                   f"'help' to see supported commands or exit to stop the bot."
        except ValueError:
            return "Phone number can only consist of 10 digits."
        else:
            return result
    return wrapper


def hello_command() -> str:
    return "How can I help you?"


@input_error
def add_command(name: str, phone: str, birthday: str = "") -> str | None:
    if contacts.find(name):
        print(
            f"Contact with this name already exists. Enter another name. \n"
            f"Entered name: "
        )
        return name
    record = Record(username=name)
    record.add_phone(phone=phone)
    if birthday:
        record.add_birthday(birthday)
    contacts.add_record(record_data=record)
    return f"Contact was added.\n" \
           f"| {name:<20} | {phone:<20} | " \
           f"{birthday:<20}"


@input_error
def change_command(name: str, old_phone: int, new_phone: int) -> str:
    rec = contacts.find(name)
    found_phone = [p for p in contacts[name]["phones"] if p == old_phone]
    if rec and found_phone:
        rec.edit_phone(old_phone=old_phone, new_phone=new_phone)
        contacts.update_record(rec)
        return f"Phone number for contact '{rec.name.value}' has been " \
               f"changed from '{old_phone}' to '{new_phone}'"
    elif not rec:
        return f"The contact with the name '{name}' was not found."
    return f"Entered phone which should be changed is not found."


@input_error
def phone_command(name: str) -> str:
    rec = contacts.find(name)
    if rec:
        phone_nums = [phone_num.value for phone_num in rec.phones]
        return f"{rec.name.value}\'s phone number(s): " + ", ".join(phone_nums)
    return f"The contact with the name '{name}' was not found."


def get_formatted_headers() -> str:
    """
    Method generate formatted headers string.
    :return: Formatted headers string.
    """
    s = "{:^50}".format("***Clients phone numbers***")
    s += "\n{:<10} | {:<20} | {:<70} |\n".format(
        "Number", "User name", "Phone number"
    )
    return s


@input_error
def search_contact(data: str):
    if len(data) < 2:
        return "Searched phrase must have at least 2 symbols"
    records = contacts.search_contact(search_phrase=data)
    divider = f"{'':-^67}\n"
    existing_contacts = f"{'Number':^20} | {'Name':^20} | {'Phone':^20} |\n" \
                        f"{'':-^67}\n"
    for num, record in enumerate(records, start=1):
        phones_str = ",".join(
            [phone_num for phone_num in record["info"]["phones"]]
        )
        existing_contacts += '{:^20} | {:^20} | {:^20} |\n'.format(
            num, record["name"], phones_str
        ) + divider
    return existing_contacts


def show_all_command() -> str:
    existing_contacts = f"| {'Name':^20} | {'Phone':^20} |\n" \
                        f"{'':-^47}\n"
    for name, info in zip(contacts.keys(), list(contacts.iterator())):
        existing_contacts += \
            f"| {name:<20} | " \
            f"{', '.join([p for p in info[0]['phones']]):<20} |\n"
    return existing_contacts


@input_error
def delete_contact(name: str) -> str:
    return contacts.delete(username=name)


def exit_command() -> str:
    return "Exit..."


@input_error
def show_days_to_birthday(name: str) -> str:
    """
    Method returns the number of days to the next client's birthday. The method
    returns the number of days without fractional part.
    :return: String with a number of days.
    """
    record = contacts.find(name)
    if record:
        days_to_birthday = record.days_to_birthday()
        return f"Days to the next birthday for '{name}': {days_to_birthday}."
    return f"Contact with a name '{name}' doesn't exist in the Address Book"


def help_command() -> str:
    return """List of supported commands:\n
           1 - 'hello' to greeting the bot;\n
           2 - 'add' to add a contact, e.g. 'add John 380995057766';\n
           or 'add John 380995057766 30-05-1967';\n
           3 - 'change' to change an existing contact's phone,\n
           e.g. 'change John 380995051919 1234567890';\n
           4 - 'phone' to see a contact, e.g. 'phone John';\n
           5 - 'show all' to show all contacts which were add during the 
           session with the bot:\n
           6 - 'good bye', 'close' or 'exit' to stop the bot;\n
           7 - 'search na' or 'search 123' to search in the address book 
           by any match in name or phone;\n
           8 - 'delete john' to remove a whole contact by name.\n
           9 - 'help' to see description and supported commands.\n\n
           Each command, name or phone should be separated by a 
           space like ' '.
           Each command should be entered in order like 'command name 
           phone'.\n
           Each contact's name has to be unique.\n
           Each contact's name should be entered like a single word, if\n
           desired name is first name and last name, separate them with\n
           underscore, e.g. John_Wick.\n
           You can add only one phone to the name.\n
           Purpose of the bot to create, modify and save contacts during\n
           a single session. All data will be deleted after exit from the\n
           session."""


def unknown_command(command: str) -> str:
    return f"Unsupported command: '{command}'. " \
           f"Type 'help' to see supported commands."


@input_error
def parse_command(input_data: str) -> dict:
    command_parts = input_data.split()
    if input_data.lower().startswith("show days to birthday"):
        return {
            "command": " ".join(command_parts[0:4]).lower(),
            "name": command_parts[4]
        }
    return {
        "command": " ".join(command_parts[0:2]).lower() if any(
            map(input_data.lower().startswith, {"show all", "good bye"})
        ) else command_parts[0].lower(),
        "data": command_parts[1] if command_parts[0].lower() in {
            "search"} else None,
        "name": command_parts[1] if command_parts[0].lower() in {
            "add", "change", "phone", "delete"} else None,
        "phone": str(command_parts[2]) if command_parts[0].lower() in {
            "add", "change"} else None,
        "new_phone": str(command_parts[3]) if command_parts[0].lower() in {
            "change"} else None,
        "days_to_birthday": command_parts[-1] if len(command_parts) > 3 else "",
    }


@input_error
def start_bot() -> callable:
    while True:
        command = input(
            "\n"
            "Enter a command. \n"
            "Type 'help' to see list of supported commands. \n"
            "Type 'exit' to stop the bot. \n\n"
        )

        parsed_data = parse_command(command)

        if not parsed_data:
            continue

        if isinstance(parsed_data, str):
            print(parsed_data)
            continue

        match parsed_data["command"]:
            case "hello":
                result = hello_command()
            case "add":
                result = add_command(
                    parsed_data["name"], parsed_data["phone"],
                    parsed_data["days_to_birthday"]
                )
            case "change":
                result = change_command(
                    name=parsed_data["name"], old_phone=parsed_data["phone"],
                    new_phone=parsed_data["new_phone"]
                )
            case "phone":
                result = phone_command(parsed_data["name"])
            case "search":
                result = search_contact(parsed_data["data"])
            case "show all":
                result = show_all_command()
            case "delete":
                result = delete_contact(parsed_data["name"])
            case "help":
                result = help_command()
            case "show days to birthday":
                result = show_days_to_birthday(parsed_data["name"])
            case command if command in {"good bye", "close", "exit"}:
                result = exit_command()
            case _:
                result = unknown_command(command)

        print(result)

        if result == "Exit...":
            break


if __name__ == '__main__':
    start_bot()
