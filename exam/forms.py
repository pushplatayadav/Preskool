from django import forms
from .models import Exam, Grade, ExamSchedule, ExamAttendance, ExamResult


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["name", "school_class", "section", "subject", "exam_date", "start_time", "end_time", "total_marks", "pass_marks", "room", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Exam Name"}),
            "school_class": forms.Select(attrs={"class": "form-select"}),
            "section": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.Select(attrs={"class": "form-select"}),
            "exam_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "total_marks": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter Total Marks", "min": "1"}),
            "pass_marks": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter Pass Marks", "min": "1"}),
            "room": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["name", "min_marks", "max_marks", "grade_point", "description", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Grade Name"}),
            "min_marks": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter Minimum Marks", "min": "0"}),
            "max_marks": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter Maximum Marks", "min": "0"}),
            "grade_point": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter Grade Point", "step": "0.1", "min": "0"}),
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Description"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class ExamScheduleForm(forms.ModelForm):
    class Meta:
        model = ExamSchedule
        fields = ["exam", "school_class", "section", "subject", "exam_date", "start_time", "end_time", "room", "status"]
        widgets = {
            "exam": forms.Select(attrs={"class": "form-select"}),
            "school_class": forms.Select(attrs={"class": "form-select"}),
            "section": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.Select(attrs={"class": "form-select"}),
            "exam_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "room": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class ExamAttendanceForm(forms.Form):
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["exam"].empty_label = "Select Exam"


class ExamResultForm(forms.ModelForm):
    class Meta:
        model = ExamResult
        fields = ["student", "exam", "marks_obtained", "grade", "remarks"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "exam": forms.Select(attrs={"class": "form-select"}),
            "marks_obtained": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter Marks Obtained", "min": "0"}),
            "grade": forms.Select(attrs={"class": "form-select"}),
            "remarks": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Remarks"}),
        }
