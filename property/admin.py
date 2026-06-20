from django.contrib import admin
from.models import SignupModel, UserToken,PropertyType,PropertyStatus,PropertyDetails,ByerAgentVisiterLocationDetails,PropertyImage,PropertyFeature,PropertyFeatureValue,Review,Favorite,ContactRequest,PropertyInquery,AgentProfile
# Register your models here.

@admin.register(SignupModel)
class SignupAdmin(admin.ModelAdmin):
    list_display = ['id','name','email','password','mobileNo', 'signup_at']
    search_fields = ['name','email']


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ['id','user_token','key','create_at']
    search_fields = ['user_token','ker']
    readonly_fields = ['key']

class OTPAdmin(admin.ModelAdmin):
    list_display = ['mobileNO','otp','isused','cts','exp_at']

class CaptchaAdmin(admin.ModelAdmin):
    list_display = ['mobileNO','captch','cts','exp_at','isused']


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['id','property_typename','cts','uts']


@admin.register(PropertyStatus)
class PropertyStatusAdmin(admin.ModelAdmin):
    list_display = ['id','property_statusname','cts','uts']


@admin.register(PropertyDetails)
class PropertyDetailAdmin(admin.ModelAdmin):
    list_display = ['id','businessname','description','price','property_location','property_type','status_name','image_count','listed_ownername','cts','uts']

    def property_location(self,obj):
        """ return the number of property location name
        """
        return obj.location.city
    property_location.short_description = 'location'

    def property_type(self,obj):
        """ return the number of property name
        """
        return obj.propertytype.name
    property_type.short_description='property type'

    def status_name(self,obj):
        """ 
        return the number of property status name 
        """
        return obj.status.name
    PropertyStatus.short_description='property status'

    def image_count(self, obj):
        """ 
        return the number of property image count 
        """
        return obj.images.count()
    image_count.short_description='images count'

    def listed_ownername(self,obj):
        """ 
        return the number of property user name
        """
        return obj.listed_by.usernmae
    listed_ownername.short_description='listed_by '


@admin.register(ByerAgentVisiterLocationDetails)
class BusinessUserLocationAdmin(admin.ModelAdmin):
    list_display = ['city','state','country','pincode','latitude','longitude','cts','uts']


@admin.register(PropertyImage)
class UserPropertImageAdmin(admin.ModelAdmin):
    list_display = ['image','images','cts','uts']

    def images(self,obj):
        """
        return iamge with uploader name
        """
        return obj.uploaded_by.name
    images.short_description = 'user name'
    
@admin.register(PropertyFeature)
class PropertyFeatureAdmin(admin.ModelAdmin):
    list_display = ['name','cts','uts']

@admin.register(PropertyFeatureValue)
class PropertyFeatureValueAdmin(admin.ModelAdmin):
    list_display = ['property','feature','value','cts','uts']

@admin.register(Review)
class ReviewAmin(admin.ModelAdmin):
    list_display = ['property','user','rating','comment','cts','uts']

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['property','user','cts','uts']
    

@admin.register(ContactRequest)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['sender','property','name','phone','email','message','cts']

@admin.register(PropertyInquery)
class PropertyInqueryAdmin(admin.ModelAdmin):
    list_display = ['property','user','name','phone','email','message','status','cts']

@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ['profileimage','totalsell','properties','user','agencyname','licensenumber','contactnumber','verified','location','cts','uts']