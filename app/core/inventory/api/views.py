from .serializer import ProductSerializer
from inventory.models import Product
from rest_framework.views import APIView
from rest_framework.response import Response

class ProductListAV(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)