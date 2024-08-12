from django.urls import path
from . import views


urlpatterns = [
    path('public_chat/',views.chat_view,name="public_chat"),
    path('chat/room/<str:chat_room_name>',views.chat_view,name="chatroom"),
    path('pr_chat/<str:username>',views.do_private_chatroom,name="pr_chat"),
    path('chat/fileupload/<chat_room_name>',views.chat_file_upload, name="chat_file_upload"),
]