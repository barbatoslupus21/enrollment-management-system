from django.db import models
from homepage.models import System_users

class Notification(models.Model):
    module = models.CharField(max_length=50, null=True)
    sender = models.ForeignKey(System_users, on_delete=models.CASCADE, null=True, related_name="notif_sender")
    reciever = models.ForeignKey(System_users, on_delete=models.CASCADE, null=True, related_name="notif_receiver")
    message = models.TextField()
    send_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender.name} - {self.module} - {self.reciever.name}'
