from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from lms.models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    course = Course.objects.get(id=course_id)
    subscriptions = Subscription.objects.filter(course=course)
    emails = list(subscriptions.values_list("user__email", flat=True).distinct())
    if not emails:
        return
    send_mail(
        subject="Изменение курса.",
        message=f"Курс {course.title} был изменен.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails,
    )
