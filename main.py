import functools


def notify(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        name = func.__name__
        print(f"Executing function: {name}")

        this, value = args
        old_value = getattr(this, name)
        if old_value != value:
            print(f"Value changed from {old_value} to {value}")
        return func(*args, **kwargs)
    return wrapper


class MyClass:

    _data: int = 0

    @property
    def data(self):
        return self._data

    @data.setter
    @notify
    def data(self, value):
        self._data = value


def main():
    m = MyClass()
    m.data = 10
    print(m.data)


if __name__ == "__main__":
    main()
