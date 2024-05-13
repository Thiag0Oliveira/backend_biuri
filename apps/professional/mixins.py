from apps.professional.models import Seller, Executive


class TypeUserMixin(object):

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None

    def user_seller(self):
        seller = Seller.objects.filter(user=self.request.user)
        if seller.exists():
            return seller[0]
        return None
