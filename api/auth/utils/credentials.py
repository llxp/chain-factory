async def get_domain(username: str) -> str:
    if '@' in username:
        domain = username.split('@')
        if len(domain) == 2:
            return domain[1]
    return ""


async def get_user(username: str) -> str:
    if '@' in username:
        username_splitted = username.split('@')
        if len(username_splitted) == 2:
            return username_splitted[0]
    return username
