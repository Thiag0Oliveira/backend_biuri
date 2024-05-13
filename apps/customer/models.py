from django.contrib.auth.models import User
from django.db import models

from allauth.socialaccount.models import SocialAccount

from apps.common.models import BestPraticesModel
from apps.core.models import Address
from apps.iugu.customer import Customer as IuguCustomer


GENDER_LIST = (
    ('Masculino', 'Masculino'),
    ('Feminino', 'Feminino'),
)

class Customer(BestPraticesModel):
    """
    Model for Customers
    """
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    address = models.ForeignKey(Address, null=True, blank=True)
    iugu_client_id = models.CharField(max_length=200, blank=True, null=True)
    avatar_image = models.ImageField(upload_to='customer/avatar/', null=True, blank=True)
    avatar_image_facebook = models.URLField(null=True, blank=True)
    celphone = models.CharField(max_length=11, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_LIST, null=True, blank=True)

    class Meta:
        verbose_name = "Customer"

    def __str__(self):
        return '{}'.format(self.id)

    def save(self, *args, **kwargs):
        self.iugu_client_id = self.customer_iugu()
        social_account = SocialAccount.objects.filter(user=self.user, provider='facebook')
        if social_account.exists():
            social_account = social_account[0]
            self.avatar_image_facebook = social_account.get_avatar_url()
        super(Customer, self).save(*args, **kwargs)

    def create_new_iugu_customer(self, email, name):
        data = {'email': email, 'name': name}
        iugu = IuguCustomer().create(data)
        iugu = iugu['id']
        return iugu

    def customer_iugu(self):
        email = self.user.email
        if self.user.first_name is None or self.user.first_name == '':
            name = self.user.username
        else:
            name = self.user.first_name
        if email is None or email == '':
            email = str(self.user.id) + '@email.com.br'
        if self.iugu_client_id is None:
            iugu = self.create_new_iugu_customer(email, name)
        else:
            data = {'email': email, 'name': name}
            try:
                iugu = IuguCustomer().change(self.iugu_client_id, data)['id']
            except KeyError:
                iugu = self.create_new_iugu_customer(email, name)
        return iugu


    @property
    def get_avatar(self):
        social_account = SocialAccount.objects.filter(user=self.user, provider='facebook')
        if self.avatar_image:
            photo_url = 'http://www.biuri.com.br/' + self.avatar_image.url
            return photo_url
        else:
            if self.avatar_image_facebook:
                return self.avatar_image_facebook
            else:
                return 'http://www.biuri.com.br/media/professional/avatar/default.png'


class PricingCriterionCustomer(BestPraticesModel):
    """
    Stores the Pricing Criterion Options(:model:`service_core.PricingCriterionOptions`) for a single Customer(:model:`customer.customer`)
    """
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    pricing_criterion = models.ForeignKey('service_core.PricingCriterion', on_delete=models.DO_NOTHING)
    pricing_criterion_option = models.ForeignKey('service_core.PricingCriterionOptions', on_delete=models.DO_NOTHING)
