from django import forms
from .models import Account


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }
        ),
    )
    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm password",
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }
        ),
    )

    class Meta:
        model = Account
        fields = ["first_name", "last_name", "email", "password"]

        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email",
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "First Name",
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Last Name",
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

        return cleaned_data


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
    widget = forms.EmailInput(
                attrs={
                    "placeholder": "Email",
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
                }
            ),)
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }
        ),
    )

        