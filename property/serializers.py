from rest_framework import serializers
from .models import SignupModel,UserToken, PropertyType,PropertyStatus,PropertyDetails,PropertyFeature,PropertyFeatureValue,PropertyImage,PropertyInquery,ByerAgentVisiterLocationDetails,Review,ContactRequest,Favorite,AgentProfile,OTPModel,CaptchaModel,Payment
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
import re
from django.utils import timezone
from .models import OTPModel,CaptchaModel

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignupModel
        fields = ['name','email','password','mobileNo']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = SignupModel.objects.create_user(password=password, **validated_data)
        return user
    
# Email based user login
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self,data):
        email = data.get('email').strip().lower()   #remove extra space in email and if anythids in caplital convert in lower case
        password = data.get('password')
        try:
            user = SignupModel.objects.get(email__iexact=email)
            if not user:
                raise serializers.ValidationError({'error':['user email does not exist']})
        except SignupModel.DoesNotExist:
            raise serializers.ValidationError({'email':['user email does not exist']})        
        if not check_password(password,user.password):                                      # match user row password and hash password
            raise serializers.ValidationError({'password':['inviled password']})        
            # Attach user to validated data for later access in view
        data['user'] = user
        return data

# send otp on registered mobile number
class OTPSendSerializer(serializers.Serializer):
    mobileNo = serializers.CharField(max_length=15)

    def validate_mobile_number(self,value):
        if not re.match(r"^\d{10}$",value):
            raise serializers.ValidationError("Enter valied mobile number")
        return value 
    
# login use mobile number
class LoginSerializer(serializers.Serializer):
    mobileNo = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)
    
    def validate(self,data):
        mobileNo = data.get('mobileNo')
        otp = data.get('otp')
        # fetch otp on this particuler mobile number
        record_otp = OTPModel.objects.filter(mobileNo=mobileNo,isused=False).order_by("-cts").first()

        if record_otp is None:
            raise serializers.ValidationError("otp not found or already used")

        if record_otp.otp_expired():
            raise serializers.ValidationError("otp expired")

        if record_otp.otp !=otp:
            raise serializers.ValidationError("inviled otp")
        
        record_otp.isused= True
        record_otp.save()

        user,_ = SignupModel.objects.get_or_create(mobileNo=mobileNo)

        # if not user.is_active:
        #     raise serializers.ValidationError("user is disabled")
        return {'user': user}


class PropertyTypeSerializer(serializers.ModelSerializer):
    # property_typename=serializers.CharField(max_length=120)
    class Meta:
        model = PropertyType
        fields = ['id','property_typename']


class PropertyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyStatus
        fields = ['id','property_statusname']

class PropertyImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    uploaded_by = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = PropertyImage
        fields = ["id",'image','uploaded_by','cts','uts']


class UserBusenessLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ByerAgentVisiterLocationDetails
        fields = ['id','city','state','country','pincode','latitude','longitude']


class PropertyDetailSerializer(serializers.ModelSerializer):

    images_data = PropertyImageSerializer(many=True,read_only=True,source="images")
    propertytype = PropertyTypeSerializer(read_only=True)
    status = PropertyStatusSerializer(read_only=True)
    location = UserBusenessLocationSerializer(read_only=True)
    listed_by = SignupSerializer(read_only=True)

         # POST ke liye 

    images =serializers.PrimaryKeyRelatedField(
        queryset=PropertyImage.objects.all(),
        many=True,
        write_only=True,

    )

    location_id = serializers.PrimaryKeyRelatedField(
        queryset=ByerAgentVisiterLocationDetails.objects.all(),
        write_only=True,
        source="location",
    )
    propertytype_id = serializers.PrimaryKeyRelatedField(
        queryset=PropertyType.objects.all(),
        write_only=True,
        source="propertytype",
    )

    status_id = serializers.PrimaryKeyRelatedField(
        queryset=PropertyStatus.objects.all(),
        write_only=True,
        source="status",
    )
    

    class Meta:
        model = PropertyDetails
        fields =  [
            'id','businessname','description','price',
            "location","propertytype","status","images_data","listed_by",            #for read (get)
            "images","location_id","propertytype_id","status_id"           # for write(post)
        ]         
        read_only_fields = ["listed_by"]         


    def create(self, validated_data):
        imagesIds = validated_data.pop('images', [])
        property_instance = PropertyDetails.objects.create(**validated_data)
        if imagesIds:
            property_instance.images.set(imagesIds)
        return property_instance


class PropertyFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyFeature
        fields = ['id','name']


class PropertyFeatureValueSerializer(serializers.ModelSerializer):
    class Meta : 
        model = PropertyFeatureValue
        fields = ['id','property','feature','value']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id','property','user','rating','comment']

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite 
        fields = ['id','property','user']

class ContactRequestSerializer(serializers.ModelSerializer):
    sender = SignupSerializer(read_only=True)
   
    class Meta:
        model = ContactRequest
        fields = ['id','sender','property','name','phone','email','message','cts']

        read_only = ['sender']

class PropertyInquerySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyInquery
        fields = ['id','property','user','name','phone','email','message','status','cts']

class AgentProfileSerializer(serializers.ModelSerializer):
    properties = PropertyDetailSerializer(read_only=True)                 #only get PropertyDeatil data
    user = SignupSerializer(read_only=True)

    properties = serializers.StringRelatedField(read_only=True)

    properties_id = serializers.PrimaryKeyRelatedField(                 #post new data  from Propertdeatil in AgentProfile 
        queryset = PropertyDetails.objects.all(),
        source="properties",
        write_only=True)
    
    # user = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )

    class Meta:
        model = AgentProfile
        fields = [
            'id',
            'profileimage','totalsell','properties','agencyname',"user",
            'licensenumber','contactnumber','verified','location','cts','uts',
            'properties_id'
            ]
        ready_only_fields = ["user"]

    def validate_license(self, value):
        pattern = r"^[A-Z]{2}-RERA-AGENT\d{4}\d{6}$"
        if not re.match(pattern,value):
            serializers.ValidationError("inviled license Number")
        return value

    def validate_user(self,value):
        if AgentProfile.objects.filter(user=value).exists():
            serializers.ValidationError(
                "User already exist"
            )
        return value

# generate captcha serializer
class CaptchGenSrializer(serializers.Serializer):
    mobileNo = serializers.CharField(max_length=15)

# captcha based login serializer
class CaptchaLoginSerializer(serializers.Serializer):
    mobileNo = serializers.CharField(max_length = 15)
    captcha = serializers.CharField(max_length=6)

    def validate(self, data):
        mobileNo = data.get("mobileNo")
        captcha = data.get("captcha")

        caprecord=CaptchaModel.objects.filter(
            mobileNo=mobileNo,
            isused=False
        ).order_by("-id").first()

        if caprecord is None:
            raise serializers.ValidationError({
                "captcha": "Captcha expired or not found"
            })

        # ✅ SAFE NOW
        if caprecord.captcha != captcha:
            raise serializers.ValidationError({
                "captcha": "Invalid captcha"
            })

        caprecord.isused=True
        caprecord.save()
        
        user,_= SignupModel.objects.get_or_create(mobileNo=mobileNo)
        print(user)
        return {"user":user}
    
class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model=Payment
        fields = "__all__"