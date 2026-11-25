from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        CONFIRMED = 'CONFIRMED', 'Confirm\u00e9'
        CANCELLED = 'CANCELLED', 'Annul\u00e9'

    reason = models.TextField()
    prescription = models.FileField(
        upload_to='prescriptions/', blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    duration_minutes = models.PositiveIntegerField(default=30)
    appointment_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    doctor = models.ForeignKey(
        'AccountApp.Doctor', on_delete=models.CASCADE, related_name='appointments'
    )
    patient = models.ForeignKey(
        'AccountApp.Patient', on_delete=models.CASCADE, related_name='appointments'
    )

    class Meta:
        ordering = ['appointment_date']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date'],
                name='unique_doctor_appointment_date',
            )
        ]

    def clean(self):
        super().clean()
        if not self.appointment_date:
            return
        # Rule applies only on creation or when the date changed
        date_changed = self._state.adding
        if not date_changed and self.pk:
            old = Appointment.objects.filter(pk=self.pk).values_list('appointment_date', flat=True).first()
            date_changed = old != self.appointment_date
        if date_changed and self.appointment_date <= timezone.now():
            raise ValidationError(
                {'appointment_date': "La date du rendez-vous doit etre posterieure a maintenant."}
            )

    def __str__(self):
        return f"{self.patient} -> {self.doctor} le {self.appointment_date:%d/%m/%Y %H:%M}"
