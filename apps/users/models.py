from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.utils.abstracts import AbstractUUID

# from apps.utils.country.countries import country_codes
from apps.utils.enums import (
    AuthTokenEnum,
    AuthTokenStatusEnum,
    StaffType,
    GenderType,
    MaritalType,
    UserType,
)


class User(AbstractUser, AbstractUUID):
    """
    USER MODELS
    """

    type = models.PositiveSmallIntegerField(default=0, choices=UserType.choices())
    mobile = models.CharField(unique=True, max_length=20)
    email = models.EmailField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    town = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(default="", null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True, choices=GenderType.choices())
    marital_status = models.CharField(
        max_length=255, null=True, blank=True, choices=MaritalType.choices()
    )

    newsletter = models.BooleanField(default=True)
    is_confirmed = models.BooleanField(default=False, blank=True)
    first_login = models.BooleanField(default=True, null=True, blank=True)
    secret_key = models.CharField(max_length=255, null=True, blank=True)
    public_key = models.CharField(max_length=255, null=True, blank=True)
    referral_code = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        db_table = "user"
        ordering = ("-date_joined",)

    def __str__(self):
        return f"{self.mobile} {self.get_full_name()} {self.id} {self.group()}"

    def group(self):
        if self.groups.all().count():
            return self.groups.all().first().name
        else:
            return "customer"


class AuthToken(AbstractUUID):
    """
    AUTH TOKEN
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="user_token_value"
    )
    type = models.PositiveSmallIntegerField(
        choices=AuthTokenEnum.choices(), default=AuthTokenEnum.NUMBER_VERIFICATION
    )
    token = models.CharField(max_length=255, null=True, blank=True, editable=False)
    status = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        choices=AuthTokenStatusEnum.choices(),
        default=AuthTokenStatusEnum.PENDING,
        editable=False,
    )
    expiry = models.DateTimeField(null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return "{0} {1}".format(str(self.user), str(self.created_at))

    class Meta:
        ordering = ("-created_at",)
        db_table = "auth_token"
        verbose_name = "Token"


class StaffSettings(AbstractUUID):
    """this model handles farmer settings and profile information"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="farmer")
    category = models.CharField(max_length=200, null=True, blank=True, choices=StaffType.choices())
    staff_name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True, choices=StaffType.choices())
    state = models.CharField(max_length=255, null=True, blank=True)
    local_govt = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(default="")
    disability = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="farmer_images", null=True, blank=True)
    # bank information
    bank_code = models.CharField(max_length=255, null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=255, null=True, blank=True)
    account_name = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return "{0} {1}".format(str(self.user), str(self.created_at))

    class Meta:
        ordering = ("-created_at",)
        db_table = "staff_settings"
        verbose_name = "StaffSetting"
        verbose_name_plural = "StaffSettings"


class DeliveryAddress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="delivery_address", null=True, blank=True
    )
    location_name = models.CharField(max_length=255)
    address = models.TextField(default="", blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    is_default_address = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.location_name}"

    class Meta:
        verbose_name_plural = "User Delivery Address"


class Wallet(AbstractUUID):
    """
    this model serves as a virtual wallet for user in which they can use to perform automation on our system
    """

    identifier = models.CharField(unique=True, max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="virtual_bank")
    amount = models.FloatField(default=0.0)
    ledge_balance = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.user.username, self.amount)

    class Meta:
        db_table = "wallet"
        ordering = ["-created_at"]
        verbose_name_plural = "Wallet"
