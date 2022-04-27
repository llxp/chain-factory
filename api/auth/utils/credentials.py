async def get_domain(username: str):
    if '@' in username:
        domain = username.split('@')
        if len(domain) == 2:
            return domain[1]
    return None


async def get_user(username: str):
    if '@' in username:
        username = username.split('@')
        if len(username) == 2:
            return username[0]
    return username
