from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image
import os


class User(AbstractUser):
    """User model

    Args:
        AbstractUser (_type_): _description_

    Returns:
        _type_: _description_
    """
    USER_TYPES = (
        ('freelancer', 'Freelancer'),
        ('client', 'Cliente'),
        ('admin', 'Administrador'),
    )
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='freelancer')
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


class FreelancerProfile(models.Model):
    """Freelancer profile model

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    SKILL_LEVELS = (
        ('beginner', 'Principiante'),
        ('intermediate', 'Intermedio'),
        ('advanced', 'Avanzado'),
        ('expert', 'Experto'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    bio = models.TextField(max_length=1000, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    
    # Información profesional
    title = models.CharField(max_length=100, blank=True)  # ej: "Full Stack Developer"
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    experience_years = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        blank=True, null=True
    )
    availability = models.CharField(max_length=50, blank=True)  # ej: "Full-time", "Part-time"
    
    # Métricas
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        default=0.0
    )
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    completed_projects = models.PositiveIntegerField(default=0)
    
    # Control
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Override save para redimensionar avatar"""
        super().save(*args, **kwargs)
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                img.thumbnail((300, 300))
                img.save(self.avatar.path)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"
    
    class Meta:
        verbose_name = 'Perfil Freelancer'
        verbose_name_plural = 'Perfiles Freelancers'


class Skill(models.Model):
    """
    Habilidades/tecnologías
    """
    CATEGORIES = (
        ('programming', 'Programación'),
        ('design', 'Diseño'),
        ('marketing', 'Marketing'),
        ('writing', 'Escritura'),
        ('other', 'Otro'),
    )
    
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    icon = models.CharField(max_length=100, blank=True)  # Para iconos de FontAwesome
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    class Meta:
        verbose_name = 'Habilidad'
        verbose_name_plural = 'Habilidades'
        ordering = ['category', 'name']


class FreelancerSkill(models.Model):
    """
    Relación freelancer-habilidad con nivel
    """
    LEVELS = (
        ('beginner', 'Principiante'),
        ('intermediate', 'Intermedio'),
        ('advanced', 'Avanzado'),
        ('expert', 'Experto'),
    )
    
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVELS)
    years_experience = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('freelancer', 'skill')
        verbose_name = 'Habilidad del Freelancer'
        verbose_name_plural = 'Habilidades del Freelancer'
    
    def __str__(self):
        return f"{self.freelancer.user.get_full_name()} - {self.skill.name} ({self.get_level_display()})"


class ClientProfile(models.Model):
    """
    Perfil para clientes
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    company_name = models.CharField(max_length=100, blank=True)
    company_website = models.URLField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Métricas
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    projects_posted = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Override save para redimensionar avatar"""
        super().save(*args, **kwargs)
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                img.thumbnail((300, 300))
                img.save(self.avatar.path)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company_name or 'Cliente'}"
    
    class Meta:
        verbose_name = 'Perfil Cliente'
        verbose_name_plural = 'Perfiles Clientes'