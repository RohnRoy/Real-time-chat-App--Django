import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.user = self.scope["user"]
        try:
            self.other_user_id = int(self.scope["url_route"]["kwargs"]["user_id"])
        except (TypeError, ValueError):
            await self.close()
            return

        if self.other_user_id == self.user.id:
            await self.close()
            return

        if not await User.objects.filter(id=self.other_user_id).aexists():
            await self.close()
            return

        self.room = f"chat_{min(self.user.id, self.other_user_id)}_{max(self.user.id, self.other_user_id)}"

        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()

        await User.objects.filter(id=self.user.id).aupdate(
            is_online=True,
            last_seen=None,
        )

        await self.channel_layer.group_send(
            "users",
            {
                "type": "users_update",
                "data": {
                    "action": "presence",
                    "user_id": self.user.id,
                    "is_online": True,
                    "last_seen": None,
                },
            },
        )

        await self._mark_messages_read()
        await self.channel_layer.group_send(
            self.room,
            {
                "type": "read_receipt",
                "reader_id": self.user.id,
                "message_id": None,
            },
        )

        unread_count = await self._unread_count(
            sender_id=self.other_user_id,
            receiver_id=self.user.id,
        )
        await self.channel_layer.group_send(
            "users",
            {
                "type": "users_update",
                "data": {
                    "action": "unread_update",
                    "sender": self.other_user_id,
                    "receiver": self.user.id,
                    "unread_count": unread_count,
                },
            },
        )

    async def disconnect(self, code):
        if hasattr(self, "room"):
            await self.channel_layer.group_discard(self.room, self.channel_name)

        if not hasattr(self, "user"):
            return

        now = timezone.now()
        await User.objects.filter(id=self.user.id).aupdate(
            is_online=False,
            last_seen=now,
        )

        await self.channel_layer.group_send(
            "users",
            {
                "type": "users_update",
                "data": {
                    "action": "presence",
                    "user_id": self.user.id,
                    "is_online": False,
                    "last_seen": now.isoformat(),
                },
            },
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        event_type = data.get("type", "message")

        if event_type == "read":
            message_id = data.get("message_id")

            updated = await self._mark_messages_read(message_id)

            if updated:
                await self.channel_layer.group_send(
                    self.room,
                    {
                        "type": "read_receipt",
                        "reader_id": self.user.id,
                        "message_id": message_id,
                    },
                )

            unread_count = await self._unread_count(
                sender_id=self.other_user_id,
                receiver_id=self.user.id,
            )
            await self.channel_layer.group_send(
                "users",
                {
                    "type": "users_update",
                    "data": {
                        "action": "unread_update",
                        "sender": self.other_user_id,
                        "receiver": self.user.id,
                        "unread_count": unread_count,
                    },
                },
            )
            return

        if event_type == "delete":
            message_id = data.get("message_id")
            deleted = await self._delete_message(message_id)
            if not deleted:
                return

            await self.channel_layer.group_send(
                self.room,
                {
                    "type": "message_deleted",
                    "event": "message_deleted",
                    "message_id": int(message_id),
                    "deleted_by_id": self.user.id,
                },
            )

            unread_count = await self._unread_count(
                sender_id=self.user.id,
                receiver_id=self.other_user_id,
            )
            await self.channel_layer.group_send(
                "users",
                {
                    "type": "users_update",
                    "data": {
                        "action": "unread_update",
                        "sender": self.user.id,
                        "receiver": self.other_user_id,
                        "unread_count": unread_count,
                    },
                },
            )
            return

        message = data.get("message", "").strip()

        if not message:
            return

        receiver = await User.objects.aget(id=self.other_user_id)

        msg = await Message.objects.acreate(
            sender=self.user,
            receiver=receiver,
            content=message,
        )

        await self.channel_layer.group_send(
            self.room,
            {
                "type": "chat_message",
                "event": "chat_message",
                "message": message,
                "sender_id": self.user.id,
                "receiver_id": receiver.id,
                "message_id": msg.id,
                "is_read": msg.is_read,
                "timestamp": msg.timestamp.isoformat(),
            },
        )

        await self.channel_layer.group_send(
            "users",
            {
                "type": "users_update",
                "data": {
                    "action": "new_message",
                    "sender": self.user.id,
                    "receiver": receiver.id,
                    "unread_count": await self._unread_count(
                        sender_id=self.user.id,
                        receiver_id=receiver.id,
                    ),
                },
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def read_receipt(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "read_receipt",
                    "reader_id": event["reader_id"],
                    "message_id": event["message_id"],
                }
            )
        )

    async def message_deleted(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "message_deleted",
                    "message_id": event["message_id"],
                    "deleted_by_id": event["deleted_by_id"],
                }
            )
        )

    async def _mark_messages_read(self, message_id=None):
        queryset = Message.objects.filter(
            sender_id=self.other_user_id,
            receiver_id=self.user.id,
            is_read=False,
            is_deleted=False,
        )

        if message_id:
            queryset = queryset.filter(id=message_id)

        return await queryset.aupdate(is_read=True)

    async def _unread_count(self, sender_id, receiver_id):
        return await Message.objects.filter(
            sender_id=sender_id,
            receiver_id=receiver_id,
            is_read=False,
            is_deleted=False,
        ).acount()

    async def _delete_message(self, message_id):
        try:
            message_id = int(message_id)
        except (TypeError, ValueError):
            return False

        deleted = await Message.objects.filter(
            id=message_id,
            sender_id=self.user.id,
            receiver_id=self.other_user_id,
            is_deleted=False,
        ).aupdate(
            is_deleted=True,
            deleted_at=timezone.now(),
            deleted_by_id=self.user.id,
        )
        return bool(deleted)


class PresenceConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.user = self.scope["user"]

        await self.channel_layer.group_add("users", self.channel_name)
        await self.accept()

        await User.objects.filter(id=self.user.id).aupdate(is_online=True, last_seen=None)
        await self.channel_layer.group_send(
            "users",
            {
                "type": "users_update",
                "data": {
                    "action": "presence",
                    "user_id": self.user.id,
                    "is_online": True,
                    "last_seen": None,
                },
            },
        )

    async def disconnect(self, code):
        await self.channel_layer.group_discard("users", self.channel_name)
        if not hasattr(self, "user"):
            return

        now = timezone.now()
        await User.objects.filter(id=self.user.id).aupdate(is_online=False, last_seen=now)
        await self.channel_layer.group_send(
            "users",
            {
                "type": "users_update",
                "data": {
                    "action": "presence",
                    "user_id": self.user.id,
                    "is_online": False,
                    "last_seen": now.isoformat(),
                },
            },
        )

    async def users_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
