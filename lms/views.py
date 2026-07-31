from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, generics

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "update", "partial_update"]:
            return [IsModer()]
        return [IsAuthenticated()]


class LessonListAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsModer()]
        return [IsAuthenticated()]


class LessonRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ["GET", "PUT", "PATCH"]:
            return [IsModer()]
        return [IsAuthenticated()]
