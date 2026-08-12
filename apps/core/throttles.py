"""Throttles de abuso em endpoints públicos sensíveis."""

from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = "login"


class RegistroRateThrottle(AnonRateThrottle):
    scope = "registro"
