from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, Lesson, Subscription
from lms.paginators import LMSPagination
from lms.serializers import (
    CourseSerializer,
    LessonSerializer,
    SubscriptionRequestSerializer,
    SubscriptionResponseSerializer,
)
from lms.tasks import send_course_update_email
from users.permissions import IsModer, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для просмотра, создания, изменения и удаления курсов."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = LMSPagination

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated, ~IsModer]
        elif self.action in ["retrieve", "update", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsModer | IsOwner]
        elif self.action == "destroy":
            self.permission_classes = [IsAuthenticated, ~IsModer, IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user.groups.filter(name="moderators").exists():
            return Course.objects.all()

        return Course.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        course = serializer.save()
        send_course_update_email.delay(course.pk)


class LessonListAPIView(generics.ListCreateAPIView):
    """View для просмотра списка уроков и создания нового урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LMSPagination

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAuthenticated, ~IsModer]
        else:
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    """View для просмотра, изменения и удаления отдельного урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "PUT", "PATCH"]:
            self.permission_classes = [IsAuthenticated, IsModer | IsOwner]
        elif self.request.method == "DELETE":
            self.permission_classes = [IsAuthenticated, ~IsModer, IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in self.permission_classes]


class SubscriptionAPIView(APIView):

    @extend_schema(
        summary="Добавление или удаление подписки",
        description="Повторный запрос переключает состояние подписки",
        request=SubscriptionRequestSerializer,
        responses={200: SubscriptionResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, pk=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course)

        if subs_item.exists():
            subs_item.delete()
            message = "Подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course)
            message = "Подписка активирована"

        return Response({"message": message})
