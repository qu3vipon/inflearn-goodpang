from django.db import models


class ServiceUser(models.Model):
    email = models.EmailField()

    class Meta:
        app_label = "user"
        db_table = "service_user"
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_email"),
        ]
