from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import AddToCartSerializer

# Create your views here.

class AddToCartView(APIView):
    def post(self, request):
        # if not request.session.session_key:
        #     request.session.create()
        # session_id = request.session.session_key
        session_id = request.session.session_key or request.session.create()
        
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data['product_id']
        name = serializer.validated_data['name']
        price = serializer.validated_data['price']
        quantity = serializer.validated_data['quantity']
        