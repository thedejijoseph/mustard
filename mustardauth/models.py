from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    KYC_LEVELS = [
        ('verified_email', _('Verified Email')),
        ('verified_bvn', _('Verified BVN')),
        ('verified_nin', _('Verified NIN')),
    ]

    TIERS = [
        ('tier_1', _('Tier 1')),
        ('tier_2', _('Tier 2')),
        ('tier_3', _('Tier 3')),
    ]

    email = models.EmailField(unique=True)
    kyc_level = models.CharField(
        max_length=20,
        choices=KYC_LEVELS,
        default='verified_email',
        help_text=_('The KYC level the user has completed'),
    )
    tier = models.CharField(
        max_length=20,
        choices=TIERS,
        default='tier_1',
        help_text=_('The current transaction tier of the user'),
    )

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        verbose_name=_("groups"),
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
        verbose_name=_("user permissions"),
        blank=True,
    )

    def update_tier(self):
        """
        Automatically update the tier based on the current KYC level.
        """
        kyc_to_tier_map = {
            'verified_email': 'tier_1',
            'verified_bvn': 'tier_2',
            'verified_nin': 'tier_3',
        }
        self.tier = kyc_to_tier_map.get(self.kyc_level, 'tier_1')
        self.save()

    @property
    def transaction_limits(self):
        """
        Returns the transaction limits for the current tier.
        """
        limits = {
            'tier_1': {
                'credit_limit': 50_000,
                'debit_limit': 20_000,
                'max_balance': 100_000,
            },
            'tier_2': {
                'credit_limit': 200_000,
                'debit_limit': 200_000,
                'max_balance': 1_000_000,
            },
            'tier_3': {
                'credit_limit': 1_000_000,
                'debit_limit': 2_000_000,
                'max_balance': None,  # Unlimited
            },
        }
        return limits.get(self.tier, limits['tier_1'])
