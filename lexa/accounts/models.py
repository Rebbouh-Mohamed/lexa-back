from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', _('Admin')),
        ('lawyer', _('Lawyer')),
        ('assistant', _('Assistant')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('blocked', _('Blocked')),
        ('pending', _('Pending')),
        ('suspended', _('Suspended')),
    ]
    
    SUBSCRIPTION_STATUS_CHOICES = [
        ('trial', _('Trial')),
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('cancelled', _('Cancelled')),
        ('expired', _('Expired')),
    ]
    username = models.CharField(_('username'), max_length=150, blank=True, null=True, unique=False)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='lawyer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    subscription_status = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_STATUS_CHOICES,
        default='active'
    )
    subscription_plan = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    bar_number = models.CharField(max_length=50, blank=True)  # For lawyers
    wilaya = models.CharField(max_length=2, blank=True)  # Algerian province code
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sign_in_at = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    specializations = models.JSONField(default=list, blank=True)
    languages = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    
    # Practice information
    law_firm = models.CharField(max_length=200, blank=True)
    years_experience = models.PositiveIntegerField(null=True, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    
    # Tax information (Algerian business registration)
    nif = models.CharField(max_length=50, blank=True, help_text="Numéro d'Identification Fiscale")
    nis = models.CharField(max_length=50, blank=True, help_text="Numéro d'Identification Statistique")
    rc = models.CharField(max_length=50, blank=True, help_text="Registre de Commerce")
    tva = models.CharField(max_length=50, blank=True, help_text="Numéro TVA")
    activity_code = models.CharField(max_length=20, blank=True, help_text="Code d'Activité")
    
    # Additional business information
    company_name = models.CharField(max_length=200, blank=True)
    company_address = models.TextField(blank=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.full_name} Profile"