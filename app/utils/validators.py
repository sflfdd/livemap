import re
from email_validator import validate_email as validate_email_format, EmailNotValidError

def validate_email(email):
    """Validate email format."""
    try:
        validate_email_format(email)
        return True
    except EmailNotValidError:
        return False

def validate_password(password):
    """
    Validate password strength.
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True

def sanitize_html(html_content):
    """Sanitize HTML content."""
    import bleach
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
    allowed_attrs = {'a': ['href', 'title']}
    return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attrs)
