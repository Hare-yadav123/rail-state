import razorpay
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status 
from property.models import Payment

# razorpay client object
client = razorpay.Client(
   auth = (
        settings.RAZORPAY_KEY_ID , 
        settings.RAZORPAY_KEY_SECRET
    )
)

# -----------------------------order created-------------------------------

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_order(request):
    
    user =  request.user         
    amount = request.data.get("amount")

    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    payment = Payment.objects.create(
        user=user,
        email=request.data.get("email"),
        amount=amount,
        razorpay_order_id=razorpay_order["id"],
        status="PENDING"
    )

    return Response({
        "message": "Order created",
        "order_id": payment.razorpay_order_id,
        "amount": payment.amount,
        "key": settings.RAZORPAY_KEY_ID
    }, status=status.HTTP_201_CREATED)



# ------------------------veryfy payment---------------------
@api_view(["POST"])
def verify_payment(request):

    data = request.data

    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_signature = data.get("razorpay_signature")

    try:

        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })

        payment = Payment.objects.get(
            razorpay_order_id=razorpay_order_id
        )

        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = "SUCCESS"

        payment.save()

        return Response({
            "message": "Payment Successful"
        })

    except:

        return Response({
            "message": "Payment Failed"
        }, status=400)