class Singleton(object):
    __instance = None

    def __new__(cls):
        """
        Создает новый объект класса если такового не существует, или же просто возвращает существующий
        """
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

