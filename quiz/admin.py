from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Quiz, Question, Option, Submission, Answer


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional', {'fields': ('role',)}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_by', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('title', 'category__name')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields['created_by'].initial = request.user
        return form


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4
    fields = ('text',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'text_preview', 'correct_option', 'is_active', 'created_at')
    list_filter = ('is_active', 'quiz__category', 'quiz', 'created_at')
    search_fields = ('text', 'quiz__title')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OptionInline]
    
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question Text'


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'text', 'is_correct', 'created_at')
    list_filter = ('question__quiz__category', 'question__quiz', 'created_at')
    search_fields = ('text', 'question__text')
    readonly_fields = ('created_at', 'updated_at')
    
    def is_correct(self, obj):
        return obj.question.correct_option == obj
    is_correct.boolean = True
    is_correct.short_description = 'Correct Answer'


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'selected_option', 'is_correct', 'answered_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quiz', 'score', 'total_questions', 'correct_answers', 'submitted_at')
    list_filter = ('quiz__category', 'quiz', 'submitted_at', 'user')
    search_fields = ('user__username', 'quiz__title')
    readonly_fields = ('submitted_at',)
    inlines = [AnswerInline]
    
    def total_questions(self, obj):
        return obj.total_questions
    total_questions.short_description = 'Total Questions'
    
    def correct_answers(self, obj):
        return obj.correct_answers
    correct_answers.short_description = 'Correct Answers'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'submission', 'question_preview', 'selected_option', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'submission__quiz__category', 'submission__quiz', 'answered_at')
    search_fields = ('submission__user__username', 'question__text', 'selected_option__text')
    readonly_fields = ('answered_at',)
    
    def question_preview(self, obj):
        return obj.question.text[:50] + "..." if len(obj.question.text) > 50 else obj.question.text
    question_preview.short_description = 'Question'
