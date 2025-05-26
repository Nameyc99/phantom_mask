# your_app/utils.py

from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError

def parse_date_param(date_str: str, param_name: str):
    try:
        return timezone.make_aware(datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)) # timedelta for inclusive
    except (TypeError, ValueError):
        raise ValidationError(f"{param_name} must be provided in YYYY-MM-DD format.")
