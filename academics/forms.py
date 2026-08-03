from django import forms
from .models import (
    SchoolClass, Section, Subject, ClassRoom, Syllabus, TimeTableEntry,
    HomeWork, Schedule,
)


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ["academic_year", "name", "numeric_order"]


SECTION_CHOICES = [("", "Select"), ("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"), ("E", "E"), ("F", "F"), ("G", "G"), ("H", "H"), ("I", "I"), ("J", "J")]


class SectionForm(forms.Form):
    class_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Class Name"}),
    )
    section_name = forms.ChoiceField(
        choices=SECTION_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    no_of_students = forms.IntegerField(
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter no of Students"}),
    )
    no_of_subjects = forms.IntegerField(
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter no of Subjects"}),
    )
    room_number = forms.CharField(
        max_length=20,
        required=False,
        initial="",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Room Number"}),
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
    )

    def clean_no_of_students(self):
        val = self.cleaned_data.get("no_of_students")
        return val if val is not None else 0

    def clean_no_of_subjects(self):
        val = self.cleaned_data.get("no_of_subjects")
        return val if val is not None else 0


class SubjectForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Name"}),
    )
    code = forms.CharField(
        max_length=20,
        required=False,
        initial="",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Code"}),
    )
    type = forms.ChoiceField(
        choices=[("", "Select"), ("theory", "Theory"), ("practical", "Practical")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    is_active = forms.BooleanField(required=False, initial=True)

    def clean_type(self):
        val = self.cleaned_data.get("type")
        return val if val else "theory"


class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ["name", "room_number", "capacity", "floor", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Room Name"}),
            "room_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Room Number"}),
            "capacity": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter Capacity", "min": "1"}),
            "floor": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Floor"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class SyllabusForm(forms.ModelForm):
    class Meta:
        model = Syllabus
        fields = ["school_class", "section", "subject_group", "title", "file", "status"]
        widgets = {
            "school_class": forms.Select(attrs={"class": "form-select"}),
            "section": forms.Select(attrs={"class": "form-select"}),
            "subject_group": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Subject Group"}),
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Title"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].required = False


class TimeTableEntryForm(forms.ModelForm):
    class Meta:
        model = TimeTableEntry
        fields = ["school_class", "section", "subject", "teacher", "room", "day", "start_time", "end_time"]
        widgets = {
            "school_class": forms.Select(attrs={"class": "form-select"}),
            "section": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.Select(attrs={"class": "form-select"}),
            "teacher": forms.Select(attrs={"class": "form-select"}),
            "room": forms.Select(attrs={"class": "form-select"}),
            "day": forms.Select(attrs={"class": "form-select"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control timepicker", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control timepicker", "type": "time"}),
        }


TIME_CHOICES = [
    ("", "Select"),
    ("09:30", "09:30 AM"),
    ("10:30", "10:30 AM"),
    ("11:30", "11:30 AM"),
    ("12:30", "12:30 PM"),
    ("01:30", "01:30 PM"),
    ("02:30", "02:30 PM"),
    ("03:30", "03:30 PM"),
    ("04:30", "04:30 PM"),
    ("05:30", "05:30 PM"),
    ("06:30", "06:30 PM"),
    ("07:30", "07:30 PM"),
]


class ScheduleForm(forms.ModelForm):
    start_time = forms.ChoiceField(choices=TIME_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))
    end_time = forms.ChoiceField(choices=TIME_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = Schedule
        fields = ["schedule_type", "start_time", "end_time", "status"]
        widgets = {
            "schedule_type": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")
        if start and end and start >= end:
            raise forms.ValidationError("End time must be after start time.")
        return cleaned_data

    def clean_start_time(self):
        val = self.cleaned_data.get("start_time")
        from datetime import time
        if val:
            h, m = val.split(":")
            return time(int(h), int(m))
        return val

    def clean_end_time(self):
        val = self.cleaned_data.get("end_time")
        from datetime import time
        if val:
            h, m = val.split(":")
            return time(int(h), int(m))
        return val


class HomeWorkForm(forms.ModelForm):
    class Meta:
        model = HomeWork
        fields = ["school_class", "section", "subject", "homework_date", "submission_date", "attachments", "description", "status"]
        widgets = {
            "school_class": forms.Select(attrs={"class": "form-select"}),
            "section": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.Select(attrs={"class": "form-select"}),
            "homework_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "submission_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }


