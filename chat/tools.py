from .models import Item


def check_stock(name):
    """Look up how many of an item we have."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    return {"name": item.name, "quantity": item.quantity, "price": item.price}


def list_items():
    """Return every item in the inventory."""
    items = Item.objects.all()
    return {"items": [{"name": i.name, "quantity": i.quantity, "price": i.price} for i in items]}

# adding an item takes its price as argument 
def add_item(name, quantity, price=None):
    """Create a new item, or add to an existing one's stock."""
    item = Item.objects.filter(name__iexact=name).first()
    # if the item already exists, the price is updated if a new price is provided, and if the item does not exist, it is created with the given price or 0 if price not provided
    if item is not None:
        item.quantity += quantity
        if price is not None:
            item.price = price
        item.save()
        return {"name": item.name, "quantity": item.quantity, "price": item.price, "created": False}
    item = Item.objects.create(name=name, quantity=quantity, price=price or 0)
    return {"name": item.name, "quantity": item.quantity, "price": item.price, "created": True}


def remove_stock(name, quantity):
    """Take a quantity out of stock."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    if quantity > item.quantity:
        return {
            "error": f"Cannot remove {quantity}. Only {item.quantity} in stock.",
            "name": item.name,
            "quantity": item.quantity,
        }
    item.quantity -= quantity
    item.save()
    return {"name": item.name, "quantity": item.quantity}


def delete_item(name):
    """Remove an item from the inventory entirely."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    item.delete()
    return {"deleted": name}


# added this: function takes the name of an item and a price, and sets the price of that item to the given value. 
# if the item does not exist, it returns an error message
def set_price(name, price):
    """Set the price of one unit of an existing item."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"'{name}' does not exist in the inventory."}
    item.price = price
    item.save()
    return {"name": item.name, "price": item.price}

# added this: function takes the name of an item, a quantity, and an optional VAT percentage, and returns the total cost of that quantity of the item including VAT when specified. 
# if the item does not exist or has no price set, it returns an error message
def calculate_cost(name, quantity, vat_percent=0):
    """Total cost of "quantity" of an item, including VAT if specified."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"'{name}' does not exist in the inventory."}
    if item.price == 0:
        return {
            "error": f"{item.name} has no price set yet."}
    subtotal = item.price * quantity
    vat_amount = subtotal * (vat_percent / 100)
    total = subtotal + vat_amount
    # round the float numbers and take 2 digits after the decimal point to avoid floating point precision issues and to make the output more user-friendly
    return {
        "name": item.name,
        "quantity": quantity,
        "unit_price": item.price,
        "subtotal": round(subtotal, 2),
        "vat_percent": vat_percent,
        "vat_amount": round(vat_amount, 2),
        "total": round(total, 2),
    }
# the calculate_cost function uses math and not done by AI agent


TOOL_DECLARATIONS = [
    {
        "type": "function",
        "name": "check_stock",
        "description": "Look up the current quantity of a single item in the inventory. Use this whenever the user asks whether something is in stock or how many there are.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
            },
            "required": ["name"],
        },
    },
    {
        "type": "function",
        "name": "list_items",
        "description": "Return every item in the inventory with its quantity. Use this when the user asks what is in stock generally, or asks for a list, rather than about one specific item.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "name": "add_item",
        "description": "Add stock to the inventory. If the item does not exist it is created; if it already exists the quantity is added to the existing total. Use this for restocking and for new deliveries.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "How many units to add. Must be positive.",
                },
                "price": {
                    "type": "number",
                    "description": "Optional. The price of one unit of the item. If not provided, the price will be set to 0.",
                },
            },
            "required": ["name", "quantity"],
        },
    },
    {
        "type": "function",
        "name": "remove_stock",
        "description": "Reduce the quantity of an existing item. Use this when items are sold, shipped or used. This does NOT delete the item; it only lowers the number.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "How many units to remove. Must be positive.",
                },
            },
            "required": ["name", "quantity"],
        },
    },
    {
        "type": "function",
        "name": "delete_item",
        "description": "Permanently remove an item and its record from the inventory entirely. This is destructive. Only use it when the user clearly wants the item gone, not when they want to reduce its quantity.",
        "parameters": {
            "type": "object",
            "properties": {

                "name": {
                    "type": "string",
                    "description": "The name of the item to delete.",
                },
            },
            "required": ["name"],
        },
    },
    {
        "type": "function",
        "name": "set_price",
        "description": "Set or change the price of one unit of an existing item. Use this when the user wants to change the price of an item.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
                "price": {
                    "type": "number",
                    "description": "The price of one unit of the item, e.g. 12.99.",
                },
            },
            "required": ["name", "price"],
        },
    },
    {
        "type": "function",
        "name": "calculate_cost",
        "description": "Calculate the total cost of a given quantity of an item, including VAT if specified. Always use this for any question about cost, total price or VAT.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "How many units to calculate the cost for. Must be positive.",
                },
                "vat_percent": {
                    "type": "number",
                    "description": "Optional, VAT as a percentage. '10% VAT' means 10. Use 0 if no VAT is specified",
                },
            },
            "required": ["name", "quantity"],
        },
    },
]

TOOL_FUNCTIONS = {
    "check_stock": check_stock,
    "list_items": list_items,
    "add_item": add_item,
    "remove_stock": remove_stock,
    "delete_item": delete_item,
    "set_price": set_price,
    "calculate_cost": calculate_cost,
}
