from rest_framework import serializers
from .models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()

    def get_lessons_count(self, obj):
        return obj.lessons.count()


    class Meta:
        model = Course
        fields = ["id", "title", "lessons_count"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
