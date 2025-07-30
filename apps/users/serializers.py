from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import *

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model

    Args:
        serializers (_type_): _description_
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'user_type', 
                 'phone', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationErrror ("Passwords do not match.")
        return attrs
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        
        # Crear perfil según tipo de usuario
        if user.user_type == 'freelancer':
            FreelancerProfile.objects.create(user=user)
        elif user.user_type == 'client':
            ClientProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer para login
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Credenciales inválidas")
            if not user.is_active:
                raise serializers.ValidationError("Usuario inactivo")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("Email y contraseña son requeridos")
        
        return attrs


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer para habilidades
    """
    class Meta:
        model = Skill
        fields = '__all__'


class FreelancerSkillSerializer(serializers.ModelSerializer):
    """
    Serializer para habilidades del freelancer
    """
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FreelancerSkill
        fields = ('id', 'skill', 'skill_id', 'level', 'years_experience', 'created_at')


class FreelancerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para perfil de freelancer
    """
    skills = FreelancerSkillSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = FreelancerProfile
        fields = ('id', 'user_email', 'user_name', 'bio', 'avatar', 'portfolio_url',
                 'linkedin_url', 'github_url', 'title', 'hourly_rate', 'experience_years',
                 'availability', 'rating', 'total_sales', 'completed_projects',
                 'is_verified', 'is_active', 'skills', 'created_at', 'updated_at')
        read_only_fields = ('rating', 'total_sales', 'completed_projects', 'is_verified')


class ClientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para perfil de cliente
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = ClientProfile
        fields = ('id', 'user_email', 'user_name', 'company_name', 'company_website',
                 'bio', 'avatar', 'total_spent', 'projects_posted', 'created_at', 'updated_at')
        read_only_fields = ('total_spent', 'projects_posted')


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para usuario básico
    """
    freelancer_profile = FreelancerProfileSerializer(read_only=True)
    client_profile = ClientProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'user_type',
                 'phone', 'is_verified', 'freelancer_profile', 'client_profile',
                 'created_at', 'updated_at')
        read_only_fields = ('is_verified',)


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Las nuevas contraseñas no coinciden")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Contraseña actual incorrecta")
        return value


class FreelancerSearchSerializer(serializers.ModelSerializer):
    """
    Serializer optimizado para búsqueda de freelancers
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    skills_list = serializers.SerializerMethodField()
    
    class Meta:
        model = FreelancerProfile
        fields = ('id', 'user_name', 'title', 'bio', 'avatar', 'hourly_rate',
                 'rating', 'completed_projects', 'skills_list', 'is_verified')
    
    def get_skills_list(self, obj):
        """Obtener lista simple de skills"""
        return [skill.skill.name for skill in obj.skills.all()[:5]]