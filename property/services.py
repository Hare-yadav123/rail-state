from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import PropertyDetails
from .serializers import PropertyDetailSerializer
from django.db.models import Q


class Pagination(LimitOffsetPagination):        #  Pagination class
    """This class is use for pagination, according this class user can access limited data"""

    default_limit = 30
    # limit_query_param = "limit"
    # offset_query_param= "offset"
    max_limit=100

    def get_paginated_response(self, data):

        return Response({
            "count": self.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "data": data
        })


class IsPostAuthentication(BasePermission):

    """According to this class DreamHomes user can read real state data , if 
        someone want to update or delete or resister new property then user first Register or login 
    """
    def has_permission(self, request, view):
        # print("USER =", request.user)
        # print("AUTHENTICATED =", request.user.is_authenticated)
        if request.method == "GET":
            return True
        return request.user and request.user.is_authenticated
    

# filter city, min price , max price, property type and property status
@api_view(['GET'])
def property_search(request):
    city = request.GET.get('city')
    price = request.GET.get('price')
    propertytype = request.GET.get('propertytype')
    status  = request.GET.get('status')
    search = request.GET.get('search')
    query = Q()

    if search :
        query &= (
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(location__location__icontains=search)
        )

    # now filter
    if city:
        query &= Q(location__location__icontains=city)
    
    if price:
        price = float(price)
        tolerance = price * 0.1
        query &= Q(price__gte=price - tolerance) & Q(price__lte=price + tolerance)
    
    if propertytype:
        query &= Q(propertytype__icontains=propertytype)
    
    if status:
        query &= Q(status__icontains=status)

    properties = PropertyDetails.objects.filter(query)
    serializer = PropertyDetailSerializer(properties,many=True)
    return Response(serializer.data)

    
'''-----------------------------------fetch city name search api---------------------------------'''



@api_view(['GET'])
def city_list(request):
    cities = PropertyDetails.objects.values_list('location', flat=True).distinct()
    return Response(cities)