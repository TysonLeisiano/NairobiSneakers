from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
    
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
    

        