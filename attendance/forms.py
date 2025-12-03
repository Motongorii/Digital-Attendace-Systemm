"""
Forms for Digital Attendance System.
"""
from django import forms
from .models import AttendanceSession, Unit, Lecturer


class AttendanceSessionForm(forms.ModelForm):
    """Form for creating attendance sessions."""
    
    class Meta:
        model = AttendanceSession
        fields = ['unit', 'date', 'start_time', 'end_time', 'venue']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-input'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-input'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-input'
            }),
            'venue': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Room 101, Lab A'
            }),
        }


class StudentAttendanceForm(forms.Form):
    """Form for students to mark attendance."""
    
    student_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your full name',
            'autocomplete': 'name'
        })
    )
    
    admission_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g., ADM/2023/001',
            'autocomplete': 'off'
        })
    )
    
    def clean_admission_number(self):
        """Validate admission number format."""
        admission = self.cleaned_data.get('admission_number')
        if admission:
            admission = admission.strip().upper()
        return admission
    
    def clean_student_name(self):
        """Clean and validate student name."""
        name = self.cleaned_data.get('student_name')
        if name:
            name = ' '.join(name.strip().split())  # Normalize whitespace
        return name


class UnitForm(forms.ModelForm):
    """Form for creating/editing units."""
    
    class Meta:
        model = Unit
        fields = ['code', 'name', 'description']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., CS101'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Introduction to Programming'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Unit description...'
            }),
        }

