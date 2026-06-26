import re

VALID_PASSWORD = "Strong-password-12345!"
OTP_PATTERN = re.compile(r"\b(\d{6})\b")
