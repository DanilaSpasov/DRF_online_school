import re

from rest_framework.exceptions import ValidationError


def validate_youtube_url(value):
    pattern = r"https?://(?:www\.)?youtube\.com(?:[/?#].*)?"

    if not re.fullmatch(pattern, value):
        raise ValidationError("Прикреплять можно только ссылку на YouTube.com")
