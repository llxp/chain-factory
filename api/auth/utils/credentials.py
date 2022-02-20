async def get_domain(username: str):
    if '@' in username:
        domain = username.split('@')
        if len(domain) == 2:
            return domain[1]
    return None
