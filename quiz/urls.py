from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, CategoryViewSet, QuizViewSet, QuestionViewSet,
    ActiveQuizListView, SubmitQuizView, UserSubmissionsView,
    QuizDetailView, SubmissionDetailView
)

app_name = 'quiz'

router = DefaultRouter()
router.register(r'admin/categories', CategoryViewSet)
router.register(r'admin/quizzes', QuizViewSet)
router.register(r'admin/questions', QuestionViewSet)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('quizzes/active/', ActiveQuizListView.as_view(), name='active-quiz-list'),
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/submit/', SubmitQuizView.as_view(), name='submit-quiz'),
    path('quizzes/my-submissions/', UserSubmissionsView.as_view(), name='user-submissions'),
    path('quizzes/submissions/<int:pk>/', SubmissionDetailView.as_view(), name='submission-detail'),
    
    path('', include(router.urls)),
]
