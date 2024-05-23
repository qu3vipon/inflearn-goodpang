from datetime import datetime

from django.db import models


class ServiceUser(models.Model):
    email = models.EmailField()
    order_count = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)
    version = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = "user"
        db_table = "service_user"
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_email"),
        ]

    def create_order_code(self) -> str:
        return datetime.utcnow().strftime("%Y%m%d-%H%M%S") + f"-{self.id}"


class UserPointsHistory(models.Model):
    user = models.ForeignKey(
        ServiceUser, on_delete=models.CASCADE, related_name="points_history"
    )
    points_change = models.IntegerField(default=0)
    reason = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "user"
        db_table = "user_points_history"


class UserPoints(models.Model):
    user = models.ForeignKey(ServiceUser, on_delete=models.CASCADE)
    version = models.PositiveIntegerField(default=0)
    points_change = models.IntegerField(default=0)
    points_sum = models.PositiveIntegerField(default=0)
    reason = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "user"
        db_table = "user_points"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "version"], name="unique_user_version"
            ),
        ]
