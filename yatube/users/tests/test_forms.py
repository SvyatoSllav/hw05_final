from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class UserFormTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_new_user_is_created(self):
        form_data = {
            'username': 'Svyatoslav',
            'password1': 'alta2002',
            'password2': 'alta2002'
        }
        self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        new_user = User.objects.get(username='Svyatoslav')
        self.assertEqual(new_user.username, 'Svyatoslav')
