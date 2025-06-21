def authenticate_hook(user, token):
    """Only allow users with middlebury.edu email addresses and make them staff"""
    if user and user.email and user.email.endswith('@middlebury.edu'):
        user.is_staff = True  # ✅ Give staff privileges
        user.save()  # ✅ Save it
        return user
    return None