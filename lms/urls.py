from django.urls import path, include
from rest_framework import routers

from lms.views import (
    CourseViewSet,
    LessonRetrieveAPIView,
    LessonListAPIView,
    SubscriptionAPIView,
)

router = routers.DefaultRouter()
router.register("courses", CourseViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("lessons/", LessonListAPIView.as_view(), name="lesson_list"),
    path("lessons/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson_detail"),
    path("subscriptions/", SubscriptionAPIView.as_view(), name="subscription_toggle"),
]
