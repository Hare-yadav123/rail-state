from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from property.models import SignupModel
from django.conf import settings

@receiver(post_save,sender=SignupModel)
def post_created_notification(sender,instance,created,**kwargs):
    try:
        if created:
            send_mail(
                'Welcome!',
                f'Thank you for resistration {instance.name}',
                f'youre account  created successfully',
                settings.EMAIL_HOST_USER,
                [instance.email],
                fail_silently=False
            )
    except Exception as e:
        print('Signal email errors',str(e))


@receiver(post_delete,sender=SignupModel)
def profile_delete_notification(sender,instance,**kwargs):
    try:
        send_mail(
            'oh!',
            f'{instance.name}! You deleted your profile',
            settings.EMAIL_HOST_USER,
            [instance.email],
            fail_silently=False
        )
    except Exception as e:
        print('Signal email errors',str(e))