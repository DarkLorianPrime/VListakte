import os


def startswith_check_file(name: str, folder: str = None) -> list:
    """
    :param name: текст, с которого должно начинаться название файла
    :param folder: папка, в которой нужно искать файл
    :return:
    """
    listdir = os.listdir(folder) if folder is not None else os.listdir()
    return list(filter(lambda file: file.startswith(name), listdir))


def endswith_check_file(name: str, folder: str) -> list:
    """
    :param name: текст, на котором должно заканчиваться название файла
    :param folder: папка, в которой нужно искать файл
    :return:
    """
    return list(filter(lambda file: file.endswith(name), os.listdir(folder)))
