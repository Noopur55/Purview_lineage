# from django.test import TestCase
from django.test import TestCase
from rest_framework.test import APITestCase
import pytest
from hypothesis import strategies as st, given
from .models import onboarding_system
from django.urls import reverse, resolve
from .views import role_assignmentss

pytestmark = pytest.mark.django_db


# Create your tests here.
@pytest.mark.django_db
class test_application(APITestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self):
        pass

    def test_models(self):
        oar_id = "AAB.SYS.2033"
        my_model_instance = onboarding_system.objects.create(
            OAR_Id=oar_id, Usecase_Id="active"
        )
        retrieved_models = onboarding_system.objects.get(OAR_Id=oar_id)
        assert retrieved_models.OAR_Id == oar_id

    def test_add(self):
        a, b = 3, 6
        c = a + b
        assert 9

    def test_save_collection(self):
        response = self.client.get(reverse("save_collection"))
        self.assertEqual(response.status_code, 200)

    def test_role_assignments(self):
        url = reverse("role_assignmentss")
        self.assertEqual(resolve(url).func, role_assignmentss)
