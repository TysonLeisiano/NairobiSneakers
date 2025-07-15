from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.validators import UniqueValidator

from .models import Category, Product, Customer

from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import AbstractBaseUser


 
class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    get_absolute_url = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'name', 'get_absolute_url', 'slug',
            'description', 'price', 'image', 'thumbnail', 'date_added'
        ]
    
    def create(self, validated_data):
        return Product.objects.create(**validated_data)
    
    
    def update(self, instance, validated_data):
        instance.category = validated_data.get('category', instance.category)
        instance.name = validated_data.get('name', instance.name)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance
        instance.thumbnail = instance.make_thumbnail(instance.image)
        instance.save() 
        return instance
        if instance.image:
            instance.thumbnail = instance.make_thumbnail(instance.image)
            instance.save()
            return instance.thumbnail.url
        else:
            return ''
        
    
    def get_image(self, obj):
        if obj.image:
            return f"http://localhost:8000{obj.image.url}"
        return None

    def get_thumbnail(self, obj):
        return obj.get_image()
    

class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'get_absolute_url', 'products']
    
    def create(self, validated_data):
        return Category.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.save()
        return instance
        if instance.slug:
            return instance.get_absolute_url()
        else:
            return ''
        
        
class CustomerSerializer(serializers.ModelSerializer):
    confirm_pass = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = ['email', 'password', 'confirm_pass']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {
                'validators': [
                    UniqueValidator(
                        queryset=Customer.objects.all(),
                        message="This email is already registered. Try logging in."
                    )
                ]
            }
        }

    def validate(self, data):
        if data['password'] != data['confirm_pass']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_pass')  # remove confirm_pass before save
        validated_data['password'] = make_password(validated_data['password'])  # hash password
        return super().create(validated_data)
    

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if not customer.check_password(password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
    