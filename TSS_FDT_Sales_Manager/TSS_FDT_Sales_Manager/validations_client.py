import re


def validate_name(name):
    return len(name.strip()) >= 2


def validate_cif(cif):
    return bool(re.match(r"^[A-Za-z0-9]{8,10}$", cif))


def validate_email(email):
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))


def validate_contact(contact):
    return len(contact.strip()) >= 2
