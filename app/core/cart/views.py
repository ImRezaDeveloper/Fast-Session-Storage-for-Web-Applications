from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import AddToCartSerializer, CartItemsSerializer, RemoveCartSerializer, UpdateQuantitySerializer, SetQuantitySerializer
from . import redis_cart
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

class GetCartView(APIView):
    def get(self, request):
        session_id = request.session.session_key
        cart_data = redis_cart.get_cart(session_id)
        return Response(cart_data)
    
    def delete(self, request):
        session_id = request.session.session_key
        redis_cart.remove_all_items(session_id)
        return Response({'message': "all of the items removed!"}, status=status.HTTP_204_NO_CONTENT)
    

class AddToCartView(APIView):
    def post(self, request):
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key
        
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        redis_cart.add_to_cart(
            session_id,
            product_id=data['product_id'],
            name=data['name'],
            price=data['price'],
            quantity=data['quantity']
        )
        
        return Response({"message": "Added to cart"}, status=status.HTTP_200_OK)
    
# remove cart
class RemoveCartView(APIView):
    
    def post(self, request):
        session_id = request.session.session_key
        
        serializer = RemoveCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product_id']
        
        redis_cart.remove_cart(session_id, product_id)
        
        return Response({'message': "Removed from cart."})
    
class UpdateCartView(APIView):
    def get(self, request):
        session_id = request.session.session_key
        cart_data = redis_cart.get_cart(session_id)
        return Response(cart_data)
    
    def post(self, request):
        session_id = request.session.session_key
        product_id = request.data.get('product_id')
        action = request.data.get('action', 'inc')
        
        if action == 'inc':
            redis_cart.increment_quantity(session_id, product_id)
        else:
            redis_cart.decrement_quantity(session_id, product_id)
        
        return Response({'message': f'{action} quantity successful'})
    
class SetExiplicityView(APIView):
    def get(self, request):
        session_id = request.session.session_key
        cart_data = redis_cart.get_cart(session_id)
        return Response(cart_data)
    
    def post(self, request):
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key
        
        serializer = SetQuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]
        
        update = redis_cart.set_quantity(session_id, product_id, quantity)
        
        if not update:
            return Response({"error": f'product not found!'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"message": f'quantity updated to {quantity}'})