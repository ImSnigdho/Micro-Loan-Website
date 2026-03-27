from django.db import models
from django.contrib.auth.models import User


class SiteSettings(models.Model):
    """Singleton model — only one row should exist. Edit via Admin panel."""
    site_name = models.CharField(max_length=100, default='MPS Loan')
    logo_url = models.URLField(blank=True, help_text='External logo URL (optional)')
    logo_image = models.ImageField(upload_to='logo/', blank=True, null=True)

    # YouTube tutorial link shown in the info popup
    youtube_url = models.URLField(
        default='https://www.youtube.com/',
        help_text='YouTube video link for the intro popup'
    )

    # Payment/withdrawal numbers
    bkash_number = models.CharField(max_length=20, default='01XXXXXXXXX')
    nagad_number = models.CharField(max_length=20, default='01XXXXXXXXX')
    rocket_number = models.CharField(max_length=20, default='01XXXXXXXXX')

    # Loan interest range display
    interest_rate_min = models.DecimalField(max_digits=5, decimal_places=2, default=3.00)
    interest_rate_max = models.DecimalField(max_digits=5, decimal_places=2, default=6.00)

    # Banner / promotional text
    banner_tagline = models.CharField(max_length=200, default='লোন অফার যেন মিস না হয়!')
    banner_sub = models.CharField(max_length=200, default='চেক করুন mpsloen.com এ')

    # Security deposit percentage
    security_deposit_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00,
        help_text='Security deposit as % of loan amount'
    )

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Enforce singleton: only one settings row
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


OCCUPATION_CHOICES = [
    ('student', 'ছাত্র/ছাত্রী'),
    ('business', 'ব্যবসা'),
    ('service', 'চাকরিজীবী'),
    ('freelancer', 'ফ্রিল্যান্সার'),
    ('other', 'অন্যান্য'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, unique=True)
    occupation = models.CharField(max_length=30, choices=OCCUPATION_CHOICES, default='other')
    profile_picture = models.ImageField(upload_to='avatars/', default='default_avatar.png', blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} — {self.phone}'


LOAN_AMOUNT_CHOICES = [
    (5000, '৳৫,০০০ টাকা'),
    (10000, '৳১০,০০০ টাকা'),
    (15000, '৳১৫,০০০ টাকা'),
    (20000, '৳২০,০০০ টাকা'),
    (25000, '৳২৫,০০০ টাকা'),
    (30000, '৳৩০,০০০ টাকা'),
    (50000, '৳৫০,০০০ টাকা'),
]

DURATION_CHOICES = [
    (3, '৩ মাস'),
    (6, '৬ মাস'),
    (12, '১২ মাস'),
]

LOAN_PURPOSE_CHOICES = [
    ('business', 'ব্যবসা'),
    ('education', 'শিক্ষা'),
    ('medical', 'চিকিৎসা'),
    ('personal', 'ব্যক্তিগত'),
    ('other', 'অন্যান্য'),
]

LOAN_STATUS_CHOICES = [
    ('pending', 'অপেক্ষমাণ'),
    ('approved', 'অনুমোদিত'),
    ('rejected', 'প্রত্যাখ্যাত'),
    ('disbursed', 'বিতরণ করা হয়েছে'),
    ('closed', 'বন্ধ'),
]


class LoanApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    applicant_name = models.CharField(max_length=100)
    amount = models.IntegerField(choices=LOAN_AMOUNT_CHOICES, default=5000)
    duration_months = models.IntegerField(choices=DURATION_CHOICES, default=3)
    purpose = models.CharField(max_length=30, choices=LOAN_PURPOSE_CHOICES, default='business')
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=3.00)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # NID uploads
    nid_front = models.ImageField(upload_to='nid/', blank=True, null=True)
    nid_back = models.ImageField(upload_to='nid/', blank=True, null=True)

    status = models.CharField(max_length=20, choices=LOAN_STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    admin_note = models.TextField(blank=True)

    class Meta:
        ordering = ['-applied_at']
        verbose_name = 'Loan Application'

    def __str__(self):
        return f'{self.user.username} — ৳{self.amount} ({self.get_status_display()})'

    @property
    def total_interest(self):
        return round(self.amount * self.interest_rate / 100 * self.duration_months, 2)

    @property
    def total_payable(self):
        return round(self.amount + self.total_interest, 2)

    @property
    def monthly_payment(self):
        return round(self.total_payable / self.duration_months, 2)


PAYMENT_METHOD_CHOICES = [
    ('bkash', 'বিকাশ'),
    ('nagad', 'নগদ'),
    ('rocket', 'রকেট'),
]

TRANSACTION_TYPE_CHOICES = [
    ('deposit', 'জমা'),
    ('withdrawal', 'উত্তোলন'),
    ('loan_disbursement', 'লোন বিতরণ'),
    ('loan_repayment', 'লোন পরিশোধ'),
]


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    note = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.get_transaction_type_display()} ৳{self.amount}'


class InboxMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.user.username}] {self.title}'
