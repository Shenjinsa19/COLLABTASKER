from django import forms
from .models import CustomUser

class RegisterForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput)
    password2=forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model=CustomUser
        fields = ['email','name','password']

    def clean(self):
        cleaned_data=super().clean()
        p1=cleaned_data.get('password')
        p2=cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
    
    def save(self,commit=True):
        user=super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
