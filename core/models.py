from io import BytesIO
from PIL import Image

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.core.files import File
from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f'/{self.slug}/'


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='uploads/thumbnails/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_added',)
        unique_together = ('category', 'slug')
        
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f'/product/{self.category.slug}/{self.slug}/' 
    
    def get_image(self):
        if self.thumbnail:
            return f"http://localhost:8000{self.thumbnail.url}"
        elif self.image:
            thumbnail = self.make_thumbnail(self.image)
            self.thumbnail.save(f"thumb_{self.image.name}", thumbnail, save=True)
            return f"http://localhost:8000{self.thumbnail.url}"
        return None

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img = img.convert('RGB')
        
        img_ratio = img.width / img.height
        target_ratio = size[0] / size[1]

        if img_ratio > target_ratio:
            # Image is wider: crop the sides
            new_height = img.height
            new_width = int(new_height * target_ratio)
        else:
            # Image is taller: crop the top/bottom
            new_width = img.width
            new_height = int(new_width / target_ratio)

        left = (img.width - new_width) / 2
        top = (img.height - new_height) / 2
        right = (img.width + new_width) / 2
        bottom = (img.height + new_height) / 2

        img = img.crop((left, top, right, bottom))
        img = img.resize(size, Image.ANTIALIAS)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)
        return File(thumb_io, name=image.name)
    


class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)




class Customer(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No 'username' here

    def __str__(self):
        return self.email
