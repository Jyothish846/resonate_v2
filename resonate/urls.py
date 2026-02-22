from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect,render
from django.conf import settings
from django.conf.urls.static import static


def landing_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")
    return render(request, "landing.html")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", landing_view, name="landing"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)