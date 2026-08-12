from rest_framework.renderers import JSONRenderer


class UTF8JSONRenderer(JSONRenderer):
    """Força charset=utf-8: o JSONRenderer do DRF omite e o front quebra acentos pt-BR."""

    charset = "utf-8"
