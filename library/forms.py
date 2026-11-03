from django import forms
from django.contrib.auth.models import User
from .models import Book, Student, Faculty

class StudentRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}), label="Confirm Password")
    
    student_id = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Student ID / Roll No'}))
    branch = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Branch (e.g. Computer Science)'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("A student with this Student ID already exists.")
        return student_id

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                student_id=self.cleaned_data.get('student_id'),
                branch=self.cleaned_data.get('branch')
            )
        return user


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'quantity']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Book Title'}),
            'author': forms.TextInput(attrs={'placeholder': 'Author Name'}),
            'category': forms.TextInput(attrs={'placeholder': 'Category'}),
            'quantity': forms.NumberInput(attrs={'min': 0, 'placeholder': 'Quantity'}),
        }


class FacultyCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}), label="Confirm Password")

    faculty_id = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Faculty ID / Employee ID'}))
    department = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Department (e.g. Computer Science)'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone Number (optional)'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username

    def clean_faculty_id(self):
        faculty_id = self.cleaned_data.get('faculty_id')
        if Faculty.objects.filter(faculty_id=faculty_id).exists():
            raise forms.ValidationError("A faculty with this Faculty ID already exists.")
        return faculty_id

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            Faculty.objects.create(
                user=user,
                faculty_id=self.cleaned_data.get('faculty_id'),
                department=self.cleaned_data.get('department'),
                phone=self.cleaned_data.get('phone')
            )
        return user


class FacultyEditForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    department = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Department'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))

    def __init__(self, *args, **kwargs):
        self.faculty = kwargs.pop('faculty', None)
        super().__init__(*args, **kwargs)
        if self.faculty:
            self.fields['first_name'].initial = self.faculty.user.first_name
            self.fields['last_name'].initial = self.faculty.user.last_name
            self.fields['email'].initial = self.faculty.user.email
            self.fields['department'].initial = self.faculty.department
            self.fields['phone'].initial = self.faculty.phone or ''

    def save(self):
        if self.faculty:
            user = self.faculty.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()

            self.faculty.department = self.cleaned_data['department']
            self.faculty.phone = self.cleaned_data.get('phone', '')
            self.faculty.save()
        return self.faculty


class StudentEditForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    branch = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Branch'}))

    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        if self.student:
            self.fields['first_name'].initial = self.student.user.first_name
            self.fields['last_name'].initial = self.student.user.last_name
            self.fields['email'].initial = self.student.user.email
            self.fields['branch'].initial = self.student.branch

    def save(self):
        if self.student:
            user = self.student.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()

            self.student.branch = self.cleaned_data['branch']
            self.student.save()
        return self.student
