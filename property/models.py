from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
import secrets
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator,MaxValueValidator
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
# Create your models here.
class CustomSignupHandle(BaseUserManager):
    def create_user(self, email, password=None, **others):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **others)
        user.set_password(password)                     # hashes password automatically
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **others):
        others.setdefault('is_staff', True)
        others.setdefault('is_superuser', True)
        others.setdefault('is_active', True)
        return self.create_user(email, password, **others)
    
    
class SignupModel(AbstractBaseUser,PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100,unique=True)
    mobileNo = models.CharField(max_length=15,validators=[RegexValidator(regex=r'^\d{10,15}$',message='Enter a valied Number')])
    signup_at =models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomSignupHandle()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
    
    # def save(self,*args,**kwargs):
    #     if not self.password.startswith('pbkfd2_'):
    #         self.password=make_password(self.password)
    #     return super().save(*args,**kwargs)
    
    
    

class UserToken(models.Model):
    user_token = models.OneToOneField(SignupModel,on_delete=models.CASCADE)
    key = models.CharField(max_length=64,unique=True,default=uuid.uuid4)        #secrets.token_hex(32)
    create_at = models.DateTimeField(auto_now_add=True)

    def save(self,*args,**kwargs):
        if not self.key:
            self.key = secrets.token_hex(32)
        return super().save(*args,**kwargs)

class OTPModel(models.Model):
    mobileNo = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    isused = models.BooleanField(default=False)
    cts = models.DateTimeField(auto_now_add=True)
    exp_at = models.DateTimeField()

    def save(self,*args,**kwargs):
        if not self.exp_at:
            self.exp_at = timezone.now() + timedelta(minutes=5)
        return super().save(*args,**kwargs)
    def otp_expired(self):
        return timezone.now() > self.exp_at
    def __str__(self):
        return self.otp
    
class CaptchaModel(models.Model):
    mobileNo = models.CharField(max_length=15)
    captcha = models.CharField(max_length=6)
    cts = models.DateTimeField(auto_now_add=True)
    exp_at = models.DateTimeField()
    isused = models.BooleanField(default=False)
    
    def cap_expired(self):
        return timezone.now() >self.exp_at
    def __str__(self):
        return self.mobileNo
    
# property model 
User = get_user_model()    
class PropertyType(models.Model):
    property_typename=models.CharField(max_length=120)      # appartment, flat, plot
    cts = models.DateTimeField(auto_now_add=True)
    uts = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.property_typename
    


class PropertyStatus(models.Model):
    property_statusname = models.CharField(max_length=120)    #sales , rented , 
    cts = models.DateTimeField(auto_now_add=True)
    uts = models.DateTimeField(auto_now=True)      
 
    def __str__(self):
        return self.property_statusname


class PropertyDetails(models.Model):
    businessname = models.CharField(max_length=120)  # bussiness name
    description = models.TextField()
    price = models.DecimalField(max_digits=12,decimal_places=2)
    location = models.ForeignKey('ByerAgentVisiterLocationDetails',on_delete=models.CASCADE,related_name='property_location')      #forignkey to location model
    propertytype = models.ForeignKey(PropertyType,related_name='property_type',on_delete=models.CASCADE)
    status = models.ForeignKey(PropertyStatus,related_name='status_name',on_delete=models.CASCADE)
    images = models.ManyToManyField('PropertyImage',blank=True,related_name='propertyimage')              #manytomay relation from image model
    listed_by = models.ForeignKey(SignupModel,on_delete=models.CASCADE,related_name='property_ownername')
    cts = models.DateTimeField(auto_now_add=True)
    uts = models.DateTimeField(auto_now=True) 


    def __str__(self):
        return self.businessname
    

# byer,agent and visiter location 
class ByerAgentVisiterLocationDetails(models.Model):
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    pincode = models.CharField(max_length=10)
    latitude = models.FloatField(null=True , blank=True)     # ✅ ADD THIS
    longitude = models.FloatField(null=True , blank=True)
    cts = models.DateTimeField(auto_now_add=True)
    uts = models.DateTimeField(auto_now=True)

    

    def __str__(self):
        return f"{self.city},{self.state},{self.country} {self.pincode}"


# image table
class PropertyImage(models.Model):
    image = models.ImageField(upload_to='properties_image/')
    uploaded_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='images')   #forignkey to user 
    cts = models.DateTimeField(auto_now_add=True)
    uts = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.image}{self.id} by {self.uploaded_by.email}"
    

class PropertyFeature(models.Model):
    name = models.CharField(max_length=120)
    cts = models.DateTimeField(auto_now_add=True)
    uts = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name


class PropertyFeatureValue(models.Model):
    property = models.ForeignKey(PropertyDetails,on_delete=models.CASCADE)
    feature = models.ForeignKey(PropertyFeature,on_delete=models.CASCADE)
    value = models.CharField(max_length=120)
    cts = models.DateTimeField(auto_now_add=True)
    uts = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.value

class Review(models.Model):
    property = models.ForeignKey(PropertyDetails,on_delete=models.CASCADE,related_name='property_reviews')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_reviews')
    rating = models.DecimalField(max_digits=2,decimal_places=1,validators= [MinValueValidator(Decimal(0.0)), MaxValueValidator(Decimal(5.0))])                     # previous rating
    comment = models.CharField(max_length=120)
    cts = models.DateTimeField(auto_now_add=True)
    uts = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} -> {self.property.businessname}:{self.rating}/5"
    

class Favorite(models.Model):
    property = models.ForeignKey(PropertyDetails,on_delete=models.CASCADE,related_name='favoriteproperty')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='userfavorite')
    cts = models.DateTimeField(auto_now_add=True)
    uts = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user','property')   #prevent duplicate fevorite

    def __str__(self):
        return f"{self.property.businessname} {self.user}"
    
class ContactRequest(models.Model):
    sender = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sendercontact')
    property = models.ForeignKey(PropertyDetails,on_delete=models.CASCADE,related_name='propertycontact')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15,validators=[RegexValidator(regex=r'^\d{10,15}$',message='Enter a valid Number')])
    email = models.EmailField(max_length=100)
    message = models.TextField(null=True,blank=True)
    cts = models.DateTimeField(auto_now_add=True)


  
    def __str__(self):
        return f"{self.sender.username} for {self.property.businessname}"


class PropertyInquery(models.Model):
    property = models.ForeignKey(PropertyDetails,on_delete=models.CASCADE,related_name='propertyinquery')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='userinquery')                    #foreignkey to user
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15,validators=[RegexValidator(regex=r'^\d{10,15}$',message='Enter a valid Number')])
    email = models.EmailField(max_length=100)
    message = models.TextField(null=True,blank=True)
    status = models.CharField(max_length=50,default='Pending')
    cts = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return f"Inquery by {self.property},{self.user.email},{self.property.businessname}"

class AgentProfile(models.Model):
    profileimage = models.ImageField(upload_to='properties_image/',null=True,blank=True)
    totalsell = models.PositiveIntegerField(default=0,editable=False)
    properties = models.ForeignKey(PropertyDetails,on_delete=models.CASCADE,related_name='agentprofile')
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='user_agent_profile')         #onetoone from User
    agencyname = models.CharField(max_length=128,blank=True,null=True)
    licensenumber = models.CharField(max_length=120,unique=True)
    contactnumber = models.CharField(max_length=15,validators=[RegexValidator(regex=r'\d{10,15}$')],blank=True,null=True)
    verified = models.BooleanField(default=False)
    location = models.CharField(null=True,blank=True)
    cts = models.DateTimeField(auto_now_add=True)
    uts = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.agencyname
    

from django.db import models
from django.conf import settings


class Payment(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    email = models.EmailField()

    amount = models.PositiveIntegerField()

    razorpay_order_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True
    )

    razorpay_payment_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    razorpay_signature = models.TextField(
        blank=True,
        null=True
    )

    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.status}"