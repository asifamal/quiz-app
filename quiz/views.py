from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db.models import Q
from .serializers import (
    UserSerializer, RegisterSerializer, CategorySerializer, 
    QuizSerializer, QuestionSerializer, OptionSerializer,
    SubmissionSerializer, QuizSubmissionSerializer
)
from .models import User, Category, Quiz, Question, Option, Submission, Answer
from .permissions import IsAdminUser, IsNormalUser, IsOwnerOrAdmin


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    
    def create(self, request, *args, **kwargs):
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


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = Category.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset.order_by('name')


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = Quiz.objects.select_related('category', 'created_by').prefetch_related('questions__options')
        
        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category_id=category)
        
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        created_by = self.request.query_params.get('created_by', None)
        if created_by is not None:
            queryset = queryset.filter(created_by_id=created_by)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        original_quiz = self.get_object()
        
        new_quiz = Quiz.objects.create(
            title=f"{original_quiz.title} (Copy)",
            category=original_quiz.category,
            created_by=request.user,
            is_active=False
        )
        
        for question in original_quiz.questions.all():
            new_question = Question.objects.create(
                quiz=new_quiz,
                text=question.text,
                is_active=question.is_active
            )
            
            correct_option = None
            for option in question.options.all():
                new_option = Option.objects.create(
                    question=new_question,
                    text=option.text
                )
                if question.correct_option == option:
                    correct_option = new_option
            
            if correct_option:
                new_question.correct_option = correct_option
                new_question.save()
        
        serializer = self.get_serializer(new_quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = Question.objects.select_related('quiz', 'correct_option').prefetch_related('options')
        
        quiz = self.request.query_params.get('quiz', None)
        if quiz is not None:
            queryset = queryset.filter(quiz_id=quiz)
        
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('quiz_id', 'id')
    
    @action(detail=True, methods=['post'])
    def add_option(self, request, pk=None):
        question = self.get_object()
        option_text = request.data.get('text', '')
        
        if not option_text:
            return Response({'error': 'Option text is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        option = Option.objects.create(question=question, text=option_text)
        option_serializer = OptionSerializer(option)
        
        return Response(option_serializer.data, status=status.HTTP_201_CREATED)


class ActiveQuizListView(generics.ListAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsNormalUser]
    
    def get_queryset(self):
        return Quiz.objects.filter(
            is_active=True,
            category__is_active=True
        ).select_related('category', 'created_by').prefetch_related(
            'questions__options'
        ).order_by('-created_at')


class SubmitQuizView(APIView):
    permission_classes = [IsAuthenticated, IsNormalUser]
    
    def post(self, request):
        quiz_id = request.data.get('quiz')
        if not quiz_id:
            return Response(
                {'error': 'Quiz ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quiz = Quiz.objects.get(id=quiz_id, is_active=True)
        except Quiz.DoesNotExist:
            return Response(
                {'error': 'Quiz not found or not active'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        active_questions = quiz.questions.filter(is_active=True)
        if not active_questions.exists():
            return Response(
                {'error': 'Quiz has no active questions'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = QuizSubmissionSerializer(
            data=request.data, 
            context={'quiz': quiz, 'request': request}
        )
        
        if serializer.is_valid():
            submission = serializer.save()
            submission_data = SubmissionSerializer(submission).data
            
            return Response({
                'message': 'Quiz submitted successfully',
                'submission': submission_data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSubmissionsView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated, IsNormalUser]
    
    def get_queryset(self):
        queryset = Submission.objects.filter(
            user=self.request.user
        ).select_related('quiz', 'quiz__category').prefetch_related('answers__question', 'answers__selected_option')
        
        quiz = self.request.query_params.get('quiz', None)
        if quiz is not None:
            queryset = queryset.filter(quiz_id=quiz)
        
        min_score = self.request.query_params.get('min_score', None)
        if min_score is not None:
            try:
                queryset = queryset.filter(score__gte=float(min_score))
            except ValueError:
                pass
        
        max_score = self.request.query_params.get('max_score', None)
        if max_score is not None:
            try:
                queryset = queryset.filter(score__lte=float(max_score))
            except ValueError:
                pass
        
        return queryset.order_by('-submitted_at')


class QuizDetailView(generics.RetrieveAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsNormalUser]
    
    def get_queryset(self):
        return Quiz.objects.filter(
            is_active=True,
            category__is_active=True
        ).select_related('category', 'created_by').prefetch_related('questions__options')


class SubmissionDetailView(generics.RetrieveAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'role') and self.request.user.role == 'ADMIN':
            return Submission.objects.all().select_related('user', 'quiz').prefetch_related('answers')
        return Submission.objects.filter(user=self.request.user).select_related('quiz').prefetch_related('answers')
