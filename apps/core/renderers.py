from rest_framework.renderers import JSONRenderer


class UTF8JSONRenderer(JSONRenderer):
    """DRF omite charset no JSON; o front precisa de UTF-8 explícito para pt-BR."""

    charset = "utf-8"
