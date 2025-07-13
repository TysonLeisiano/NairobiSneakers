from io import BytesIO
from PIL import Image

from django.core.files import File
from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        ordering = ('name',)
    
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