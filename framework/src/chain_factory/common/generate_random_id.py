from uuid import uuid1, uuid4


def generate_random_id() -> str:
    """
    Generate a unique id to be used as a unique workflow id
    """
    return str(uuid1()) + "-" + str(uuid4())
