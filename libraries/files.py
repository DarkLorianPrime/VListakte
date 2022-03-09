import os


def check_file(name, folder):
    return list(filter(lambda file: file.endswith(name), os.listdir(folder)))