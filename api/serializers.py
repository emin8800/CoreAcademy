from rest_framework import serializers
from .models import User, Course, Expense, Material, Content, Request, StudentWork
from rest_framework import serializers
from .models import User, Event


class UserSerializer(serializers.ModelSerializer):
    # ✅ BU ƏN VACİB SƏTİR: password heç vaxt update-də məcburi olmasın
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'phone', 'role', 'fin', 'salary', 'group', 'payment',
            'age', 'gender', 'dob', 'password'
        ]

        # ✅ extra_kwargs içində mütləq required=False ver
        extra_kwargs = {
            "password": {"write_only": True, "required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        print("📥 CREATE validated_data:", validated_data)

        password = validated_data.pop("password", None)

        # username yoxdursa email-dən düzəlt
        if not validated_data.get("username") and validated_data.get("email"):
            validated_data["username"] = validated_data["email"]

        user = User(**validated_data)

        # parol göndərilməyibsə default
        if password:
            user.set_password(password)
        else:
            user.set_password("123456")

        user.save()
        return user

    def update(self, instance, validated_data):
        print("📥 UPDATE validated_data:", validated_data)

        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password and password.strip() != "":
            instance.set_password(password)

        instance.save()
        return instance



class CourseSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "title", "desc", "age_group", "image_file", "image_url", "image"]

    def get_image(self, obj):
        return obj.image


class ExpenseSerializer(serializers.ModelSerializer):
    added_by_name = serializers.CharField(source='added_by.get_full_name', read_only=True)
    class Meta:
        model = Expense
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'


class StudentWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentWork
        fields = '__all__'






# ✅ EVENTS SERIALIZER
class EventSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ["id", "title", "desc", "date", "location", "type", "image_file", "image_url", "image"]

    def get_image(self, obj):
        return obj.image




from rest_framework import serializers
from .models import ContactMessage

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = "__all__"
