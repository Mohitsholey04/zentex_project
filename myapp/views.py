from xml.etree.ElementTree import ParseError
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
from .serializers import AdminOrderSerializer, LoginSerializer, ProductSerializer, RegisterSerializer, Userserializer
from .models import CustomUser, Product
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions
from .permissions import IsAdminUser  # Import custom permission
from .models import Cart, Order, Product
from .serializers import CartSerializer, OrderSerializer
from .permissions import IsCustomer  # We'll create this permission class in the next step.
from rest_framework import status
from rest_framework.exceptions import PermissionDenied




# Register View
class RegisterView(CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

# Login View
class LoginView(CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            user_serialized = Userserializer(user)
            return Response({
                'user': user_serialized.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=401)

# Dashboard View
class DashboardView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        user = request.user
        user_serialized = Userserializer(user)
        return Response({
            'message': 'You are authenticated',
            'user': user_serialized.data
        }, status=200)

# Product List View
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)  # No authentication needed to view products

# Product Create View
class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Admin only permission

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Product Update (Only accessible by Admin)
class ProductUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Admin only permission

    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Product Delete (Only accessible by Admin)
class ProductDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Admin only permission

    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response({"Message": "Product Deleted Successfully."},status=status.HTTP_204_NO_CONTENT)
    

# Order View (for placing orders)
class OrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can place orders

    def post(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items:
            return Response({"error": "Your cart is empty"}, status=400)

        # Create orders from cart items
        orders = []
        for cart_item in cart_items:
            order = Order.objects.create(
                user=user,
                product=cart_item.product,
                quantity=cart_item.quantity
            )
            orders.append(order)

        # Clear the cart after placing the order
        cart_items.delete()

        return Response(OrderSerializer(orders, many=True).data)

    # Get user's orders
    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user)
        return Response(OrderSerializer(orders, many=True).data)
    

# Add to Cart View
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Get the data from the request
            data = request.data

            # Check if the data is a dictionary (a single item)
            if isinstance(data, dict):
                product_id = data.get('product_id')
                quantity = data.get('quantity', 1)  # Default quantity is 1 if not specified
                product = Product.objects.get(id=product_id)

                # Create or update the cart item
                cart_item, created = Cart.objects.get_or_create(
                    user=request.user,
                    product=product,
                    defaults={'quantity': quantity}
                )
                if not created:  # If the cart item exists, update the quantity
                    cart_item.quantity += quantity
                    cart_item.save()

                return Response({"message": "Product added to cart successfully!"}, status=status.HTTP_200_OK)

            else:
                # If the data is not a dictionary (e.g., an array of products), return an error
                return Response({"error": "Expected a JSON object."}, status=status.HTTP_400_BAD_REQUEST)

        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)      

# View Cart
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user).select_related('product')

        if not cart_items.exists():
            return Response({"message": "Your cart is empty."}, status=status.HTTP_200_OK)

        # Serialize cart items
        cart_data = [
            {
                "product_id": item.product.id,
                "product_name": item.product.name,
                "description": item.product.description,
                "price": float(item.product.price),
                "image": item.product.image.url if item.product.image else None,
                "quantity": item.quantity,
                "total": item.quantity * float(item.product.price),
            }
            for item in cart_items
        ]

        return Response(cart_data, status=status.HTTP_200_OK)

# Remove Item from Cart
class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        product_id = request.data.get('product_id')

        # Validate product exists in cart
        try:
            cart_item = Cart.objects.get(user=user, product_id=product_id)
        except Cart.DoesNotExist:
            return Response({"error": "Product not found in cart."}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response({"message": "Product removed from cart successfully."}, status=status.HTTP_200_OK)

# Update Cart Quantity
class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        # Validate quantity
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response({"error": "Quantity must be a positive integer."}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid quantity value."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate product exists in cart
        try:
            cart_item = Cart.objects.get(user=user, product_id=product_id)
        except Cart.DoesNotExist:
            return Response({"error": "Product not found in cart."}, status=status.HTTP_404_NOT_FOUND)

        cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Cart updated successfully."}, status=status.HTTP_200_OK)
    

# Admin Order View: View and update all orders
class AdminOrderView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# Customer Order View: Create and list own orders
class CustomerOrderView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminOrderSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)