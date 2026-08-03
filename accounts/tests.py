from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from accounts.forms import RegisterForm

User = get_user_model()


class RegisterFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "password1": "SecurePassword123!",
            "password2": "SecurePassword123!",
            "agree_terms": True,
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_passwords_do_not_match(self):
        form_data = {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "password1": "SecurePassword123!",
            "password2": "DifferentPassword123!",
            "agree_terms": True,
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
        self.assertEqual(form.errors["password2"][0], "Passwords do not match.")

    def test_missing_agree_terms(self):
        form_data = {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "password1": "SecurePassword123!",
            "password2": "SecurePassword123!",
            "agree_terms": False,
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("agree_terms", form.errors)

    def test_email_already_exists(self):
        User.objects.create_user(
            username="existing_user",
            email="jane.doe@example.com",
            password="SomeOldPassword123!"
        )
        form_data = {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "password1": "SecurePassword123!",
            "password2": "SecurePassword123!",
            "agree_terms": True,
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertEqual(form.errors["email"][0], "An account with this email already exists.")

    def test_save_method_creates_user_properly(self):
        form_data = {
            "name": "Jane Mary Doe",
            "email": "jane.doe@example.com",
            "password1": "SecurePassword123!",
            "password2": "SecurePassword123!",
            "agree_terms": True,
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, "jane.doe@example.com")
        self.assertEqual(user.first_name, "Jane Mary")
        self.assertEqual(user.last_name, "Doe")
        # Username should be auto-generated from email prefix
        self.assertEqual(user.username, "jane.doe")

    def test_username_collision_handling(self):
        # Create an existing user with username 'jane.doe'
        User.objects.create_user(
            username="jane.doe",
            email="other@example.com",
            password="Password123!"
        )
        form_data = {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "password1": "SecurePassword123!",
            "password2": "SecurePassword123!",
            "agree_terms": True,
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        # Should resolve collision by appending a number
        self.assertEqual(user.username, "jane.doe1")


class RegisterViewTest(TestCase):
    def test_register_get_request(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_post_valid_data(self):
        form_data = {
            "name": "Alex Smith",
            "email": "alex.smith@example.com",
            "password1": "SecurePassword123!",
            "password2": "SecurePassword123!",
            "agree_terms": True,
        }
        response = self.client.post(reverse("accounts:register"), data=form_data)
        # Should redirect to home
        self.assertRedirects(response, reverse("home"))

        # Verify user is created and logged in
        user = User.objects.get(email="alex.smith@example.com")
        self.assertEqual(user.first_name, "Alex")
        self.assertEqual(user.last_name, "Smith")
        self.assertEqual(user.username, "alex.smith")
