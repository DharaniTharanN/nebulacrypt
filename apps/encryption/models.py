from django.db import models

class EncryptionTransfer(models.Model):
    """
    Model to store PDF transfer records, replacing MongoDB usage.
    """
    sender_email = models.EmailField()
    receiver_email = models.EmailField()
    original_filename = models.CharField(max_length=255)
    encrypted_filename = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.sender_email} -> {self.receiver_email} ({self.timestamp})"
