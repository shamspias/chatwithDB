from rest_framework import serializers
from .models import DatabaseConfig, ApiKey


class DatabaseConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseConfig
        fields = ['type', 'name', 'username', 'password', 'host', 'port', 'external_info']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return DatabaseConfig.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.type = validated_data.get('type', instance.type)
        instance.name = validated_data.get('name', instance.name)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        instance.host = validated_data.get('host', instance.host)
        instance.port = validated_data.get('port', instance.port)
        instance.external_info = validated_data.get('external_info', instance.external_info)
        instance.save()
        return instance


class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = ('username', 'key')
