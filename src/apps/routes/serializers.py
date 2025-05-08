from rest_framework import serializers
from .models import Address, Route, RoutePoint, RouteSegment


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'postal_code', 'country', 'created_at', 'updated_at']


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id', 'name', 'created_at', 'updated_at', 'distance', 'duration']


class RoutePointSerializer(serializers.ModelSerializer):
    address_text = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    street = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    postal_code = serializers.SerializerMethodField()
    class Meta:
        model = RoutePoint
        fields = ['id', 'route', 'address', 'street', 'city', 'country', 'postal_code', 'latitude', 'longitude', 'sequence_number',
                  'created_at', 'updated_at', 'arrival_time', 'address_text']

    def get_address_text(self, obj):
        return f"{obj.address.street}, {obj.address.city}"

    def get_city(self, obj):
        return obj.address.city

    def get_street(self, obj):
        return obj.address.street

    def get_country(self, obj):
        return obj.address.country

    def get_postal_code(self, obj):
        return obj.address.postal_code
