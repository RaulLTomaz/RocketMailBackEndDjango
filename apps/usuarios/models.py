from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

from apps.core.constants import EMAIL_MAX_LENGTH, NOME_MAX_LENGTH


class UsuarioQuerySet(models.QuerySet):
    def publico(self):
        return self.only("id", "nome", "email", "foto_url")


class UsuarioManager(BaseUserManager.from_queryset(UsuarioQuerySet)):
    def create_user(self, email: str, nome: str, password: str | None = None, **extra):
        if not email:
            raise ValueError("E-mail é obrigatório.")
        email = self.normalize_email(email).strip().lower()
        usuario = self.model(email=email, nome=nome.strip(), **extra)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario


class Usuario(AbstractBaseUser):
    nome = models.CharField(max_length=NOME_MAX_LENGTH)
    email = models.EmailField(max_length=EMAIL_MAX_LENGTH, unique=True, db_index=True)
    foto_url = models.TextField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    objects = UsuarioManager()

    class Meta:
        db_table = "usuario"

    def __str__(self) -> str:
        return self.email
