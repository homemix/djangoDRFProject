from api.models import Item
from api.serializers import ItemSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ItemList(APIView):
    """
    List all Items, or create a new Item.
    """

    def get(self, request, format=None):
        Items = Item.objects.all()
        serializer = ItemSerializer(Items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemDetail(APIView):
    """
    Retrieve, update or delete a Item instance.
    """

    def get_object(self, pk):
        try:
            return Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        Item = self.get_object(pk)
        serializer = ItemSerializer(Item)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        Item = self.get_object(pk)
        serializer = ItemSerializer(Item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        Item = self.get_object(pk)
        Item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
