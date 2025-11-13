from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Category, Quiz, Question, Option, Submission, Answer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')
        read_only_fields = ('id',)


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name', 'role')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'role': {'required': False},
        }
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'password': "Password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        """Create and return a new user."""
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class OptionSerializer(serializers.ModelSerializer):
    """Serializer for Option model."""
    
    class Meta:
        model = Option
        fields = ('id', 'text', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model with nested options."""
    
    options = OptionSerializer(many=True, read_only=True)
    correct_option_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Question
        fields = ('id', 'text', 'correct_option_id', 'is_active', 'options', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_correct_option_id(self, value):
        """Validate that correct_option belongs to this question."""
        if value and hasattr(self, 'instance') and self.instance:
            if not self.instance.options.filter(id=value).exists():
                raise serializers.ValidationError("Selected option does not belong to this question.")
        return value
    
    def update(self, instance, validated_data):
        correct_option_id = validated_data.pop('correct_option_id', None)
        instance = super().update(instance, validated_data)
        
        if correct_option_id is not None:
            if correct_option_id:
                correct_option = instance.options.get(id=correct_option_id)
                instance.correct_option = correct_option
            else:
                instance.correct_option = None
            instance.save()
        
        return instance


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for Quiz model with nested questions."""
    
    questions = QuestionSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    total_questions = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ('id', 'title', 'category', 'category_name', 'is_active', 'created_by', 
                 'created_by_username', 'questions', 'total_questions', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')
    
    def get_total_questions(self, obj):
        return obj.questions.filter(is_active=True).count()
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer model."""
    
    question_text = serializers.CharField(source='question.text', read_only=True)
    selected_option_text = serializers.CharField(source='selected_option.text', read_only=True)
    correct_option_text = serializers.CharField(source='question.correct_option.text', read_only=True)
    
    class Meta:
        model = Answer
        fields = ('id', 'question', 'question_text', 'selected_option', 'selected_option_text', 
                 'correct_option_text', 'is_correct', 'answered_at')
        read_only_fields = ('id', 'is_correct', 'answered_at')


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Submission model."""
    
    answers = AnswerSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    total_questions = serializers.ReadOnlyField()
    correct_answers = serializers.ReadOnlyField()
    
    class Meta:
        model = Submission
        fields = ('id', 'user', 'user_username', 'quiz', 'quiz_title', 'score', 
                 'total_questions', 'correct_answers', 'answers', 'submitted_at')
        read_only_fields = ('id', 'user', 'submitted_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class QuizSubmissionSerializer(serializers.Serializer):
    """Serializer for submitting quiz answers."""
    
    answers = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Dictionary where key is question_id and value is selected_option_id"
    )
    
    def validate_answers(self, value):
        """Validate that all questions are answered and options are valid."""
        quiz = self.context['quiz']
        questions = quiz.questions.filter(is_active=True)
        
        # Check if all questions are answered
        question_ids = set(questions.values_list('id', flat=True))
        answered_question_ids = set(int(k) for k in value.keys())
        
        if question_ids != answered_question_ids:
            missing = question_ids - answered_question_ids
            extra = answered_question_ids - question_ids
            error_msg = []
            if missing:
                error_msg.append(f"Missing answers for questions: {list(missing)}")
            if extra:
                error_msg.append(f"Invalid question IDs: {list(extra)}")
            raise serializers.ValidationError(" ".join(error_msg))
        
        # Validate that selected options belong to their respective questions
        for question_id, option_id in value.items():
            question = questions.get(id=int(question_id))
            if not question.options.filter(id=option_id).exists():
                raise serializers.ValidationError(
                    f"Option {option_id} does not belong to question {question_id}"
                )
        
        return value
    
    def create(self, validated_data):
        """Create submission and answers, calculate score."""
        quiz = self.context['quiz']
        user = self.context['request'].user
        answers_data = validated_data['answers']
        
        # Create submission
        submission = Submission.objects.create(
            user=user,
            quiz=quiz,
            score=0  # Will be calculated below
        )
        
        # Create answers and calculate score
        correct_count = 0
        total_count = len(answers_data)
        
        for question_id, option_id in answers_data.items():
            question = Question.objects.get(id=int(question_id))
            selected_option = Option.objects.get(id=option_id)
            
            answer = Answer.objects.create(
                submission=submission,
                question=question,
                selected_option=selected_option
            )
            
            if answer.is_correct:
                correct_count += 1
        
        # Update submission score
        submission.score = (correct_count / total_count) * 100 if total_count > 0 else 0
        submission.save()
        
        return submission
