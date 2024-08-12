from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import ChatmessageCreateForm
from Chatter.utils import login_required

@login_required
def chat_view(request, chat_room_name='public-chat'):
    chat_group = get_object_or_404(ChatGroup, group_name=chat_room_name)
    chat_messages = chat_group.chat_messages.all()[:25]
    form = ChatmessageCreateForm()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break
    if request.method == "POST":
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context = {
                'message': message,
                'user': request.user
            }
            return render(request, 'partial/chat_message_partial.html', context)

    context = {
        'chat_messages': chat_messages,
        'form': form,
        'other_user': other_user,
        'chat_room_name': chat_room_name

    }

    return render(request, "chat/chat.html", context)


def do_private_chatroom(request, username):
    if request.user.username == username:
        return redirect('home')

    other_user = User.objects.get(username=username)
    print("the other user",other_user)
    self_chatrooms = request.user.chat_groups.filter(is_private=True)
    print(self_chatrooms)

    if self_chatrooms.exists():
        for chatroom in self_chatrooms:
            if other_user in chatroom.members.all():
                return redirect('chatroom', chatroom.group_name)

    chatroom = ChatGroup.objects.create(is_private=True)
    chatroom.members.add(other_user, request.user)
    print(chatroom.group_name)

    return redirect('chatroom', chatroom.group_name)


def chat_file_upload(request, chat_room_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chat_room_name)

    if request.method == "POST":
        file = request.FILES['file']
        message = GroupMessage.objects.create(
            file=file,
            author=request.user,
            group=chat_group,
        )

        channel_layer = get_channel_layer()
        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }

        async_to_sync(channel_layer.group_send)(
            chat_room_name, event
        )

        return HttpResponse()
