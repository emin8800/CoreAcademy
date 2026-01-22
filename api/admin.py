from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ContactMessage, User, Course, Expense, Material, Content, StudentWork, Request

# 1. İstifadəçi (User) Modelinin Admin Tənzimləmələri
class CustomUserAdmin(UserAdmin):
    model = User
    
    # Siyahıda görünəcək sütunlar
    list_display = ('username', 'get_full_name', 'email', 'role', 'phone', 'is_staff')
    
    # Süzgəc (sağ tərəfdəki menu)
    list_filter = ('role', 'is_staff', 'is_superuser', 'group', 'gender')
    
    # Axtarış sahələri
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'fin')
    
    # Edit səhifəsində sahələrin qruplaşdırılması
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Şəxsi Məlumatlar', {'fields': ('first_name', 'last_name', 'email', 'phone', 'gender', 'dob', 'age')}),
        ('İşçi Məlumatları', {'fields': ('role', 'fin', 'salary')}),
        ('Tələbə Məlumatları', {'fields': ('group', 'payment')}),
        ('İcazələr', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Tarixlər', {'fields': ('last_login', 'date_joined')}),
    )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Ad Soyad'

# 2. Kurslar
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    search_fields = ('title', 'desc')

# 3. Maliyyə (Xərclər)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('item', 'price', 'date', 'added_by', 'has_receipt')
    list_filter = ('date', 'added_by')
    search_fields = ('item',)
    
    def has_receipt(self, obj):
        return bool(obj.receipt)
    has_receipt.boolean = True
    has_receipt.short_description = 'Qaimə var?'

# 4. Dərs Materialları
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'group', 'author', 'created_at')
    list_filter = ('type', 'group', 'created_at')
    search_fields = ('title', 'group')

# 5. SMM Postları (Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('category', 'short_text', 'date', 'author')
    list_filter = ('category', 'date')
    
    def short_text(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Mətn (Qısa)'

# 6. Tələbə Tapşırıqları
class StudentWorkAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'has_file')
    list_filter = ('date',)
    search_fields = ('student__username', 'student__first_name')

    def has_file(self, obj):
        return bool(obj.file)
    has_file.boolean = True
    has_file.short_description = 'Fayl var?'

# 7. Sorğular (Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('type', 'sender', 'status', 'created_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('sender__username', 'data')
    list_editable = ('status',) # Statusu birbaşa siyahıdan dəyişmək üçün

# Modellərin qeydiyyatı
admin.site.register(User, CustomUserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Content, ContentAdmin)
admin.site.register(StudentWork, StudentWorkAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(ContactMessage)

from .models import Event

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'type')
    list_filter = ('type', 'date')
    search_fields = ('title', 'desc', 'location')

admin.site.register(Event, EventAdmin)