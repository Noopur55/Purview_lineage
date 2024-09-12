from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.onboarding_application, name="onboarding_application"),
    path("application", views.application, name="application"),
    path("secret/", views.secret_page, name="save_collection"),
    path(
        "save_collection_to_purview",
        views.save_collection_to_purview,
        name="save_collection_to_purview",
    ),
    ###############ecret will add when will do proper host with correct auth and redirect as that would be required
    # for login_required decorator.##############
    path("role_assignmentss/", views.role_assignmentss, name="role_assignmentss"),
    path("datasource_reg/", views.datasource_reg, name="datasource_reg"),
]

