from django.core.mail import send_mail
from django.conf import settings 


def send_forget_password_mail(email , token ):
    subject = 'votre lien de réinitialisation de mot de passe'
    message = f'Bonjour,Vous avez demandé à réinitialiser votre mot de passe pour notre site.Pour réinitialiser votre mot de passe, veuillez cliquer sur le lien suivant : http://127.0.0.1:8000/change-password/{token}/           Merci de votre confiance ! Cordialement, L"équipe de notre site Retian check'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True