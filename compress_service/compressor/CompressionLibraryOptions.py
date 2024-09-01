class CompressionLibraryOptions:

    def __init__(self, **kwargs):
        # Set any additional attributes provided in kwargs
        self.attributes = kwargs
        # Define the keys you want to keep
        keys_to_keep = {'name', 'order'}

        # Filter the dictionary to include only these keys
        self.attributes = {k: v for k, v in self.attributes.items() if k not in keys_to_keep}

        for key, value in kwargs.items():
            setattr(self, key, value)

    def set_attr(self, name, value):
        """Method to dynamically add or update an attribute."""
        setattr(self, name, value)

    def get_attr(self, name):
        """Method to retrieve the value of a dynamic attribute."""
        return getattr(self, name, None)

    def remove_attr(self, name):
        """Method to remove a dynamic attribute."""
        if hasattr(self, name):
            delattr(self, name)
        else:
            raise AttributeError(f"Attribute '{name}' not found.")

    def has_attributes(self):
        """Method to check if there are any attributes left."""
        return bool(self.__dict__)

    def get_dict(self):
        if self.attributes == {}:
            return None
        else:
            return self.attributes

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"
