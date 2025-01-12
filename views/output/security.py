def has_permission(user: str, permission: str) -> bool:
    if permission.startswith("Truck"):
        return True
    return False
