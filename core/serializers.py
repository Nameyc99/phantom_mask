from rest_framework import serializers
from .models import User, Pharmacy, PharmacyOpeningHour, Mask, Transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = '__all__'

class PharmacyOpeningHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyOpeningHour
        fields = '__all__'

class MaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mask
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class PurchaseItemSerializer(serializers.Serializer):
    pharmacy_id = serializers.IntegerField()
    mask_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

class PurchaseRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    purchases = PurchaseItemSerializer(many=True)