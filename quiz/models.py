from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model with role choices."""

    ADMIN = 'ADMIN'
    USER = 'USER'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (USER, 'User'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Category(models.Model):
    """Quiz category model."""

    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Quiz(models.Model):
    """Quiz model with category and creator."""

    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='quizzes')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (by {self.created_by.username})"


class Question(models.Model):
    """Question model belonging to a quiz."""

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    correct_option = models.ForeignKey('Option', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.quiz.title} - Q{self.id}: {self.text[:50]}..."


class Option(models.Model):
    """Option model belonging to a question."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Q{self.question.id} - {self.text}"


class Submission(models.Model):
    """User quiz submission model."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    score = models.FloatField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['user', 'quiz', 'submitted_at']  # Allow multiple attempts

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score}%)"

    @property
    def total_questions(self):
        return self.quiz.questions.filter(is_active=True).count()

    @property
    def correct_answers(self):
        return self.answers.filter(is_correct=True).count()


class Answer(models.Model):
    """User answer to a quiz question."""

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='selected_by')
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question__id']
        unique_together = ['submission', 'question']  # One answer per question per submission

    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{self.submission.user.username} - Q{self.question.id} {status}"

    def save(self, *args, **kwargs):
        """Auto-calculate is_correct based on selected option."""
        self.is_correct = self.question.correct_option == self.selected_option
        super().save(*args, **kwargs)
