from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from property.models import SignupModel


@receiver(post_save,sender=SignupModel)
def post_created_notification(sender,instance,created,**kwargs):
    try:
        if created:
            send_mail(
                'Welcome!'
                f'Thank you for resistration {instance.name}',
                f'youre account  created successfully',
                'example@gmail.com',
                [instance.email]
            )
    except Exception as e:
        print('Signal email errors',str(e))


@receiver(post_delete,sender=SignupModel)
def profile_delete_notification(sender,instance,**kwargs):
    try:
        send_mail(
            'oh!',
            f'{instance.name}! You deleted your profile',
            'example1@gmail.com',
            [instance.email]
        )
    except Exception as e:
        print('Signal email errors',str(e))