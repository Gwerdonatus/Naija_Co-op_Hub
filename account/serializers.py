from django.contrib.auth.models import User
from rest_framework import serializers
from account.models import Profile

class SignupSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        
        # Create the user
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # The Profile is automatically created by the signal
        user.profile.role = role
        user.profile.save()

        return user
