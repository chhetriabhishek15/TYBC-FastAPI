from enum import Enum

class RoleEnum(str, Enum):
    ADMIN = "admin"
    CHEF = "chef"
    CUSTOMER = "customer"

class TokenAudience(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
