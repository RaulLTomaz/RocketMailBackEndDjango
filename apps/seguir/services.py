from __future__ import annotations

from django.db import IntegrityError, transaction

from apps.core.exceptions import APIError
from apps.seguir.models import Seguir
from apps.usuarios.models import Usuario
from apps.usuarios.services import queryset_publico


def seguir_usuario(*, seguidor_id: int, seguido_id: int) -> dict:
    if seguidor_id == seguido_id:
        raise APIError("Não é possível seguir a si mesmo.", status_code=400)

    if not Usuario.objects.filter(pk=seguido_id).exists():
        raise APIError("Usuário a seguir não encontrado.", status_code=404)

    try:
        with transaction.atomic():
            Seguir.objects.get_or_create(seguidor_id=seguidor_id, seguido_id=seguido_id)
    except IntegrityError:
        # Corrida no unique (seguidor, seguido) — idempotente.
        pass
    return {"seguidor_id": seguidor_id, "seguido_id": seguido_id}


def deixar_de_seguir(*, seguidor_id: int, seguido_id: int) -> dict:
    Seguir.objects.filter(seguidor_id=seguidor_id, seguido_id=seguido_id).delete()
    return {"deleted": True, "seguidor_id": seguidor_id, "seguido_id": seguido_id}


def listar_seguidos(*, seguidor_id: int):
    ids = Seguir.objects.filter(seguidor_id=seguidor_id).values("seguido_id")
    return list(queryset_publico().filter(pk__in=ids).order_by("nome", "id"))
