from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny

from users.models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer, PaymentCreateSerializer
from users.services import create_stripe_product


class PaymentListAPIView(generics.ListAPIView):
    """
    View возвращает список платежей, поддерживает фильтрацию по курсу,
    уроку и способу оплаты, а также сортировку по дате.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date"]


class UserCreateAPIView(generics.CreateAPIView):
    """View для регистрации нового пользователя."""

    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet для просмотра, изменения и удаления профиля текущего пользователя."""

    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)


class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        serializer.save(
            user=self.request.user,
            amount=course.price,
            payment_method="stripe",
        )
