from django.db import models


class School(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="schools/logos/", blank=True, null=True)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class AcademicYear(models.Model):
    # FK to School only if you added Step 3
    school = models.ForeignKey(
        "core.School", on_delete=models.CASCADE, related_name="academic_years",
        null=True, blank=True  # remove null/blank if multi-tenant is mandatory
    )
    name = models.CharField(max_length=20, help_text="e.g. 2024/2025")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(
        default=False, help_text="Only one should be True at a time — the year shown in the topbar switcher."
    )

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # enforce only one "current" year
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs) 