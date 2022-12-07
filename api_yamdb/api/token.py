from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator


def send_email_code(user):
    confirm_code = default_token_generator.make_token(user=user)
    subj = 'Код подтверждения'
    message = confirm_code
    from_email = 'admin@gmail.com'
    to_email = user.email
    return send_mail(subj, message, from_email, [to_email],
                     fail_silently=False)
