import re
import bleach
from app.utils.logger import logger

def sanitize_input(text: str) -> str:
    """Sanitize input against XSS by removing unsafe HTML tags."""
    if not text:
        return text
    return bleach.clean(text, strip=True)

def detect_prompt_injection(text: str) -> bool:
    """Detect common prompt injection attacks."""
    if not text:
        return False
        
    patterns = [
        r"ignore previous instructions",
        r"disregard previous",
        r"system prompt",
        r"forget everything",
        r"you are now",
        r"bypass rules",
        r"developer mode"
    ]
    
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower):
            logger.warning("Security Audit: Potential prompt injection detected", extra={"pattern": pattern})
            return True
    return False

def audit_log(action: str, user_email: str, details: str = ""):
    """Enterprise audit trail logging."""
    logger.info("AUDIT TRAIL", extra={
        "action": action,
        "user_email": user_email,
        "details": details,
        "audit": True
    })
