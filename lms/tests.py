from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="test_password",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="test_password",
        )
        self.moderator = User.objects.create_user(
            email="moderator@example.com",
            password="test_password",
        )
        moderators_group = Group.objects.create(name="moderators")
        self.moderator.groups.add(moderators_group)

        self.course = Course.objects.create(
            title="Python course",
            description="Python course description",
            owner=self.owner,
        )
        self.lesson = Lesson.objects.create(
            title="Django lesson",
            description="Django lesson description",
            video_url="https://youtube.com/watch?v=test",
            course=self.course,
            owner=self.owner,
        )

    def test_lesson_list(self):
        self.client.force_authenticate(user=self.owner)

        url = reverse("lesson_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.lesson.pk)

    def test_lesson_create(self):
        self.client.force_authenticate(user=self.owner)

        data = {
            "title": self.lesson.title,
            "description": self.lesson.description,
            "video_url": self.lesson.video_url,
            "course": self.course.pk,
        }
        url = reverse("lesson_list")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

        created_lesson = Lesson.objects.get(pk=response.data["id"])
        self.assertEqual(created_lesson.owner, self.owner)

    def test_lesson_retrieve(self):
        self.client.force_authenticate(user=self.owner)

        url = reverse("lesson_detail", kwargs={"pk": self.lesson.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.lesson.pk)

    def test_lesson_update(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("lesson_detail", kwargs={"pk": self.lesson.pk})
        data = {
            "title": "Updated Django Lesson",
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Updated Django Lesson")

    def test_lesson_delete(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("lesson_detail", kwargs={"pk": self.lesson.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def test_other_user_cannot_update_lesson(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("lesson_detail", kwargs={"pk": self.lesson.pk})
        data = {
            "title": "Updated Django Lesson",
        }
        original_title = self.lesson.title
        response = self.client.patch(url, data)

        self.lesson.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.lesson.title, original_title)

    def test_other_user_cannot_delete_lesson(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("lesson_detail", kwargs={"pk": self.lesson.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def test_moderator_can_update_lesson(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson_detail", kwargs={"pk": self.lesson.pk})
        data = {
            "title": "Updated Django Lesson",
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Updated Django Lesson")

    def test_moderator_cannot_create_lesson(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson_list")
        data = {
            "title": "Moderator lesson",
            "description": "Lesson created by moderator",
            "video_url": "https://youtube.com/watch?v=moderator",
            "course": self.course.pk,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_moderator_cannot_delete_lesson(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson_detail", kwargs={"pk": self.lesson.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def test_unauthenticated_user_cannot_access_lessons(self):
        url = reverse("lesson_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="test_password",
        )
        self.course = Course.objects.create(
            title="Python course",
            description="Python course description",
            owner=self.owner,
        )

    def test_add_subscription(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("subscription_toggle")
        data = {
            "course_id": self.course.pk,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Subscription.objects.filter(user=self.owner, course=self.course).exists()
        )
        self.assertEqual(
            response.data["message"],
            "Подписка активирована",
        )

    def test_delete_subscription(self):
        Subscription.objects.create(
            user=self.owner,
            course=self.course,
        )
        self.client.force_authenticate(user=self.owner)
        url = reverse("subscription_toggle")
        data = {
            "course_id": self.course.pk,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            "Подписка удалена",
        )
        self.assertFalse(
            Subscription.objects.filter(user=self.owner, course=self.course).exists()
        )

    def test_course_subscription_status(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("course-detail", kwargs={"pk": self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_subscribed"])

        Subscription.objects.create(
            user=self.owner,
            course=self.course,
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_subscribed"])
