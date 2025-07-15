from django.http import Http404
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AbstractBaseUser

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view

from .models import Product, Customer, Category
from .serializers import ProductSerializer, CategorySerializer, CustomerSerializer


# Create your views here.
class ProductList(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class LatestProductList(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()[0:4]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetail(APIView):
    def get_object(self, category_slug, product_slug):
        try:
            return Product.objects.get(category__slug=category_slug, slug=product_slug)
        except Product.MultipleObjectsReturned:
            return Product.objects.filter(category__slug=category_slug, slug=product_slug).first()
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, category_slug, product_slug, format=None):
        product = self.get_object(category_slug, product_slug)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, category_slug, product_slug, format=None):
        product = self.get_object(category_slug, product_slug)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(APIView):
    def get_object(self, category_slug):
        try:
            return Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            raise Http404
        
        
    def get(self, request, category_slug):
        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            return Response({'detail': 'Category not found'}, status=404)

        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)

        return Response({
            "name": category.name,
            "products": serializer.data
        })
    
    

# class RegisterCustomer(APIView):
#     def get(self, request, format=None):
#         customers = Customer.objects.all()
#         serializer = CustomerSerializer(customers, many=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class CustomerRegisterView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def post(self, request, format=None):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful"})
        else:
            return Response(serializer.errors, status=400)
    

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Step 1: Check if user exists
        try:
            user = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return Response(
                {"error": "We couldn't find an account associated with that email address"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Step 2: Authenticate the user
        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {"error": "Invalid password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ✅ Successful login logic
        return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
    

@api_view(['POST'])
def search(request):
    query = request.data.get('query', '')
    if not query:
        return Response({'error': 'No search query provided'}, status=status.HTTP_400_BAD_REQUEST)

    products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)
    
