from rest_framework import serializers, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Product
from .models import Cart, Order, Product


# User Serializer
class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'phone', 'address', 'role')

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'phone', 'address', 'role')
        
    def create(self, validated_data):
        # Ensure role is either 'admin' or 'customer'
        role = validated_data.get('role', 'customer')  # Default to 'customer'
        if role not in ['admin', 'customer']:
            raise serializers.ValidationError("Role must be either 'admin' or 'customer'")
        
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', ''),
            role=role,
        )
        return user

# Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def update(self, instance, validated_data):
        # Allow partial update including the image field
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    

    
# Product Create View
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)  # Only authenticated users can access this view

    def perform_create(self, serializer):
        # Check if the user is an admin
        user = self.request.user
        if user.role != 'admin':
            raise PermissionDenied("You do not have permission to add products.")
        
        # Proceed with saving the product if the user is admin
        serializer.save()

# Product List View
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['user', 'product', 'quantity']

# # Order Serializer
# class OrderSerializer(serializers.ModelSerializer):
#     product = serializers.StringRelatedField()  # Show product name instead of ID
#     user = serializers.StringRelatedField()  # Show username instead of ID

#     class Meta:
#         model = Order
#         fields = ('id', 'product', 'quantity', 'ordered_at', 'status')

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display username instead of ID
    product = serializers.StringRelatedField()  # Display product name instead of ID

    class Meta:
        model = Order
        fields = ('id', 'user', 'product', 'quantity', 'ordered_at', 'status')

# Admin Order Serializer
class AdminOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'