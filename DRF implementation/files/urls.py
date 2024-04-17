from django.urls import path
from .views import FolderCreateView, FolderRenameView, FileUploadView, FileShareView, FileDeleteView, FileSearchView

urlpatterns = [
    path('folders/', FolderCreateView.as_view(), name='create-folder'),
    path('folders/<int:folder_id>/rename/', FolderRenameView.as_view(), name='rename-folder'),
    path('upload/<int:folder_id>/', FileUploadView.as_view(), name='upload-file-to-folder'),
    path('share/<int:file_id>/', FileShareView.as_view(), name='share-file'),
    path('delete/<int:file_id>/', FileDeleteView.as_view(), name='delete-file'),
    path('search/', FileSearchView.as_view(), name='search-files'),
]