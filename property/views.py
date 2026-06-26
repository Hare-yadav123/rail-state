from .models import SignupModel, UserToken,PropertyType,PropertyStatus,PropertyDetails,ByerAgentVisiterLocationDetails,PropertyImage,PropertyFeature,PropertyFeatureValue,Review,Favorite,ContactRequest,PropertyInquery,AgentProfile,OTPModel,CaptchaModel
from .serializers import SignupSerializer,UserLoginSerializer,PropertyTypeSerializer,PropertyStatusSerializer,PropertyDetailSerializer,UserBusenessLocationSerializer,PropertyImageSerializer,PropertyFeatureSerializer,PropertyFeatureValueSerializer,ReviewSerializer,FavoriteSerializer,ContactRequestSerializer,PropertyInquerySerializer,AgentProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import  status
from django.shortcuts  import get_object_or_404
from django.core.signing import TimestampSigner,BadSignature,SignatureExpired
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .services import IsPostAuthentication,Pagination
from django.core.cache import cache
from PIL import Image,ImageDraw,ImageFont
from django.http import HttpResponse
import random,string
import uuid
import io
from django.conf import settings


class UserListCreateApiviews(APIView):          # user get data and create post
    """User registration api"""
    def get(self,request):
        data = SignupModel.objects.all()
        serializer = SignupSerializer(data,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # token ,creted = UserToken.objects.get_or_create(user_token=user)
            # print(token)
            return Response({'message':'user created successfully','data':serializer.data},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)    



class UserUpdateDelateApiview(APIView):             # user get , update and delete 
    """Register user update and delete api"""

    def get(self,request,pk):
        try:
            # user=SignupModel.objects.get(pk=pk)
            user = get_object_or_404(SignupModel,pk=pk)
            if not user:
                return Response({'mes':'user does not exist'},status=status.HTTP_400_BAD_REQUEST)
            serializer=SignupSerializer(user)
            return Response(serializer.data)
        except SignupModel.DoesNotExist:
            return Response({'mes':'user does not exist'},status=status.HTTP_400_BAD_REQUEST)
        
    def put(self,request,pk):
        user = get_object_or_404(SignupModel,pk=pk)
        serializer = SignupSerializer(user,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'mes':'user data updated '},status=status.HTTP_202_ACCEPTED)
    
    def patch(self,request,pk):
        user = get_object_or_404(SignupModel,pk=pk)
        serializer = SignupSerializer(user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'mes':'partially data updated '},status=status.HTTP_200_ok)

    def delete(self,request,pk):
        user = SignupModel.objects.get(pk=pk)
        user.delete()
        return Response({'message':'user data deleted'},status=status.HTTP_200_OK)


class UserLogin(APIView):               # user login by eamil and password 
    """Email based user login api"""

    def post(self,request):
       userlogin=UserLoginSerializer(data=request.data)
       if userlogin.is_valid():
           user = userlogin.validated_data['user']
           refresh = RefreshToken.for_user(user)
           access = refresh.access_token
           return Response({
               'message':'Logedin successfully',
               'user':{
                   'id':user.id,
                   'email':user.email
               },
               'token':{
                   'refresh':str(refresh),
                   'access':str(access)
               }
           },status = status.HTTP_200_OK)
       return Response(userlogin.errors,status=status.HTTP_400_BAD_REQUEST)


# generate captcha value------this calss is not usable---------------
# class CaptchaGenApi(APIView):
#     permission_classes = [AllowAny]
    
#     def post(self,request):
#         serializer = CaptchGenSrializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         mobileNo=serializer.validated_data['mobileNo']
#         captcha = generate_new_captcha()

#         try:
#             user = SignupModel.objects.get(mobileNo=mobileNo)
#         except SignupModel.DoesNotExist:
#             return Response({"error":"user not registered with this mobile no"},status=status.HTTP_404_NOT_FOUND)
#         if user is None:
#             return Response({"error":"user not registered!"})
#         captext=CaptchaModel.objects.create(
#             mobileNo=user.mobileNo,
#             captcha=captcha,
#             exp_at=timezone.now() + timedelta(minutes=5)
#         )
#         print("captcha", captcha)

#         return Response({ 
#             "captcha":captext.id                      #only for dev, pro=image
#         })
    

# # get captcha image
# from django.http import Http404,HttpResponse
# class GetCaptchaImage(APIView):

#     def get(self,request,*args,**kwargs):
#         pk= kwargs.get("pk")
#         try:
#             capimg = get_object_or_404(CaptchaModel,pk=pk)
#         except CaptchaModel.DoesNotExist:
#             raise Http404("captcha expired")
        
#         image_bytes = gen_cap_img(capimg.captcha)

#         return HttpResponse(
#             image_bytes,
#             content_type="image/png"
#         )

# # captcha based login
# class LoginUsedCaptcha(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = []

#     def post(self, request):
#         serializer = CaptchaLoginSerializer(data=request.data)
        
#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#             refresh = RefreshToken.for_user(user)
#             access = refresh.access_token

#             return Response({
#                 "message":"login successfully",
#                 "user" :{
#                     "id":user.id,
#                     "mobileNo":user.mobileNo,
#                 },
#                 "token":{
#                     "refresh_token":str(refresh),
#                     "access_token":str(access)
#                 },
#             } ,status=status.HTTP_200_OK)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
# -----------------***************------------------------------


singer=TimestampSigner()                    # user password update 
class UserNewpasswordSendlink(APIView):
    """Register user reset password send link api"""

    def post(self,request): 
        email = request.data.get('email')
        try:
            user = SignupModel.objects.get(email=email) 
            token = singer.sign(user.email)
            reset_link = f"http://localhost:5173/reset-password/?token={token}"
            send_mail(
                subject = 'create new password',
                message = f'password reset link sent on your resister email={reset_link}',
                from_email = 'hareyadav@gmail.com',
                recipient_list = [user.email]
            )
            return Response({'message': 'reset link sent on your resister email'},status=status.HTTP_200_OK)
        except SignupModel.DoesNotExist:
            return Response({'message': 'inviled email id'},status=status.HTTP_404_NOT_FOUND)


class UserNewpasswordCreate(APIView):               # user new password create
    """Register user set or update new password api """  

    def post(self,request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        if not token or not  new_password:
            return Response({'message':'token and new password are requred'},status=status.HTTP_404_NOT_FOUND)
        try:
            email = singer.unsign(token,max_age=3600)
            signmodel = SignupModel.objects.get(email=email)
            signmodel.password = make_password(new_password)
            signmodel.save()
            return Response({'messange':'your password updated successfully'},status=status.HTTP_201_CREATED)
        except(BadSignature,SignatureExpired):
            return Response({'error':'token expired'},status=status.HTTP_400_BAD_REQUEST)
        except SignupModel.DoesNotExist:
            return Response({'error':'token does not exist'},status=status.HTTP_400_BAD_REQUEST)


#  user logout 
class UserLogout(APIView):
    """Register User JWT based logout api"""

    authentication_classes = [JWTAuthentication] 
    def post(self,request):
        try:
            refresh = request.data.get('refresh')
            if not refresh:
                return Response({"message":"refresh token not provided"},status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({"message":"user logout successfully and Redirect to login page"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status = status.HTTP_400_BAD_REQUEST)


class PropertyTypeView(APIView):            # property type class
    """ Property type get or post api class, only autherization user can post data """
    permission_classes = [IsPostAuthentication]

    def get(self,request):
        """This fuction is only read data """
        try:
            propertydata = PropertyType.objects.all()
            serializer = PropertyTypeSerializer(propertydata , many=True)
            return Response({'message':'property type found user data','data':serializer.data},status=status.HTTP_200_OK)
        except PropertyType.DoesNotExist:
            return Response({'error':'property type data not found'})

    def post(self,request):                         # create property type
        
        propertytype=PropertyTypeSerializer(data=request.data)
        if propertytype.is_valid():
            propertytype.save()
            return Response({'message':'property status added successfully ✅',
            'data':propertytype.data},
            status=status.HTTP_200_OK)
        return Response({'errors':propertytype.errors},status=status.HTTP_400_BAD_REQUEST)


class PropertyTypeUpdateDelete(APIView):                # property type update delete view
    """This properties type update, delete class"""
    permission_classes = [IsAuthenticated]

    def get(self,request,pk):
        try:
            propertytype=PropertyType.objects.get(pk=pk)
            serializer = PropertyTypeSerializer(propertytype)
            return Response({'messsage':'preprty type found','data':serializer.data},status=status.HTTP_200_OK)
        except PropertyType.DoesNotExist:
            return Response({"error":'data does not exist'},status=status.HTTP_400_BAD_REQUEST)

    def put(self,reauest,pk):
        try:
            pk = PropertyType.objects.get(pk=pk)
            if not pk:
                return Response({'error':'this user is not resistered'},status=status.HTTP_400_BAD_REQUEST)
            ptinstance = PropertyTypeSerializer(pk,data=reauest.data)
            if ptinstance.is_valid():
                ptinstance.save()
                return Response({
                'message':'property type updated successfully ✅',
                'data':ptinstance.data
            },status=status.HTTP_201_CREATED)
        except ValueError:
            return Response({'error':'not valid'},status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        data = PropertyType.objects.get(pk=pk)
        data.delete()
        return Response({'message':'property type deleted successfully'})


 
class PropertyStatusView(APIView):                         # create property status class get and crate post
    """This is properties status API class"""
    permission_classes = [IsPostAuthentication]

    def get(self,request):
        statusdata = PropertyStatus.objects.all()
        serializer = PropertyStatusSerializer(statusdata,many=True)
        return Response({"message":"data found successfully","data":serializer.data},status=status.HTTP_200_OK)
    
    def post(self,request):
        # Create serializer instance with request data
        propertystatus = PropertyStatusSerializer(data=request.data)
        if propertystatus.is_valid():
            propertystatus.save()
            return Response({
                'message':'status added successfully ✅',
                'data':propertystatus.data
            },status=status.HTTP_201_CREATED)
        return Response({'error':propertystatus.errors},status=status.HTTP_400_BAD_REQUEST)


class PropertyStatusUpdateDelete(APIView):              # propert status update delete view 
    """Here user can update and delete there data"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        try:
            pstatus = PropertyStatus.objects.get(pk=pk)
        except PropertyStatus.DoesNotExist:
            return Response({'error':'data does not exixt'},status=status.HTTP_400_BAD_REQUEST)
        serializer = PropertyStatusSerializer(pstatus)
        return Response({'message':'property status found','data':serializer.data},status=status.HTTP_200_OK)
    
    def put(self, request,pk):
        try:
            ps = PropertyStatus.objects.get(pk=pk)
            if not ps:
                return Response({'error':'status does not found'},status=status.HTTP_404_NOT_FOUND)
            serializer = PropertyStatusSerializer(ps,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'status updated successfully','data':serializer.data},status=status.HTTP_200_OK)
        except ValueError:
            return Response({"error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk):
        pk = PropertyStatus.objects.get(pk=pk)
        pk.delete()
        return Response({'message':'data deleted successfully'})



class UserBusinessDetail(APIView):          # Property Details
    """This is user Business post data api class , here pagination rule applied for fetching limited data"""
    pagination_class = Pagination
    permission_classes = [IsPostAuthentication]

    def get_permissions(self):
        """ This is api protection fuction , here user can read data only ,
            if user wnat to list-up there business data , authentication and  autherization is compulsory.
        """
        if self.request.method=="GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self,request):
        """This function only for for get data for reading purpose"""

        businessdetail = PropertyDetails.objects.all()
        paginator = self.pagination_class()
        paginator_ql = paginator.paginate_queryset(businessdetail,request)

        serializer = PropertyDetailSerializer(paginator_ql,many=True)
        return Response({'message':'data found','data':serializer.data},status=status.HTTP_200_OK)

    def post(self,request):

        """Here real state autherise Business users can list-up there property related data """

        try:
            serializer = PropertyDetailSerializer(data=request.data,context={"request": request})
            if serializer.is_valid(raise_exception=True):   
                serializer.save(listed_by=request.user)
                return Response({'message':"data added successfully"},status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response({"error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("SAVE ERROR:", str(e))
            return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       

class UserBusinessDetailUpdateDelete(APIView):

    """Here real state autharize users can get,update and  delete there list-up  property related data """

    permission_classes = [IsPostAuthentication]

    def get(self,request,pk):
        try:
            businessdata = PropertyDetails.objects.get(pk=pk)
            serializer = PropertyDetailSerializer(businessdata)
            return Response({'message':'data found','data':serializer.data},status=status.HTTP_200_OK)
        except PropertyDetails.DoesNotExist:
            return Response({'error':'data does not exist'},status=status.HTTP_400_BAD_REQUEST)
    
    
    def put(self,request,pk):

        """This is update fuction where user can update there data"""

        try:
            businessdataid = get_object_or_404(PropertyDetails,pk=pk)
            if not businessdataid:
                return Response({'error':'data does not exist'},status=status.HTTP_404_NOT_FOUND)
            serializer = PropertyDetailSerializer(businessdataid,data=request.data)   
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'data updated successfully'},status=status.HTTP_200_OK)
            return Response({"error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except :
            return Response({'error':'somthing is wrong'},status=status.HTTP_404_NOT_FOUND)

    def patch(self,request,pk):

        """This is a pratial update function"""

        try:
            businessdataid = get_object_or_404(PropertyDetails,pk=pk)
            serializer = PropertyDetailSerializer(businessdataid,data=request.data,partial=True)   
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'data updated successfully'},status=status.HTTP_200_OK)
            return Response({"error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except :
            return Response({'error':'somthing is wrong'},status=status.HTTP_404_NOT_FOUND)

    def delete(self,reqiest,pk):

        """User can delete there data """

        data = get_object_or_404(PropertyDetails,pk=pk)
        data.delete()
        return Response({'message':'data deleted successfully'},status=status.HTTP_200_OK)
    


class UserBusinessLocationGetPost(APIView):                 # property location class 

    """User location details API"""  

    permission_classes = [IsPostAuthentication]   
            
    def get(self,request):
        locactiondata = ByerAgentVisiterLocationDetails.objects.all()
        serializer = UserBusenessLocationSerializer(locactiondata,many=True)
        return Response({"message":"data found successfully","data":serializer.data},status=status.HTTP_200_OK)

    def post(self,request):
        try:
            serializer = UserBusenessLocationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'location address added'},status=status.HTTP_201_CREATED)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserBusinessLocation(APIView):

    """User Business location update API"""

    def get(self,request,pk):
        try:
            instance = get_object_or_404(ByerAgentVisiterLocationDetails,pk=pk)
            serializer = UserBusenessLocationSerializer(instance)
            return Response({'message':'data found','data':serializer.data},status=status.HTTP_200_OK)
        except ByerAgentVisiterLocationDetails.DoesNotExist:
            return Response({'error':'data not found'},status=status.HTTP_404_NOT_FOUND)
    
    def put(self,reqiest,pk):
        try:
            instance = ByerAgentVisiterLocationDetails.objects.get(pk=pk)
            if not instance:
                return Response({'error':'data not found'},status=status.HTTP_404_NOT_FOUND)
            serializer = UserBusenessLocationSerializer(instance,data=reqiest.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'data updated successfully'},status=status.HTTP_200_OK)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

    def patch(self,reqiest,pk):
        try:
            instance = ByerAgentVisiterLocationDetails.objects.get(pk=pk)
            if not instance:
                return Response({'error':'data not found'},status=status.HTTP_404_NOT_FOUND)
            serializer = UserBusenessLocationSerializer(instance,data=reqiest.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'partially data updated successfully'},status=status.HTTP_200_OK)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

    def delete(self,request,pk):
        data = ByerAgentVisiterLocationDetails.objects.get(pk=pk)
        data.delete()
        return Response({'message':'data deleted successfully'},status=status.HTTP_200_OK)



class UserPropertyImage(APIView):          # property images class 

    """User Business property image api"""     
    permission_classes = [IsPostAuthentication]
    def get(self,request):
        imagedata = PropertyImage.objects.all()
        serializer = PropertyImageSerializer(imagedata,many=True)
        return Response({'massage':'image data found','data':serializer.data},status=status.HTTP_200_OK)
    
    def post(self,request):
        pimages = PropertyImageSerializer(data=request.data)
        if pimages.is_valid():
            pimages.save(uploaded_by=request.user)
            return Response({'message':'image uploaded successfully'},status=status.HTTP_201_CREATED)
        return Response({"error":pimages.errors},status=status.HTTP_400_BAD_REQUEST)   


class UserPropertyImageUpdateDelete(APIView):

    permission_classes = [IsPostAuthentication]

    def get(self,request,pk):
        try:
            pimagedi = get_object_or_404(PropertyImage,pk=pk)
            serializer = PropertyImageSerializer(pimagedi)
            return Response({'message':'data found','data':serializer.data},status=status.HTTP_200_OK)
        except PropertyImage.DoesNotExist:
            return Response({'error':'data not found'},status=status.HTTP_404_NOT_FOUND) 

    def put(self,request,pk):
        try:
            instance = get_object_or_404(PropertyImage,pk=pk)
            serializer = PropertyImageSerializer(instance,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'data updated successfully'},status=status.HTTP_200_OK)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    
    def patch(self,request,pk):
        try:
            instance = get_object_or_404(PropertyImage,pk=pk)
            serializer = PropertyImageSerializer(instance,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'partially data updated successfully'},status=status.HTTP_200_OK)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

    def delete(self,request,pk):
        pimageid = PropertyImage.objects.get(pk=pk)
        pimageid.delete()
        return Response({'message':'data deleted successfully'},status=status.HTTP_200_OK)

# property feature class
class UserPropertyFeature(APIView):

    def get(self,request):
        try:
            featuredata = PropertyFeature.objects.all()
            serializer = PropertyFeatureSerializer(featuredata,many=True)
            return Response(serializer.data)
        except UserPropertyFeature.DoesNotexist:
            return Response({'error':serializer.errors},status=status.HTTP_404_NOT_FOUND)
        
    def post(self,request):
        try:
            serializerdata = PropertyFeatureSerializer(data=request.data)
            if serializerdata.is_valid():
                serializerdata.save()
                return Response({'message':'feature data post successfully','data':serializerdata.data},status=status.HTTP_201_CREATED)
            return Response({'error':serializerdata.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

class UserPropertyFeatureUpdateDelete(APIView):

    def get(self,request,pk):
        try:
            featuredata = get_object_or_404(PropertyFeature,pk=pk)
            serializer = PropertyFeatureSerializer(featuredata)
            return Response({'message':'data found successfully','data':serializer.data},status=status.HTTP_200_OK)
        except PropertyFeature.DoesNotExist:
            return Response({'error':serializer.errors},status=status.HTTP_404_NOT_FOUND)
        
    def put(self,request,pk):
        try:
            featuredata = get_object_or_404(PropertyFeature,pk=pk)
            serializer = PropertyFeatureSerializer(featuredata,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'updated successfully'},status=status.HTTP_200_OK)
            return Response({"error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
    def patch(self,request,pk):
        try:
            featuredata = get_object_or_404(PropertyFeature,pk=pk)
            serializer = PropertyFeatureSerializer(featuredata,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'data partially updated successfully'},status=status.HTTP_200_OK)
            return Response({"error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

    def delete(self,request, pk):
        data = PropertyFeature.objects.get(pk=pk)
        data.delete()
        return Response({'message':'data deleted successfully'},status=status.HTTP_200_OK)
    
# user feature value
class UserFeautureValue(APIView):

    def get(self,request):
        try:
            featurevaluedata = PropertyFeatureValue.objects.all()
            serializer = PropertyFeatureValueSerializer(featurevaluedata,many=True)
            return Response({'message':'data found','data':serializer.data},status=status.HTTP_200_OK)
        except PropertyFeatureValue.DoesNotExist:
            return Response({'message':'data not found'},status=status.HTTP_404_NOT_FOUND)
    
    def post(self,request):
        featurevaluedata = PropertyFeatureValueSerializer(data=request.data)
        if featurevaluedata.is_valid():
            featurevaluedata.save()
            return Response({'message':'data post successfully'},status=status.HTTP_201_CREATED)
        return Response({'error':featurevaluedata.errors})


class UserFeatureValueUpdateDelete(APIView):

    def get(self,request,pk):
        featurevaluedata = get_object_or_404(PropertyFeatureValue,pk=pk)
        serializer = PropertyFeatureValueSerializer(featurevaluedata)
        return Response(serializer.data)
    
    def put(self,request,pk):  #full update
        try:
            featurevaluedata = get_object_or_404(PropertyFeatureValue,pk=pk)
            serializer = PropertyFeatureValueSerializer(featurevaluedata,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'data update successfully'},status=status.HTTP_200_OK)
            return Response({'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self,request,pk):  #partial update
        try:
            featurevaluedata = get_object_or_404(PropertyFeatureValue,pk=pk)
            serializer = PropertyFeatureValueSerializer(featurevaluedata,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'partially data updated successfully'},status=status.HTTP_200_OK)
            return Response({'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self,request,pk):
        featurevaluedata = PropertyFeatureValue.objects.get(pk=pk)
        featurevaluedata.delete()
        return Response({'message':'data deleted'},status=status.HTTP_200_OK)

# user review business logic
class UserReview(APIView):
    def get(self,request):
        try:
            reviewdata = Review.objects.all()
            serializer = ReviewSerializer(reviewdata,many=True)
            return Response({'message':'Review data found','data':serializer.data},status=status.HTTP_200_OK)
        except Review.DoesNotExist:
            return Response({'error':serializer.data},status=status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        try:
            reviewdata = ReviewSerializer(data=request.data)  
            if reviewdata.is_valid():
                reviewdata.save()
                return Response({"message":"your data submitted successafully"},status=status.HTTP_201_CREATED)
            return Response({'error':reviewdata.errors},status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error':'something is wrong'},status=status.HTTP_400_BAD_REQUEST)

class UserReviewUpdateDelete(APIView):
    def get(self,request,pk):
        try:
            reviewdata = Review.objects.get(pk=pk)
            serializer = ReviewSerializer(reviewdata)
            return Response({'message':'data found','data':serializer.data},status=status.HTTP_200_OK)
        except Review.DoesNotExist:
            return Response({'error':'data not found'},status=status.HTTP_404_NOT_FOUND)
        
    def put(self,request,pk):
        try:
            reviewdata = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({'message':'data not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = ReviewSerializer(reviewdata,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'data updated successfully'},status=status.HTTP_200_OK)
        return Response({'message':serializer.errors},status=status.HTTP_200_OK)

    
    def patch(self,request,pk):
        try:
            reviewdata = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({'message':'data not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = ReviewSerializer(reviewdata,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'data partially updated'},status=status.HTTP_200_OK)
        return Response({'message':serializer.errors},status=status.HTTP_200_OK)
    
    def delete(self,request,pk):
        reviewdata = Review.objects.get(pk=pk)
        reviewdata.delete()
        return Response({'message':'data deleted'},status=status.HTTP_200_OK)


#user favvorite businesslogic
class UserFavorite(APIView):
    def get(self,request):
        try:
            favoritedata = Favorite.objects.all()
            serializer = FavoriteSerializer(favoritedata,many=True)
            return Response({'message':'data found','data':serializer.data},status=status.HTTP_200_OK)
        except Favorite.DoesNotExist:
            return Response({'error':serializer.errors},status=status.HTTP_404_NOT_FOUND)
        
    def post(self,request):
        try:
            serializer = FavoriteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'favorite post created successfully'},status=status.HTTP_201_CREATED)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserFavoriteUpdateDelete(APIView):
    
    def get(self,requist,pk):
        favoritedata = get_object_or_404(Favorite,pk=pk)
        serializer = FavoriteSerializer(favoritedata)
        return Response({'message':'data found successfully','data':serializer.data},status=status.HTTP_200_OK)
    
    def put(self,request,pk):
        try:
            favoratedata = get_object_or_404(Favorite,pk=pk)
            serializer = FavoriteSerializer(favoratedata,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'data updated successfully'},status=status.HTTP_200_OK)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self,request,pk):
        try:
            favoratedata = get_object_or_404(Favorite,pk=pk)
            serializer = FavoriteSerializer(favoratedata,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'partially data updated successfully'},status=status.HTTP_200_OK)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self,request,pk):
        inastance = get_object_or_404(Favorite,pk=pk)
        inastance.delete()
        return Response({'message':'data deleted successfully'},status=status.HTTP_200_OK)
    

class UserContactMessage(APIView):

    def get(self,request):
        message = ContactRequest.objects.all()
        serializer = ContactRequestSerializer(message,many=True)
        return Response({'message':'user request found','data':serializer.data},status=status.HTTP_200_OK)
    
    def post(self,request):
        try:
            serializer = ContactRequestSerializer(data=request.data)
            if not serializer:
                return Response({'message':'inviled data found'},status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid():
                serializer.save(sender=request.user)
                return Response({'message':'Your request send successfully'},status=status.HTTP_200_OK)
            return Response({'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserContactRequestUpdate(APIView):
    
    def get(self,request,pk):
        message = get_object_or_404(ContactRequest,pk=pk)
        serializer = ContactRequestSerializer(message)
        return Response({'message':'data found','data':serializer.data})
    
    def put(self,request,pk):
        try:
            message = get_object_or_404(ContactRequest,pk=pk)
            serializer = ContactRequestSerializer(message,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'user request updated'},status=status.HTTP_200_OK)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def patch(self,request,pk):
        try:
            message = get_object_or_404(ContactRequest,pk=pk)
            serializer = ContactRequestSerializer(message,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'user request partially updated'},status=status.HTTP_200_OK)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

    def delete(self,request,pk):
        instance = get_object_or_404(ContactRequest,pk=pk)
        instance.delete()
        return Response({"message":"data deleted successfully"},status=status.HTTP_200_OK)
    

# ==== property inquery===
class UserPropertyInquery(APIView):

    def get(self,request):
        try:
            instance = PropertyInquery.objects.all()
            serializer = PropertyInquerySerializer(instance,many=True)
            return Response({'message':'data found successfully','data':serializer.data},status=status.HTTP_200_OK)
        except PropertyInquery.DoesNotExist:
            return Response({'error':serializer.errors},status=status.HTTP_404_NOT_FOUND)
    def post(self,request):
        try:
            serializer = PropertyInquerySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'data submitted successfully'},status=status.HTTP_201_CREATED)
            return Response({'error':'inviled data'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
class UserPropertyInqueryUpdate(APIView):

    def get(self,request,pk):
        try:
            instance = get_object_or_404(PropertyInquery,pk=pk)
            serializer = PropertyInquerySerializer(instance)
            return Response({'message':'data found successfully','data':serializer.data},status=status.HTTP_200_OK)
        except PropertyInquery.DoesNotExist:
            return Response({'error':serializer.errors},status=status.HTTP_404_NOT_FOUND)
        
    def put(self,request,pk):
        try:
            instance = get_object_or_404(PropertyInquery,pk=pk)
            serializer = PropertyInquerySerializer(instance,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'user request updated'},status=status.HTTP_200_OK)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


    def patch(self,request,pk):
        try:
            instance = get_object_or_404(PropertyInquery,pk=pk)
            serializer = PropertyInquerySerializer(instance,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'user request partially updated'},status=status.HTTP_200_OK)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

    def delete(self,request,pk):
        instance = get_object_or_404(PropertyInquery,pk=pk)
        instance.delete()
        return Response({'message':'data deleted successfully'},status=status.HTTP_200_OK)

# === agent profile===
class CreateAgentProfile(APIView):
    """Real state agent profile"""
    permission_classes = [IsPostAuthentication]

    def get(self,request):
        instanse = AgentProfile.objects.all()
        serializer = AgentProfileSerializer(instanse,many=True)
        return Response({'message':'data found successfully','data':serializer.data},status=status.HTTP_200_OK)

    def post(self,request):
        try:
            serializer = AgentProfileSerializer(data=request.data,context={"request":request})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({'message':'data submitted successfully'},status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response({"error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
           
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


class CreateAgentProfileUpdate(APIView):

    def get(self,request,pk):
        instanse = get_object_or_404(AgentProfile,pk=pk)
        serializer = AgentProfileSerializer(instanse)
        return Response({'message':'data found successfully','data':serializer.data},status=status.HTTP_200_OK)
    
    def put(self,request,pk):
        try:
            instance = get_object_or_404(AgentProfile,pk=pk)
            serializer = AgentProfileSerializer(instance,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'Agent profile updated'},status=status.HTTP_200_OK)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    

    def patch(self,request,pk):
        try:
            instance = get_object_or_404(AgentProfile,pk=pk)
            serializer = AgentProfileSerializer(instance,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'Agent profile partially updated'},status=status.HTTP_200_OK)
            return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


    def delete(self,request,pk):
        instanse = get_object_or_404(AgentProfile,pk=pk)
        instanse.delete()
        return Response({'meassage':'data deleted successfully'})


class LoginIntApi(APIView):
    """Genereat cache base cpatcha  for login register user which not
    save in database, and captcha  verify using captcha key"""

    def post(self,request):
        mobileNo = request.data.get('mobileNo')
        if not mobileNo:
            return Response({"error":"mobile no is required"},status=status.HTTP_400_BAD_REQUEST)
        
        # verified mobile no
        if not SignupModel.objects.filter(mobileNo=mobileNo).exists():
            return Response({"error":["mobileNO does not exist"]},status=status.HTTP_404_NOT_FOUND)

        captcha = "".join(random.choices(string.ascii_uppercase + string.digits,k=6))
        captcha_text=captcha
        captcha_key = f"random_{uuid.uuid4().hex}"
        cache.set(
            captcha_key,
            captcha_text,
            timeout=300
        )

        return Response({
            "captcha_key":captcha_key,
            "captcha" :captcha
        })

class CaptchaImageView(APIView):
    """Create Captcha image for login user"""

    # def get(self, request, captcha_key):
    #     # Get the captcha text from cache
    #     captcha_text = cache.get(captcha_key)
    #     if not captcha_text:
    #         return Response({"error": "Captcha expired"}, status=404)

    #     # Generate an image
    #     font_path = settings.BASE_DIR / "fonts" / "arial.ttf"
    #     try:
    #         fontsize = ImageFont.truetype(font_path,50)
    #     except:
    #         fontsize = ImageFont.load_default()

    #     captcha_text = str(captcha_text)
    #     img = Image.new("RGB", (250, 80), color=(255, 255, 255))
    #     d = ImageDraw.Draw(img)
    #     d.text((20, 10), captcha_text, fill=(0, 0, 0),font=fontsize)  # simple black text

    #     buf = io.BytesIO()
    #     img.save(buf, format="PNG")
    #     buf.seek(0)

    #     return HttpResponse(buf, content_type="image/png")
    def get(self, request, captcha_key):

        captcha_text = cache.get(captcha_key)

        if not captcha_text:
            return Response(
                {"error":"Captcha expired"},
                status=404
            )


        font_path = settings.BASE_DIR / "fonts" / "arial.ttf"


        try:
            fontsize = ImageFont.truetype(
                str(font_path),
                65
            )
            print("FONT OK")

        except Exception as e:
            print("FONT ERROR",e)
            fontsize = ImageFont.load_default()


        img = Image.new(
            "RGB",
            (250,80),
            "white"
        )


        d = ImageDraw.Draw(img)


        d.text(
            (20,10),
            str(captcha_text),
            fill="black",
            font=fontsize
        )


        buf = io.BytesIO()

        img.save(
            buf,
            "PNG"
        )

        buf.seek(0)


        return HttpResponse(
            buf.getvalue(),
            content_type="image/png"
        )

class CatcheLoginApi(APIView):

    """user login using mobile number and captcha value"""
    
    """User login using mobile number and captcha value"""
    def post(self,request):
        """
        Handle POST request to login user using mobile number and captcha value
        """
        mobileNo = request.data.get("mobileNo")
        captcha_key= request.data.get("captcha_key")
        captcha_input = request.data.get("captcha")

        # validate mobile number
        if not mobileNo:
            return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)

        # validate captcha key
        if not captcha_key:
            return Response({"error": "Captcha session expired"}, status=status.HTTP_400_BAD_REQUEST)

        # validate captcha input
        if not captcha_input:
            return Response({"error": "Captcha is required"}, status=status.HTTP_308_PERMANENT_REDIRECT)
        
        # validate captcha input length
        if len(captcha_input) != 6:
            return Response({"error":"captcha must be 6 character long"},status=status.HTTP_400_BAD_REQUEST)

        # get captcha data from cache
        captcha_data = cache.get(captcha_key)
        if not captcha_data:
            return Response({"error":"captcha is expired"},status=status.HTTP_400_BAD_REQUEST)
        
        
        # validate captcha data
        if captcha_data != captcha_input:
            return Response({"error":"captcha does not match"},status=status.HTTP_406_NOT_ACCEPTABLE) 

        # delete captcha key from cache
        cache.delete(captcha_key)

        # generate jwt token
        user = SignupModel.objects.get(mobileNo=mobileNo)
        
        refresh = RefreshToken.for_user(user)
        return Response({
            "access_token":str(refresh.access_token),
            "refresh_token":str(refresh)
        })
