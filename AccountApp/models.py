from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone


def validate_past_date(value):
    """birth_date must be before today."""
    if value >= timezone.localdate():
        raise ValidationError("La date de naissance doit etre anterieure a aujourd'hui.")


class User(AbstractUser):
    """Custom user model (extension point of the project)."""
    pass


class Specialty(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'specialty'
        verbose_name_plural = 'specialties'

    def __str__(self):
        return self.name


class Doctor(User):
    license_number = models.CharField(
        max_length=6, unique=True, validators=[MinLengthValidator(6)]
    )
    phone = models.CharField(
        max_length=8, validators=[RegexValidator(r'^\d{8}$', "Le numero doit contenir 8 chiffres.")]
    )
    specialties = models.ManyToManyField(Specialty, related_name='doctors', blank=True)

    class Meta:
        verbose_name = 'doctor'
        verbose_name_plural = 'doctors'

    def __str__(self):
        return f"Dr {self.first_name} {self.last_name}"


class Patient(User):
    national_id = models.CharField(
        max_length=8, unique=True,
        validators=[RegexValidator(r'^\d{8}$', "Le CIN doit contenir exactement 8 chiffres.")]
    )
    phone = models.CharField(
        max_length=8, validators=[RegexValidator(r'^\d{8}$', "Le numero doit contenir 8 chiffres.")]
    )
    birth_date = models.DateField(validators=[validate_past_date])

    class Meta:
        verbose_name = 'patient'
        verbose_name_plural = 'patients'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
