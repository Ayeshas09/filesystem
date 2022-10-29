from datetime import datetime


def string_to_bytes(string):
    return list([ord(char) for char in string])


def bytes_to_string(bytes):
    return ''.join([chr(byte) for byte in bytes])


def get_datetime_object(date_string: str):
    return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
