from django.core.management import BaseCommand

from lms.models import Course, Lesson
from users.models import User, Payment


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        user = User.objects.first()
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        if not user:
            self.stdout.write(
                self.style.ERROR("Нет пользователей")
            )
            return
        
        Payment.objects.create(user=user, course=course, amount=1000, payment_method="cash")
        Payment.objects.create(user=user, lesson=lesson, amount=200, payment_method="transfer")
        Payment.objects.create(user=user, course=course, amount=1500, payment_method="transfer")
        Payment.objects.create(user=user, lesson=lesson, amount=300, payment_method="cash")

        self.stdout.write(self.style.SUCCESS("Payments created"))
