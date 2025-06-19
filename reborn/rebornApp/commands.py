from abc import ABC, abstractmethod
from .models import Item, Seller

class Command(ABC):
    """
    Abstract Base Class for a command.
    """
    @abstractmethod
    def execute(self):
        pass

class CreateProductCommand(Command):
    """
    Command to create a new product listing.
    """
    def __init__(self, seller: Seller, product_data: dict):
        self.seller = seller
        self.product_data = product_data

    def execute(self):
        """Creates and returns a new Item."""
        item = Item.objects.create(seller=self.seller, **self.product_data)
        return item

class EditProductCommand(Command):
    """
    Command to edit an existing product listing.
    """
    def __init__(self, item: Item, product_data: dict):
        self.item = item
        self.product_data = product_data

    def execute(self):
        """Updates the item with new data and returns it."""
        for key, value in self.product_data.items():
            setattr(self.item, key, value)
        self.item.save()
        return self.item

class DeleteProductCommand(Command):
    """
    Command to delete a product listing.
    """
    def __init__(self, item: Item):
        self.item = item

    def execute(self):
        """Deletes the item if it can be safely deleted."""
        if not self.item.can_be_deleted():
            raise ValueError(f"Cannot delete item '{self.item.title}' because it's part of existing orders.")
        self.item.delete()

class ProductCommandInvoker:
    """
    The Invoker is responsible for executing a command.
    It's a simple invoker that just runs the command immediately.
    """
    def __init__(self, command: Command):
        self._command = command

    def execute_command(self):
        return self._command.execute()
