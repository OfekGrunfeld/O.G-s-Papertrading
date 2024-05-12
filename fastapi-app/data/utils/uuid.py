import uuid

def generate_uuid() -> str:
    """
    Returns:
        str: A uuid4 formatted as a string.
    """
    return str(uuid.uuid4())
