from django.db.models import PositiveSmallIntegerField
from django.utils.functional import classproperty
from django.utils.translation import gettext as _


class CustomEnum(object):
    class Enum(object):
        name = None
        value = None
        type = None

        def __init__(self, name, value, type):
            self.key = name
            self.name = name
            self.value = value
            self.type = type

        def __str__(self):
            return self.name

        def __repr__(self):
            return self.name

        def __eq__(self, other):
            if other is None:
                return False
            if isinstance(other, CustomEnum.Enum):
                return self.value == other.value
            raise TypeError

    @classmethod
    def choices(c):
        attrs = [a for a in c.__dict__.keys() if a.isupper()]
        values = [(c.__dict__[v], CustomEnum.Enum(v, c.__dict__[v], c).__str__()) for v in attrs]
        return sorted(values, key=lambda x: x[0])

    @classmethod
    def default(cls):
        """
        Returns default value, which is the first one by default.
        Override this method if you need another default value.
        """
        return cls.choices()[0][0]

    @classmethod
    def field(cls, **kwargs):
        """
        A shortcut for
        Usage:
            class MyModelStatuses(CustomEnum):
                UNKNOWN = 0
            class MyModel(Model):
                status = MyModelStatuses.field(label='my status')
        """
        field = PositiveSmallIntegerField(choices=cls.choices(), default=cls.default(), **kwargs)
        field.enum = cls
        return field

    @classmethod
    def get(c, value):
        if type(value) is int:
            try:
                return [
                    CustomEnum.Enum(k, v, c)
                    for k, v in c.__dict__.items()
                    if k.isupper() and v == value
                ][0]
            except Exception:
                return None
        else:
            try:
                key = value.upper()
                return CustomEnum.Enum(key, c.__dict__[key], c)
            except Exception:
                return None

    @classmethod
    def key(c, key):
        try:
            return [value for name, value in c.__dict__.items() if name == key.upper()][0]
        except Exception:
            return None

    @classmethod
    def name(c, key):
        try:
            return [name for name, value in c.__dict__.items() if value == key][0]
        except Exception:
            return None

    @classmethod
    def get_counter(c):
        counter = {}
        for key, value in c.__dict__.items():
            if key.isupper():
                counter[value] = 0
        return counter

    @classmethod
    def items(c):
        attrs = [a for a in c.__dict__.keys() if a.isupper()]
        values = [(v, c.__dict__[v]) for v in attrs]
        return sorted(values, key=lambda x: x[1])

    @classmethod
    def to_list(c):
        attrs = [a.lower() for a in c.__dict__.keys() if a.isupper()]
        return attrs

    @classmethod
    def is_valid_transition(c, from_status, to_status):
        return from_status == to_status or from_status in c.transition_origins(to_status)

    @classmethod
    def transition_origins(c, to_status):
        return to_status

    @classmethod
    def get_name(c, key):
        choices_name = dict(c.choices())
        return choices_name.get(key)


class UnProcessTransactionStatus(CustomEnum):
    TRANSFER: int = 0
    DEPOSIT: int = 1

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.TRANSFER, "TRANSFER"),
            (cls.DEPOSIT, "DEPOSIT"),
        )


class UserType(CustomEnum):
    CUSTOMER: int = 0
    STAFF: int = 1
    DEALER: int = 2
    AGENT: int = 3
    INVESTOR: int = 4

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.CUSTOMER, "CUSTOMER"),
            (cls.STAFF, "STAFF"),
            (cls.DEALER, "DEALER"),
            (cls.AGENT, "AGENT"),
            (cls.INVESTOR, "INVESTOR"),
        )


class UserGroup(CustomEnum):
    BUYER: str = "buyer"
    STAFF: str = "staff"
    DEALER: str = "dealer"
    AGENT = "facilitator"
    INVESTOR = "investor"

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.BUYER, "BUYER"),
            (cls.STAFF, "STAFF"),
            (cls.DEALER, "DEALER"),
            (cls.AGENT, "AGENT"),
            (cls.INVESTOR, "INVESTOR"),
        )


class AuthTokenEnum(CustomEnum):
    RESET_TOKEN: int = 0
    LOGIN_TOKEN: int = 1
    NUMBER_VERIFICATION: int = 2
    AUTHORIZATION_TOKEN: int = 3

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.RESET_TOKEN, "TRANSFER"),
            (cls.LOGIN_TOKEN, "LOGIN TOKEN"),
            (cls.NUMBER_VERIFICATION, "NUMBER VERIFICATION"),
            (cls.AUTHORIZATION_TOKEN, "AUTHORIZATION TOKEN"),
        )


class StaffType(CustomEnum):
    WAITER: str = "waiter"
    BAR_TENDER: str = "bar tender"
    MANAGER: str = "manager"

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.WAITER, "WAITER"),
            (cls.BAR_TENDER, "BAR_TENDER"),
            (cls.MANAGER, "MANAGER"),
        )


class AuthTokenStatusEnum(CustomEnum):
    PENDING: int = 0
    USED: int = 1

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.PENDING, "PENDING"),
            (cls.USED, "USED"),
        )


class DisabilityType(CustomEnum):
    DISABLE: int = "disable"
    NOT_DISABLE: int = "not_"

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.DISABLE, "DISABLE"),
            (cls.NOT_DISABLE, "NOT DISABLE"),
        )


class MaritalType(CustomEnum):
    MARRIED: str = "MARRIED"
    SINGLE: str = "SINGLE"
    DIVORSED: str = "DIVORSED"

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.MARRIED, "MARRIED"),
            (cls.SINGLE, "SINGLE"),
            (cls.DIVORSED, "DIVORSED"),
        )


class GenderType(CustomEnum):
    MALE: str = "male"
    FEMALE: str = "female"

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.MALE, "Male"),
            (cls.FEMALE, "Female"),
        )


class SMSEnum(CustomEnum):
    SENDCHAMP = "https://api.sendchamp.com/api/v1/sms/send"


class PaymentChannelEnum(CustomEnum):
    PAYSTACK: str = "paystack"
    FLUTTERWAVE: str = "flutterwave"

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.PAYSTACK, "PAYSTACK"),
            (cls.FLUTTERWAVE, "FLUTTERWAVE"),
        )


class DeliveryType(CustomEnum):
    PICKUP: str = "pickup"
    DELIVER: str = "deliver"

    @classmethod
    def choices(cls) -> tuple:
        return ((cls.PICKUP, "Pickup"), (cls.DELIVER, "Delivery"))


class EstimatedDeliveryDurationType(CustomEnum):
    HOUR: str = "hour"
    DAY: str = "day"
    WEEK: str = "week"
    MONTH: str = "month"
    YEAR: str = "year"

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.HOUR, "Hour"),
            (cls.DAY, "DAY"),
            (cls.WEEK, "WEEK"),
            (cls.MONTH, "MONTH"),
            (cls.YEAR, "YEAR"),
        )


class TransactionStatusEnum(CustomEnum):
    PAID: str = "paid"
    PENDING: str = "pending"
    CANCELLED: str = "cancelled"
    EXPIRED: str = "expired"


class FulfilmentStatusEnum(CustomEnum):
    DELIVERED: str = "delivered"
    NOT_DELIVERED: str = "not_delivered"
    PENDING: str = "pending"
    CANCELLED: str = "cancelled"


class PaymentMethodEnum(CustomEnum):
    PAYSTACK: str = "paystack"
    INTERSWITCH: str = "interswitch"


class ConfigurationTypeEnum(CustomEnum):
    PRODUCT_CHARGE_RATE: str = "product_charge_rate"
    FULFILMENT_CHARGE_RATE: str = "fulfilment_charge_rate"

    @classmethod
    def choices(c) -> tuple:
        return (
            (c.PRODUCT_CHARGE_RATE, "PRODUCT CHARGE RATE"),
            (c.FULFILMENT_CHARGE_RATE, "FULFILMENT CHARGE RATE"),
        )


class GlobalUrlConfigEnum(CustomEnum):
    API_URL = ""
    LOGIN_URL = ""


class UnitTypeEnum(CustomEnum):
    PIECE: str = "piece"
    BOX: str = "box"
    KG: str = "kg"
    LITRE: str = "liter"
    PACKAGE: str = "package"

    @classmethod
    def choices(c) -> tuple:
        return (
            (c.PIECE, "Piece"),
            (c.BOX, "Box"),
            (c.KG, "Kilogram"),
            (c.LITRE, "Litre"),
            (c.PACKAGE, "Package"),
        )
