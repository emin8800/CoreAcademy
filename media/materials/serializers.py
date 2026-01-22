from requests import Response
from django.contrib.auth.forms import PasswordResetForm
from rest_framework import serializers

from .models import (
    CustomUser,
    Note,
    PlaceMap,
    PlaceReview,
    PlaceURL,
    UserForm,
    Comment,
    QRCode,
)

# --------------------------------------------------------
# User Serializer
# --------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'telephone']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            telephone=validated_data.get('telephone'),
            is_verified=False,
            is_active=False,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


# --------------------------------------------------------
# Password Reset Serializer
# --------------------------------------------------------

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not PasswordResetForm({'email': value}).is_valid():
            raise serializers.ValidationError("Bu e-posta qeydiyyatda deyil.")
        return value


# --------------------------------------------------------
# Sentiment Request Serializer
# --------------------------------------------------------

class SentimentRequestSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=1000)


# --------------------------------------------------------
# Place Serializers
# --------------------------------------------------------

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceMap
        fields = ['user', 'namap_name', 'created_at']


class PlaceMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceMap
        fields = ["id", "branch_name", "uid"]


class PlaceURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceURL
        fields = ['id', 'user', 'place_map', 'url', 'place_name', 'created_at', 'uid']


class AddPlaceURLSerializer(serializers.Serializer):
    branch_name = serializers.CharField(max_length=255)
    google_map_url = serializers.URLField(required=False)


# --------------------------------------------------------
# QR Code Serializer
# --------------------------------------------------------

class QRCodeSerializer(serializers.ModelSerializer):
    place_maps = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='branch_name'
    )

    class Meta:
        model = QRCode
        fields = ["id", "uid", "qr_image", "qr_url", "place_maps","logo"]
        read_only_fields = ['qr_image']


# --------------------------------------------------------
# Comment Serializers
# --------------------------------------------------------

class CommentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    gender = serializers.CharField(source="user.gender", read_only=True)
    age_range = serializers.CharField(source="user.age_range", read_only=True)

    class Meta:
        model = Comment
        fields = ["first_name", "last_name", "gender", "age_range", "sentiment", "comment", "created_at"]


class FullCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


# --------------------------------------------------------
# Review Serializers
# --------------------------------------------------------

class PlaceReviewSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = PlaceReview
        fields = ["author_name", "text", "stars", "sentiment", "branch_name", "created_at"]


class FullPlaceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceReview
        fields = "__all__"


# --------------------------------------------------------
# Sentiment Analysis Serializers
# --------------------------------------------------------

class SentimentCountSerializer(serializers.Serializer):
    Yaxşı = serializers.IntegerField(default=0)
    Mənfi = serializers.IntegerField(default=0)
    Neytral = serializers.IntegerField(default=0)


class GenderSentimentCountSerializer(serializers.Serializer):
    Kişi = serializers.DictField(child=serializers.IntegerField())
    Qadın = serializers.DictField(child=serializers.IntegerField())
    Digər = serializers.DictField(child=serializers.IntegerField())


class SentimentAnalysisResponseSerializer(serializers.Serializer):
    year = serializers.DictField(child=GenderSentimentCountSerializer())
    month = serializers.DictField(child=GenderSentimentCountSerializer())
    week = serializers.DictField(child=GenderSentimentCountSerializer())


# --------------------------------------------------------
# User Form Serializer
# --------------------------------------------------------
# serializers.py
# serializers.
#19u yusif
from rest_framework import serializers
from .models import UserForm, CustomerBonus, LoyaltySettings


class UserFormSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    last_comment_date = serializers.SerializerMethodField()
    gender_display = serializers.SerializerMethodField()
    gender_choices_localized = serializers.SerializerMethodField()

    # ✅ Loyalty info
    bonus_balance = serializers.SerializerMethodField()
    total_spent_bonus = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()

    bonus_balance_azn = serializers.SerializerMethodField()
    total_spent_azn = serializers.SerializerMethodField()

    uid = serializers.UUIDField(read_only=True)

    class Meta:
        model = UserForm
        fields = [
            "id",
            "uid",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "full_name",
            "birth_date",
            "age_range",
            "gender",
            "gender_display",
            "gender_choices_localized",
            "contact",
            "last_comment_date",

            # ✅ bonus fields
            "bonus_balance",
            "total_spent_bonus",
            "rank",
            "bonus_balance_azn",
            "total_spent_azn",
        ]

    # =========================================================
    # ✅ Helper: həmin biznes üçün CustomerBonus tap
    # =========================================================
    def _get_customer_bonus(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        return CustomerBonus.objects.filter(
            customer=obj,
            owner=request.user
        ).select_related("rank").first()

    # =========================================================
    # ✅ Helper: həmin biznes üçün LoyaltySettings tap
    # =========================================================
    def _get_loyalty_settings(self):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        return LoyaltySettings.objects.filter(user=request.user).first()

    # =========================================================
    # ✅ BONUS
    # =========================================================
    def get_bonus_balance(self, obj):
        bonus = self._get_customer_bonus(obj)
        return bonus.bonus_balance if bonus else 0

    def get_total_spent_bonus(self, obj):
        bonus = self._get_customer_bonus(obj)
        return bonus.total_spent_bonus if bonus else 0

    def get_rank(self, obj):
        bonus = self._get_customer_bonus(obj)
        return bonus.rank.code if (bonus and bonus.rank) else "bronze"

    # =========================================================
    # ✅ AZN hesablamalar (bonus_to_currency_rate görə)
    # =========================================================
    def get_bonus_balance_azn(self, obj):
        bonus = self._get_customer_bonus(obj)
        settings = self._get_loyalty_settings()

        if not bonus or not settings or not settings.bonus_to_currency_rate:
            return 0

        rate = float(settings.bonus_to_currency_rate)
        return round(bonus.bonus_balance / rate, 2)

    def get_total_spent_azn(self, obj):
        bonus = self._get_customer_bonus(obj)
        settings = self._get_loyalty_settings()

        if not bonus or not settings or not settings.bonus_to_currency_rate:
            return 0

        rate = float(settings.bonus_to_currency_rate)
        return round(bonus.total_spent_bonus / rate, 2)

    # =========================================================
    # digər hissələr səndəki kimi qalır
    # =========================================================
    def get_full_name(self, obj):
        name = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        if name:
            return name
        if obj.phone_number:
            return obj.phone_number
        if obj.email:
            return obj.email
        return "Naməlum"

    def get_contact(self, obj):
        if obj.phone_number and obj.email:
            return f"{obj.phone_number} | {obj.email}"
        elif obj.phone_number:
            return obj.phone_number
        elif obj.email:
            return obj.email
        return "—"

    def get_last_comment_date(self, obj):
        last_comment = obj.comments.order_by('-created_at').first()
        if last_comment and last_comment.created_at:
            return last_comment.created_at.strftime("%d.%m.%Y")
        return None

    def get_gender_display(self, obj):
        lang = self.context.get('request').GET.get('lang', 'az')
        return self._gender_map().get(obj.gender, {}).get(lang, obj.get_gender_display())

    def get_gender_choices_localized(self, obj):
        lang = self.context.get('request').GET.get('lang', 'az')
        return {
            "male": self._gender_map()["male"][lang],
            "female": self._gender_map()["female"][lang],
            "other": self._gender_map()["other"][lang],
        }

    def _gender_map(self):
        return {
            'male': {'az': 'Kişi', 'en': 'Male', 'ru': 'Мужчина'},
            'female': {'az': 'Qadın', 'en': 'Female', 'ru': 'Женщина'},
            'other': {'az': 'Digər', 'en': 'Other', 'ru': 'Другое'},
        }


# --------------------------------------------------------
# Note Serializer
# --------------------------------------------------------

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'date']


# --------------------------------------------------------
# User Profile Serializer
# --------------------------------------------------------

class UserProfileSerializer(serializers.ModelSerializer):
    wepsite = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_wepsite(self, value):
        if value:
            value = value.strip()
            if not value.startswith("http://") and not value.startswith("https://"):
                value = "https://" + value
        return value

    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'telephone',
            'location',
            'wepsite',
            'piography',
            'profile_picture',
            'username',
            'is_2fa_enabled',
        ]



#############################Mail api ucun #############################
from rest_framework import serializers

class ContactFormSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    message = serializers.CharField()


from rest_framework import serializers

class ContactWithFileSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    message = serializers.CharField()
    file = serializers.FileField(required=False)  # 👈 əlavə şəkil (istəyə bağlı)
    text_file = serializers.FileField(required=False)  # 👈 əlavə text fayl (istəyə bağlı)
#########################################################################
from rest_framework import serializers
from .models import UserForm


class NullableDateField(serializers.DateField):
    """Boş string və ya None gələndə None qaytaran DateField"""
    def to_internal_value(self, value):
        if value in ("", None):
            return None
        return super().to_internal_value(value)


class UserFormMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True, required=False)
    contact = serializers.CharField(write_only=True, required=False)
    birth_date = NullableDateField(
        required=False,
        allow_null=True,
        input_formats=["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]
    )

    class Meta:
        model = UserForm
        fields = [
            "uid",
            "first_name",
            "last_name",
            "birth_date",
            "age_range",
            "gender",
            "email",
            "phone_number",
            "full_name",   # input üçün
            "contact",     # input üçün
        ]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "email": {"required": False},
            "phone_number": {"required": False},
            "birth_date": {"required": False},
        }

    def to_representation(self, instance):
        """GET zamanı cavab formatı"""
        rep = super().to_representation(instance)
        rep["full_name"] = f"{instance.first_name or ''} {instance.last_name or ''}".strip() or None
        rep["contact"] = instance.phone_number or instance.email or None
        return rep

    def create(self, validated_data):
        full_name = validated_data.pop("full_name", None)
        contact = validated_data.pop("contact", None)

        if full_name:
            parts = full_name.strip().split(" ", 1)
            validated_data["first_name"] = parts[0]
            validated_data["last_name"] = parts[1] if len(parts) > 1 else ""

        if contact:
            if "@" in contact:
                validated_data["email"] = contact
            else:
                validated_data["phone_number"] = contact

        # ✅ customer_of-u avtomatik əlavə et
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["customer_of"] = request.user

        return super().create(validated_data)


    def update(self, instance, validated_data):
        """Mövcud obyekt update edilərkən"""
        full_name = validated_data.pop("full_name", None)
        contact = validated_data.pop("contact", None)

        if full_name:
            parts = full_name.strip().split(" ", 1)
            validated_data["first_name"] = parts[0]
            validated_data["last_name"] = parts[1] if len(parts) > 1 else ""

        if contact:
            if "@" in contact:
                validated_data["email"] = contact
                validated_data["phone_number"] = None
            else:
                validated_data["phone_number"] = contact
                validated_data["email"] = None

        return super().update(instance, validated_data)




################################################################################################
from rest_framework import serializers
from .models import BonusModule

class BonusModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusModule
        fields = ['id', 'is_active', 'created_at', 'updated_at']

################################################################################################
# --------------------------------------------------------
# Campaign Serializer
# --------------------------------------------------------
# serializers.py
from rest_framework import serializers
from .models import UserProfileDetail, Company
from .models import CustomUser  

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'image', 'user']
        read_only_fields = ['id', 'user']



class UserProfileDetailSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(source='user.profile_picture', required=False, allow_null=True)

    class Meta:
        model = UserProfileDetail
        fields = [
            'instagram', 'facebook', 'tiktok', 'whatsapp', 'telegram',
            'background_image', 'phone_number',
            'show_receipt_number',#yeni əlavə yusif
            'notify_nearby_customers', 'show_business_reviews',
            'category', 'profile_picture'
        ]

    def to_internal_value(self, data):
        data = data.copy()
        for key in data:
            if data[key] == "null":
                data[key] = None
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        # ✅ profil şəklini yadda saxla
        if 'profile_picture' in user_data:
            user.profile_picture = user_data['profile_picture']
            user.save()

        return super().update(instance, validated_data)



class FullProfileSerializer(serializers.ModelSerializer):
    profile_detail = UserProfileDetailSerializer()
    companies = CompanySerializer(many=True)

    class Meta:
        model = CustomUser
        fields = ['uid', 'email', 'username', 'profile_detail', 'companies']

######################################################################################

#Story Serializer
# stories/serializers.py
from rest_framework import serializers
from .models import Story
from moviepy.editor import VideoFileClip
from django.core.files.base import ContentFile
import os
import tempfile
import uuid

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['id', 'file', 'is_video', 'created_at']
        read_only_fields = ['id', 'is_video', 'created_at']

    def validate_file(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif']:
            return value
        elif ext in ['.mp4', '.mov', '.avi']:
            return value
        raise serializers.ValidationError("Yalnız şəkil və video yükləyə bilərsiniz.")

    def create(self, validated_data):
        file = validated_data['file']
        ext = os.path.splitext(file.name)[1].lower()
        is_video = ext in ['.mp4', '.mov', '.avi']

        if is_video:
            # TEMP: original video'u oxu və kəs
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_input:
                for chunk in file.chunks():
                    temp_input.write(chunk)
                temp_input_path = temp_input.name

            clip = VideoFileClip(temp_input_path)
            duration = clip.duration
            max_duration = 60  # saniyə

            if duration > max_duration:
                clip = clip.subclip(0, max_duration)

            temp_output_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.mp4")
            clip.write_videofile(temp_output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)

            with open(temp_output_path, 'rb') as f:
                new_file = ContentFile(f.read(), name=f"trimmed_{file.name}")

            validated_data['file'] = new_file

            # Təmizlik
            os.remove(temp_input_path)
            os.remove(temp_output_path)

        validated_data['is_video'] = is_video
        return super().create(validated_data)


########################################################################################################
#acilis kapma saatlari serializer
from rest_framework import serializers
from .models import WeeklySchedule

class WeeklyScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklySchedule
        exclude = ['id', 'user', 'created_at', 'updated_at']





###################################################################################################
#bonus module serializer

from rest_framework import serializers
from .models import LoyaltySettings
from decimal import Decimal

class LoyaltySettingsSerializer(serializers.ModelSerializer):
    # Spec-ə uyğun nested field-lər
    daily_spend_limit = serializers.SerializerMethodField()
    rank_bonus = serializers.SerializerMethodField()
    birthday_campaign = serializers.SerializerMethodField()
    holiday_campaign = serializers.SerializerMethodField()
    custom_campaign = serializers.SerializerMethodField()
    weekend_campaign = serializers.SerializerMethodField()

    class Meta:
        model = LoyaltySettings
        fields = [
            "loyalty_enabled",
            "bonus_per_review",
            "bonus_to_currency_rate",

            "daily_spend_limit",
            "rank_bonus",

            "birthday_campaign",
            "holiday_campaign",
            "custom_campaign",
            "weekend_campaign",
        ]

    # ✅ GET formatı (model -> spec JSON)
    def get_daily_spend_limit(self, obj):
        return {
            "enabled": obj.daily_spend_limit_enabled,
            "amount": obj.daily_spend_limit_amount
        }

    def get_rank_bonus(self, obj):
        return {
            "silver": {
                "enabled": obj.silver_enabled,
                "type": obj.silver_type,
                "value": obj.silver_value
            },
            "gold": {
                "enabled": obj.gold_enabled,
                "type": obj.gold_type,
                "value": obj.gold_value
            },
            "vip": {
                "enabled": obj.vip_enabled,
                "type": obj.vip_type,
                "value": obj.vip_value
            }
        }

    def get_birthday_campaign(self, obj):
        return {
            "enabled": obj.birthday_enabled,
            "bonus": obj.birthday_bonus
        }

    def get_holiday_campaign(self, obj):
        return {
            "enabled": obj.holiday_enabled,
            "bonus": obj.holiday_bonus,
        }

    def get_custom_campaign(self, obj):
        return {
            "enabled": obj.custom_enabled,
            "date_from": obj.custom_date_from,
            "date_to": obj.custom_date_to,
            "type": obj.custom_type,
            "value": obj.custom_value
        }

    def get_weekend_campaign(self, obj):
        return {
            "enabled": obj.weekend_enabled,
            "type": obj.weekend_type,
            "value": obj.weekend_value
        }

    # ✅ update/create üçün payload JSON -> model write
    def update(self, instance, validated_data):
        request_data = self.context["request"].data

        rate = request_data.get("bonus_to_currency_rate")
        if rate is not None and Decimal(str(rate)) <= 0:
            raise serializers.ValidationError({
                "bonus_to_currency_rate": "0 və ya mənfi ola bilməz"
            }) #19u yusif
        
        # 1) simple fields
        instance.loyalty_enabled = request_data.get("loyalty_enabled", instance.loyalty_enabled)
        instance.bonus_per_review = request_data.get("bonus_per_review", instance.bonus_per_review)
        instance.bonus_to_currency_rate = request_data.get("bonus_to_currency_rate", instance.bonus_to_currency_rate)

        # 2) daily spend limit
        daily = request_data.get("daily_spend_limit", {})
        instance.daily_spend_limit_enabled = daily.get("enabled", instance.daily_spend_limit_enabled)
        instance.daily_spend_limit_amount = daily.get("amount", instance.daily_spend_limit_amount)

        # 3) rank bonus
        rank = request_data.get("rank_bonus", {})

        silver = rank.get("silver", {})
        instance.silver_enabled = silver.get("enabled", instance.silver_enabled)
        instance.silver_type = silver.get("type", instance.silver_type)
        instance.silver_value = silver.get("value", instance.silver_value)

        gold = rank.get("gold", {})
        instance.gold_enabled = gold.get("enabled", instance.gold_enabled)
        instance.gold_type = gold.get("type", instance.gold_type)
        instance.gold_value = gold.get("value", instance.gold_value)

        vip = rank.get("vip", {})
        instance.vip_enabled = vip.get("enabled", instance.vip_enabled)
        instance.vip_type = vip.get("type", instance.vip_type)
        instance.vip_value = vip.get("value", instance.vip_value)

        # 4) campaigns
        birthday = request_data.get("birthday_campaign", {})
        instance.birthday_enabled = birthday.get("enabled", instance.birthday_enabled)
        instance.birthday_bonus = birthday.get("bonus", instance.birthday_bonus)

        holiday = request_data.get("holiday_campaign", {})
        instance.holiday_enabled = holiday.get("enabled", instance.holiday_enabled)
        instance.holiday_bonus = holiday.get("bonus", instance.holiday_bonus)
      

        custom = request_data.get("custom_campaign", {})
        instance.custom_enabled = custom.get("enabled", instance.custom_enabled)
        instance.custom_date_from = custom.get("date_from", instance.custom_date_from)
        instance.custom_date_to = custom.get("date_to", instance.custom_date_to)
        instance.custom_type = custom.get("type", instance.custom_type)
        instance.custom_value = custom.get("value", instance.custom_value)

        weekend = request_data.get("weekend_campaign", {})
        instance.weekend_enabled = weekend.get("enabled", instance.weekend_enabled)
        instance.weekend_type = weekend.get("type", instance.weekend_type)
        instance.weekend_value = weekend.get("value", instance.weekend_value)

        # ✅ Spec validasiya qaydaları: true olub dəyər yoxdursa -> false et
        self.apply_auto_fixes(instance)

        instance.save()
        return instance

    def apply_auto_fixes(self, instance):
        # daily spend limit
        if instance.daily_spend_limit_enabled and instance.daily_spend_limit_amount is None:
            instance.daily_spend_limit_enabled = False

        # silver
        if instance.silver_enabled:
            if instance.silver_type not in ["fixed", "percent"] or instance.silver_value is None:
                instance.silver_enabled = False
                instance.silver_type = None
                instance.silver_value = None

        # gold
        if instance.gold_enabled:
            if instance.gold_type not in ["fixed", "percent"] or instance.gold_value is None:
                instance.gold_enabled = False
                instance.gold_type = None
                instance.gold_value = None

        # vip
        if instance.vip_enabled:
            if instance.vip_type not in ["fixed", "percent"] or instance.vip_value is None:
                instance.vip_enabled = False
                instance.vip_type = None
                instance.vip_value = None

        # birthday
        if instance.birthday_enabled and instance.birthday_bonus is None:
            instance.birthday_enabled = False

        # holiday
        if instance.holiday_enabled and instance.holiday_bonus is None:
            instance.holiday_enabled = False

        # custom
        if instance.custom_enabled:
            if (instance.custom_date_from is None or instance.custom_date_to is None or
                instance.custom_type not in ["fixed", "percent"] or instance.custom_value is None):
                instance.custom_enabled = False
                instance.custom_date_from = None
                instance.custom_date_to = None
                instance.custom_type = None
                instance.custom_value = None

        # weekend
        if instance.weekend_enabled:
            if instance.weekend_type not in ["fixed", "percent"] or instance.weekend_value is None:
                instance.weekend_enabled = False
                instance.weekend_type = None
                instance.weekend_value = None


############################################################################################
































