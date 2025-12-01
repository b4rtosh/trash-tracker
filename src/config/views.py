from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from django.conf import settings


def render_home(request):
    return render(request, "home.html")


def health_check(request):
    """Health check endpoint for ALB"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse(
            {"status": "healthy", "database": "connected", "debug": settings.DEBUG}
        )
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=503)
