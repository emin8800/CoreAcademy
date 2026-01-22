from django.contrib import admin
from django.utils.timezone import now
from .models import (
    CommentTranslation, CustomUser, Story, UserForm, PlaceMap, QRCode, Comment, PlaceReview,
    PlaceURL, Note, TopicAnalysis, CommentAnalysis, PlaceReviewAnalysis,
    AccountActionRequest, CustomerConfirm,ReviewTranslation,WeeklySchedule
)
from .utils import delete_user_completely

from django.contrib import admin
from .models import CommentTranslation, ReviewTranslation

@admin.register(CommentTranslation)
class CommentTranslationAdmin(admin.ModelAdmin):
    pass   # heç bir əlavə özəllik olmadan sadəcə admin paneldə çıxacaq

@admin.register(ReviewTranslation)
class ReviewTranslationAdmin(admin.ModelAdmin):
    pass

# ✅ CustomUser Admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_verified', 'is_suspended')
    list_filter = ('is_verified', 'is_suspended', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')


# ✅ UserForm Admin
# @admin.register(UserForm)
# class UserFormAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'gender', 'age_range', 'selected_place', 'created_at','uid','id')
#     list_filter = ('gender', 'age_range', 'created_at')
#     search_fields = ('first_name', 'last_name', 'email', 'phone_number')


from django.contrib import admin
from django.db import models
from accounts.models import UserForm, CustomerBonus, BusinessCustomer

# ✅ UserForm Admin 19u yusif
@admin.register(UserForm)
class UserFormAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "gender",
        "age_range",
        "selected_place",
        "created_at",
        "uid",
        "id",

        "get_businesses",  # ✅ hansı bizneslərdə var

        "get_total_bonus_balance",
        "get_total_spent_bonus",
        "get_ranks",
    )

    list_filter = ("gender", "age_range", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone_number")

    # ✅ user hansı bizneslərə bağlıdır
    def get_businesses(self, obj):
        owners = BusinessCustomer.objects.filter(customer=obj).select_related("owner")
        return " | ".join([m.owner.username for m in owners]) if owners else "-"
    get_businesses.short_description = "Businesses"

    def get_total_bonus_balance(self, obj):
        return CustomerBonus.objects.filter(customer=obj).aggregate(
            total=models.Sum("bonus_balance")
        )["total"] or 0
    get_total_bonus_balance.short_description = "Total Bonus Balance"

    def get_total_spent_bonus(self, obj):
        return CustomerBonus.objects.filter(customer=obj).aggregate(
            total=models.Sum("total_spent_bonus")
        )["total"] or 0
    get_total_spent_bonus.short_description = "Total Spent Bonus"

    def get_ranks(self, obj):
        bonuses = CustomerBonus.objects.filter(customer=obj).select_related("rank", "owner")
        result = []
        for b in bonuses:
            rank_code = b.rank.code if b.rank else "bronze"
            result.append(f"{b.owner.username}: {rank_code}")
        return " | ".join(result) if result else "-"
    get_ranks.short_description = "Ranks"


# ✅ PlaceMap Admin
@admin.register(PlaceMap)
class PlaceMapAdmin(admin.ModelAdmin):
    list_display = ('branch_name', 'user', 'place_id', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('branch_name', 'place_id')


# ✅ QRCode Admin
@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('uid', 'user', 'text', 'created_at', 'get_place_maps', 'qr_url')
    search_fields = ('uid', 'user__email', 'text')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('uid', 'created_at', 'qr_image')

    def get_place_maps(self, obj):
        return ", ".join([place.branch_name for place in obj.place_maps.all()])
    get_place_maps.short_description = 'Əlaqəli Şöbələr'


# ✅ Comment Admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user_full_name", "qr_code", "sentiment", "stars", "created_at", "place_map")
    list_filter = ("sentiment", "created_at", "stars", "place_map")
    search_fields = ("user__first_name", "user__last_name", "comment")

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_full_name.short_description = "İstifadəçi"


# ✅ PlaceReview Admin
@admin.register(PlaceReview)
class PlaceReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'place_id', 'author_name', 'stars', 'created_at', 'branch_name', 'sentiment')
    search_fields = ('user__email', 'place_id', 'author_name', 'branch_name__branch_name')
    list_filter = ('stars', 'created_at', 'branch_name', 'sentiment')
    ordering = ('-created_at',)


# ✅ PlaceURL Admin
@admin.register(PlaceURL)
class PlaceURLAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'url', 'created_at', 'place_name', 'uid')
    search_fields = ('place_map__user__email', 'url', 'place_name', 'uid')
    list_filter = ('created_at',)

    def get_user(self, obj):
        if obj.place_map and obj.place_map.user:
            return obj.place_map.user.email
        return "Yoxdur"
    get_user.short_description = 'İstifadəçi'
    get_user.admin_order_field = 'place_map__user__email'


# ✅ Note Admin
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'created_at')
    search_fields = ('title', 'user__email')
    list_filter = ('created_at',)


# ✅ TopicAnalysis Admin
@admin.register(TopicAnalysis)
class TopicAnalysisAdmin(admin.ModelAdmin):
    list_display = ('branch', 'filter_type', 'start_date', 'end_date')
    list_filter = ('filter_type', 'start_date')


# ✅ CommentAnalysis Admin
@admin.register(CommentAnalysis)
class CommentAnalysisAdmin(admin.ModelAdmin):
    list_display = ('branch', 'filter_type', 'start_date', 'end_date')
    list_filter = ('filter_type',)


# ✅ PlaceReviewAnalysis Admin
@admin.register(PlaceReviewAnalysis)
class PlaceReviewAnalysisAdmin(admin.ModelAdmin):
    list_display = ('branch', 'filter_type', 'start_date', 'end_date')
    list_filter = ('filter_type',)


# ✅ AccountActionRequest Admin
@admin.register(AccountActionRequest)
class AccountActionRequestAdmin(admin.ModelAdmin):
    list_display = ['user_email_snapshot', 'action', 'status', 'created_at', 'reviewed_by']
    readonly_fields = ['created_at', 'user_email_snapshot']
    list_filter = ('action', 'status', 'created_at')

    def save_model(self, request, obj, form, change):
        user = obj.user
        is_newly_reviewed = obj.status != 'pending' and obj.reviewed_at is None

        if is_newly_reviewed:
            obj.reviewed_by = request.user
            obj.reviewed_at = now()

        super().save_model(request, obj, form, change)

        if is_newly_reviewed:
            if obj.status == 'approved':
                if obj.action == 'delete':
                    delete_user_completely(user)
                elif obj.action == 'suspend':
                    user.is_suspended = True
                    user.save()


# ✅ CustomerConfirm Admin
@admin.register(CustomerConfirm)
class CustomerConfirmAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_confirmed', 'confirmed_at', 'created_at']
    list_filter = ['is_confirmed']

    def save_model(self, request, obj, form, change):
        is_newly_confirmed = False

        if obj.pk:
            prev_obj = CustomerConfirm.objects.get(pk=obj.pk)
            if not prev_obj.is_confirmed and obj.is_confirmed:
                is_newly_confirmed = True

        super().save_model(request, obj, form, change)

        if is_newly_confirmed:
            obj.confirm()  # 📨 BURADA həm user aktivləşir, həm email göndərilir


# ✅ Panel görünüşləri
admin.site.index_title = 'FeedSync'
admin.site.site_header = 'FeedSync AdminPanel'
admin.site.site_title = 'Feedsync Admin'

from django.contrib import admin
from .models import UserCommentDisplayConfig#, InstagramPost, InstagramComment, InstagramTarget


@admin.register(UserCommentDisplayConfig)
class UserCommentDisplayConfigAdmin(admin.ModelAdmin):
    list_display = ("user", "limit", "is_unlimited")
    list_filter = ("is_unlimited",)
    search_fields = ("user__email",)


# class InstagramCommentInline(admin.TabularInline):
#     """Post admin səhifəsində şərhləri inline göstərmək üçün"""
#     model = InstagramComment
#     extra = 0
#     fields = ("user", "text", "created_at", "like_count")
#     readonly_fields = ("created_at",)
#     ordering = ("-created_at",)


# @admin.register(InstagramPost)
# class InstagramPostAdmin(admin.ModelAdmin):
#     list_display = (
#         "id",
#         "user",
#         "profile_username",
#         "post_url",
#         "total_likes",
#         "total_comments",
#         "created_at",
#     )
#     list_filter = ("profile_username", "created_at")
#     search_fields = ("profile_username", "caption", "post_id", "user__email")
#     ordering = ("-created_at",)

#     readonly_fields = ("id", "created_at", "post_id")

#     fieldsets = (
#         ("📌 Əsas məlumatlar", {
#             "fields": ("user", "profile_username", "post_id", "post_url", "taken_at", "caption")
#         }),
#         ("📊 Statistika", {
#             "fields": ("total_likes", "total_comments")
#         }),
#         ("⚙️ Texniki", {
#             "fields": ("id", "created_at"),
#         }),
#     )

#     inlines = [InstagramCommentInline]


# @admin.register(InstagramComment)
# class InstagramCommentAdmin(admin.ModelAdmin):
#     list_display = ("user", "text", "post", "created_at", "like_count")
#     list_filter = ("created_at", "post__profile_username")
#     search_fields = ("user", "text", "post__profile_username")
#     ordering = ("-created_at",)

# from .models import InstagramPost, InstagramComment, InstagramTarget


# @admin.register(InstagramTarget)
# class InstagramTargetAdmin(admin.ModelAdmin):
#     list_display = ("username", "user", "active", "created_at")
#     list_filter = ("active", "created_at")
#     search_fields = ("username", "user__email")
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at",)


# accounts/admin.py
# accounts/admin.py
# from django.contrib import admin
# from .models import BonusModule

# @admin.register(BonusModule)
# class BonusModuleAdmin(admin.ModelAdmin):
#     list_display = ("user", "is_enabled", "is_active", "created_at")
#     list_editable = ("is_enabled",)
#     search_fields = ("user__email",)










from django.contrib import admin
from .models import UserProfileDetail, Company

admin.site.register(UserProfileDetail)
admin.site.register(Company)
admin.site.register(Story)
admin.site.register(WeeklySchedule)




from django.contrib import admin
from .models import BonusModule, LoyaltySettings, BonusLog, CustomerBonus

@admin.register(BonusModule)
class BonusModuleAdmin(admin.ModelAdmin):
    list_display = ("user", "is_enabled", "is_active", "created_at")
    list_filter = ("is_enabled", "is_active")
    search_fields = ("user__email",)
    ordering = ("-created_at",)


@admin.register(LoyaltySettings)
class LoyaltySettingsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "loyalty_enabled",
        "bonus_per_review",
        "bonus_to_currency_rate",
        "daily_spend_limit_enabled",
        "daily_spend_limit_amount",
        "updated_at",
    )
    list_filter = ("loyalty_enabled", "daily_spend_limit_enabled")
    search_fields = ("user__email",)
    ordering = ("-updated_at",)





@admin.register(BonusLog)
class BonusLogAdmin(admin.ModelAdmin):
    list_display = ("customer", "bonus_type", "bonus_date", "created_at")
    list_filter = ("bonus_type", "bonus_date")
    search_fields = ("customer__first_name", "customer__last_name", "customer__email", "customer__phone_number")
    ordering = ("-created_at",)


@admin.register(CustomerBonus)
class CustomerBonusAdmin(admin.ModelAdmin):
    list_display = ("customer", "owner", "bonus_balance")
    list_filter = ("owner",)
    search_fields = ("customer__first_name", "customer__last_name", "customer__email", "owner__email")
    ordering = ("-bonus_balance",)