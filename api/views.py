from datetime import datetime

from django.core.cache import cache
from django.contrib.auth.hashers import make_password

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Product, Cart, Category, CartItem, Order, Coupon
from .serializers import (
    UserSerializer,
    ProductSerializer,
    CategorySerializer,
    CartItemSerializer,
    CartSerializer,
    OrderSerializer,
    CouponSerializer,
)


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            pass
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Without Using Caching
class ProductViewSet(viewsets.ModelViewSet):
    """
    API to manage products: Add, Edit, Delete, and Fetch.
    """
    queryset = Product.objects 
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"  
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

## Using Caching
# class ProductViewSet(viewsets.ModelViewSet):
#     """
#     API to manage products: Add, Edit, Delete, and Fetch.
#     """
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def list(self, request, *args, **kwargs):
#         cache_key = "product_list"
#         cached_data = cache.get(cache_key)

#         if cached_data:
#             return Response(cached_data)

#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         cache.set(cache_key, serializer.data, timeout=300)  # Cache for 5 minutes (300 sec)

#         return Response(serializer.data)

#     def retrieve(self, request, *args, **kwargs):
#         product_id = kwargs.get("pk")
#         cache_key = f"product_{product_id}"
#         cached_data = cache.get(cache_key)

#         if cached_data:
#             return Response(cached_data)

#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         cache.set(cache_key, serializer.data, timeout=300)  # Cache for 5 minutes

#         return Response(serializer.data)

#     def destroy(self, request, *args, **kwargs):
#         response = super().destroy(request, *args, **kwargs)
#         cache.delete("product_list")
#         return response

#     def update(self, request, *args, **kwargs):
#         response = super().update(request, *args, **kwargs)
#         product_id = kwargs.get("pk")
#         cache.delete(f"product_{product_id}")
#         cache.delete("product_list")
#         return response

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API to manage categories: Add, Edit, Delete, and Fetch.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = Cart.objects(user=request.user).first()
        if not cart:
            return Response({"message": "Cart is empty."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        cart = Cart.objects(user=request.user).first()
        if cart:
            cart.items = []
            cart.save()
            return Response({"message": "Cart cleared successfully."}, status=status.HTTP_200_OK)
        return Response({"message": "Cart is already empty."}, status=status.HTTP_404_NOT_FOUND)

class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']

            product = Product.objects(id=product_id).first()
            if not product:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

            cart = Cart.objects(user=request.user).first()
            if not cart:
                cart = Cart(user=request.user, items=[])
            
            existing_item = next((item for item in cart.items if str(item.product.id) == product_id), None)
            if existing_item:
                existing_item.quantity += quantity  
            else:
                cart.items.append(CartItem(product=product, quantity=quantity))

            cart.save()
            return Response({"message": "Item added to cart"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        product_id = request.data.get("product_id") 
        
        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects(user=request.user).first()
        if not cart:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        filtered_items = [item for item in cart.items if str(item.product.id) != product_id]

        if len(filtered_items) == len(cart.items):
            return Response({"error": "Product not in cart"}, status=status.HTTP_404_NOT_FOUND)

        cart.items = filtered_items
        cart.save()
        
        return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)

class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart = Cart.objects(user=user).first()

        if not cart or not cart.items:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        items = [{"product": str(item.product.id), "quantity": item.quantity, "price": item.product.price} for item in cart.items]
        total_price = sum(item["quantity"] * item["price"] for item in items)

        order = Order(user=user, items=items, total_price=total_price)
        order.save()

        cart.items = []
        cart.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class OrderStatusView(APIView):
    permission_classes = [IsAuthenticated]
    allowed_statuses = {'Pending', 'Shipped', 'Delivered', 'Cancelled'}

    def post(self, request):
        order_id = request.data.get("order_id")
        new_status = request.data.get("status")

        if not order_id:
            return Response({"error": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not new_status:
            return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)

        if new_status not in self.allowed_statuses:
            return Response(
                {"error": f"Invalid status. Allowed statuses: {', '.join(self.allowed_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = Order.objects(id=order_id).first()
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        order.status = new_status
        order.save()

        return Response({"message": "Order status updated successfully", "status": new_status}, status=status.HTTP_200_OK)

class ApplyCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")
        order_id = request.data.get("order_id")

        order = Order.objects(id=order_id).first()
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        coupon = Coupon.objects(code=code).first()
        if not coupon:
            return Response({"error": "Invalid coupon code"}, status=status.HTTP_400_BAD_REQUEST)

        if coupon.expiry_date < datetime.utcnow():
            return Response({"error": "Coupon has expired"}, status=status.HTTP_400_BAD_REQUEST)

        discount_amount = (order.total_price * coupon.discount_percentage) / 100
        order.total_price -= discount_amount
        order.save()

        return Response({"message": "Coupon applied", "new_total": order.total_price}, status=status.HTTP_200_OK)

class CouponCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  

    def post(self, request):
        serializer = CouponSerializer(data=request.data)
        if serializer.is_valid():
            coupon = serializer.save()
            return Response(
                {
                    "id": str(coupon.id),
                    "code": coupon.code,
                    "discount_percentage": coupon.discount_percentage,
                    "expiry_date": coupon.expiry_date,
                    "usage_limit": coupon.usage_limit
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Logged out successfully"}, status=200)