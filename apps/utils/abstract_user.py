from django.db import models


class StaffAbstract(models.Model):
    staff = models.ForeignKey(
        "users.User", related_name="%(class)s", on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        abstract = True
