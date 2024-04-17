from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Folder, File, Permission
from .serializers import FolderSerializer, FileSerializer, PermissionSerializer
from .minio_client import minio_client


class FolderCreateView(generics.CreateAPIView):
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class FolderRenameView(generics.UpdateAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(id=self.kwargs['folder_id'], owner=self.request.user)
        return obj


class FileUploadView(generics.CreateAPIView):
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        folder_id = self.kwargs.get('folder_id')
        folder = Folder.objects.filter(id=folder_id, owner=self.request.user).first()
        if not folder:
            raise serializers.ValidationError("Folder not found.")

        file_obj = self.request.FILES.get('file')
        object_name = f"{folder.name}/{file_obj.name}"
        path = minio_client.upload_file(file_obj, object_name)
        serializer.save(filename=file_obj.name, url=path, owner=self.request.user, folder=folder)


class FileShareView(generics.UpdateAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        file_id = self.kwargs.get('file_id')
        target_user_id = self.request.data.get('target_user_id')
        can_read = self.request.data.get('can_read')
        can_change = self.request.data.get('can_change')
        permission = Permission.objects.filter(file_id=file_id, user_id=target_user_id).first()
        if not permission:
            permission = Permission(file_id=file_id, user_id=target_user_id, can_read=can_read, can_change=can_change)
        else:
            permission.can_read = can_read
            permission.can_change = can_change
        permission.save()


class FileDeleteView(generics.DestroyAPIView):
    queryset = File.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        user_permission = Permission.objects.filter(file=instance, user=self.request.user).first()
        if not user_permission or not user_permission.can_change:
            raise PermissionDenied("You do not have permission to delete this file.")

        minio_client.remove_object(BUCKET_NAME, instance.path.split("/")[-1])
        instance.delete()


class FileSearchView(generics.ListAPIView):
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('query')
        folder_id = self.request.query_params.get('folder_id')
        return File.objects.filter(folder_id=folder_id, owner=self.request.user, filename__icontains=query)