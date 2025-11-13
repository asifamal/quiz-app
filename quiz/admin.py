from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Quiz


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
        """Pre-fill created_by with current user on creation."""
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Only for new objects
            form.base_fields['created_by'].initial = request.user
        return form
