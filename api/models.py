from django.db import models
from django.contrib.auth.models import AbstractUser

# Bütün istifadəçilər (Rəhbər, Müəllim, Tələbə və s.)
class User(AbstractUser):
    ROLES = (
        ('rehber', 'Rəhbər'),
        ('muellim', 'Müəllim'),
        ('maliyye', 'Maliyyə'),
        ('reseption', 'Resepşn'),
        ('smm', 'SMM'),
        ('hr', 'HR'),
        ('telebe', 'Tələbə'),
    )
    
    role = models.CharField(max_length=20, choices=ROLES)
    phone = models.CharField(max_length=20, blank=True, null=True)
    fin = models.CharField(max_length=20, blank=True, null=True) # İşçilər üçün
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0) # İşçilər üçün
    
    # Tələbə spesifik sahələr
    group = models.CharField(max_length=50, blank=True, null=True)
    payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)

class Course(models.Model):
    AGE_GROUPS = (
        ("3-16", "3-16 yaş"),
        ("16+", "16+ yaş"),
    )

    title = models.CharField(max_length=200)
    desc = models.TextField()

    # ✅ yaş qrupu
    age_group = models.CharField(max_length=10, choices=AGE_GROUPS, default="16+")

    image_file = models.ImageField(upload_to="courses/", blank=True, null=True)
    image_url = models.URLField(max_length=1000, blank=True, null=True)

    @property
    def image(self):
        if self.image_file:
            return self.image_file.url
        return self.image_url


    

class Expense(models.Model):
    item = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)

class Material(models.Model):
    TYPES = (('video', 'Video'), ('file', 'Fayl'), ('text', 'Mətn'), ('link', 'Link'))
    
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=TYPES)
    content = models.TextField(blank=True, null=True) # Link və ya tekst üçün
    file = models.FileField(upload_to='materials/', blank=True, null=True)
    notes = models.TextField(blank=True)
    group = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Content(models.Model): # SMM Postları
    text = models.TextField()
    file = models.FileField(upload_to='smm/', blank=True, null=True)
    category = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField(blank=True, null=True)


class StudentWork(models.Model): # Tələbə Tapşırıqları
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='homeworks/', blank=True, null=True)
    date = models.DateField(auto_now_add=True)

# Sorğular (HR, Resepşn, Müəllim sorğuları üçün ümumi model)
class Request(models.Model):
    TYPES = (('staff_hire', 'İşçi Qəbulu'), ('student_reg', 'Tələbə Qeydiyyatı'), ('student_delete', 'Tələbə Silinməsi'))
    STATUS = (('pending', 'Gözləyir'), ('approved', 'Təsdiq'), ('rejected', 'Rədd'))

    type = models.CharField(max_length=20, choices=TYPES)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    
    # JSON formatında dinamik məlumatlar (ad, soyad, vəzifə və s.)
    data = models.JSONField() 
    
    created_at = models.DateTimeField(auto_now_add=True)

#####################################################################
# =========================
# ✅ EVENTS MODEL
# =========================
class Event(models.Model):
    EVENT_TYPES = (
        ("tedbir", "Tədbir"),
        ("yaris", "Yarış"),
    )

    title = models.CharField(max_length=200)
    desc = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=EVENT_TYPES)

    image_file = models.ImageField(upload_to="events/", blank=True, null=True)
    image_url = models.URLField(max_length=1000, blank=True, null=True)

    @property
    def image(self):
        if self.image_file:
            return self.image_file.url
        return self.image_url

    def __str__(self):
        return self.title
    

from django.db import models

class ContactMessage(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.email}"
