from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Book


class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.Roles.choices, required=True, label="Register As")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'role',)


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'published_date', 'total_copies', 'description']
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total_copies = cleaned_data.get('total_copies')

        if self.instance.pk:  # If updating
            # Prevent setting total copies lower than what's currently borrowed
            borrowed_books = self.instance.total_copies - self.instance.available_copies
            if total_copies < borrowed_books:
                raise forms.ValidationError(
                    f"Cannot reduce total copies below {borrowed_books}. Books are currently checked out."
                )
            cleaned_data['available_copies'] = total_copies - borrowed_books
        return cleaned_data