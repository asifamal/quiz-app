from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer, RegisterSerializer
from .models import User


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    POST /api/auth/register/ to create a new user.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    
    def create(self, request, *args, **kwargs):
        """Override create to return user data after registration."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = UserSerializer(user).data
        return Response(
            {
                'message': 'User registered successfully.',
                'user': user_data
            },
            status=status.HTTP_201_CREATED
        )
