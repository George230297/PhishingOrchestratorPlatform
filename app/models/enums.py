import enum

class AttackVectorEnum(str, enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    QR = "QR"
    WHATSAPP = "WHATSAPP"

class EventTypeEnum(str, enum.Enum):
    SENT = "SENT"
    OPENED = "OPENED"
    CLICKED = "CLICKED"
    DOWNLOAD_ATTACHMENT = "DOWNLOAD_ATTACHMENT"
    SUBMITTED_DATA = "SUBMITTED_DATA"
    REPORTED = "REPORTED"

class HealthStatusEnum(str, enum.Enum):
    HEALTHY = "HEALTHY"
    BURNED = "BURNED"
    WARMUP = "WARMUP"
