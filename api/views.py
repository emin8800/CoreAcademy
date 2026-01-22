from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import *
from .serializers import *

from rest_framework import viewsets, status
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            print("❌ CREATE VALIDATION ERROR:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        print("📥 UPDATE request.data:", request.data)

        serializer = self.get_serializer(
            instance=self.get_object(),
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():
            print("❌ UPDATE VALIDATION ERROR:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets
from .models import Expense
from .serializers import ExpenseSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    parser_classes = (MultiPartParser, FormParser)


from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def create(self, request, *args, **kwargs):
        print("✅ CREATE MATERIAL CALLED")
        print("📌 request.data:", request.data)
        print("📌 request.FILES:", request.FILES)

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            print("❌ SERIALIZER ERRORS:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        print("✅ SAVED MATERIAL:", serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets
from .models import Content
from .serializers import ContentSerializer

class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    parser_classes = (MultiPartParser, FormParser)


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

class StudentWorkViewSet(viewsets.ModelViewSet):
    queryset = StudentWork.objects.all()
    serializer_class = StudentWorkSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by("-date")
    serializer_class = EventSerializer

from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import Material

class MaterialDownloadViewSet(viewsets.ViewSet):

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        material = get_object_or_404(Material, pk=pk)
        return FileResponse(
            material.file.open("rb"),
            as_attachment=True,
            filename=material.file.name.split("/")[-1]
        )



from rest_framework import viewsets
from .models import ContactMessage
from .serializers import ContactMessageSerializer

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all().order_by("-id")
    serializer_class = ContactMessageSerializer
