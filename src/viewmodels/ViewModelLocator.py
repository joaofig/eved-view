class ViewModelLocator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ViewModelLocator, cls).__new__(cls)
        return cls._instance
