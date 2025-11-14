"""Display all URL patterns"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizapp.settings')
django.setup()

from django.urls import get_resolver

def show_urls(urlpatterns, prefix=''):
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            # This is an include()
            show_urls(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            # This is a URL pattern
            print(f"{prefix}{pattern.pattern}")

print("=" * 60)
print("All Registered URL Patterns")
print("=" * 60)
show_urls(get_resolver().url_patterns)
