from django.shortcuts import render
from django.views import View, generic
from django.db import transaction
from django.urls import reverse_lazy
import functools
from .forms import CreditCardForm
from .models import CreditCard

from .forms import CreditCardForm, VoucherForm
from .models import CreditCard, Voucher
from apps.common.views import PermissionListView
from apps.professional.models import Executive
# from apps.professional.filters import GenericFilter
from apps.common.views import GenericFilterList


class VoucherList(generic.ListView):
    """
    Lists the Vouchers(:model:`payment.voucher`)
    """
    model = Voucher
    template_name = 'payment/voucher_list.html'
    # filterset_class = GenericFilter
    verbose_name = 'Cupom'
    verbose_name_plural = 'Cupons'
    add_display_name = 'Criar Cupom'
    queryset = Voucher.objects.all()
    ordering = '-id'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        executive = self.user_executive()
        if executive is not None:
            return queryset
        else:
            return queryset.none()

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None

    def get_context_data(self, **kwargs):
        context = super(VoucherList, self).get_context_data(**kwargs)
        return context


class VoucherCreate(generic.CreateView):
    """
    View for Voucher(:model:`payment.voucher`) Creation
    """
    model = Voucher
    template_name = 'payment/voucher_form.html'
    form_class = VoucherForm
    permission_form_fields = [{'field': 'commission', 'permission': 'professional.can_edit_seller'},
                              {'field': 'seller', 'permission': 'professional.can_edit_seller'}]

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None

    def permission_form(self, form, user):
        # for permission_form_field in self.permission_form_fields:
        #     if not user.has_perm(permission_form_field['permission']):
        #         del form.fields[permission_form_field['field']]
        return form

    def get_success_url(self):
        url = '/payment/voucher/' + str(self.object.pk) + '/edit'
        return url

    def get_context_data(self, **kwargs):
        context = super(VoucherCreate, self).get_context_data(**kwargs)
        context['form'] = self.permission_form(form=context['form'], user=self.request.user)
        executive = self.user_executive()
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        form = self.permission_form(form=form, user=self.request.user)

        if form.is_valid():
            self.object = form.save(commit=False)
            if self.object.discount_type == 'percent':
                self.object.discount = self.object.discount_value
                self.object.discount_value = 0
            else:
                self.object.discount = 0
            executive = self.user_executive()
            if executive is not None:
                self.object.executive = executive
            self.object = form.save()
            return super(VoucherCreate, self).form_valid(form)
        return render(request, self.template_name, {'form': form})


class VoucherUpdate(generic.UpdateView):
    """
    View for Voucher(:model:`payment.voucher`) Update
    """
    model = Voucher
    template_name = 'payment/voucher_form.html'
    form_class = VoucherForm
    success_url = reverse_lazy('payment:voucher-list')
    permission_form_fields = [{'field': 'seller', 'permission': 'company_sale.edit_sale_seller'},
                              {'field': 'company', 'permission': 'company_sale.edit_sale_company'},
                              {'field': 'executive', 'permission': 'company_sale.edit_sale_executive'},
                              {'field': 'commission', 'permission': 'company_sale.edit_sale_seller'}]
    queryset = Voucher.objects.all()
    # sale_voucher_generator_form = modelformset_factory(SaleVoucherGenerator, form=SaleVoucherGeneratorForm,
    #                                                    extra=1, can_delete=True)

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        executive = self.user_executive()
        if executive is not None:
            return queryset.filter(executive=executive)
        else:
            return queryset.none()

    def permission_form(self, form, user):
        # for permission_form_field in self.permission_form_fields:
        #     if not user.has_perm(permission_form_field['permission']):
        #         del form.fields[permission_form_field['field']]
        return form

    def get_context_data(self, **kwargs):
        context = super(VoucherUpdate, self).get_context_data(**kwargs)
        context['form'] = self.permission_form(form=context['form'], user=self.request.user)
        executive = self.user_executive()
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        form = self.permission_form(form=form, user=self.request.user)

        if form.is_valid():
            self.object.type = 'marketplace'
            if self.object.discount_type == 'percent' and self.object.discount_value != 0:
                self.object.discount = self.object.discount_value
                self.object.discount_value = 0
            if self.object.discount_type == 'value':
                self.object.discount = 0
            self.object = form.save()
            return super(VoucherUpdate, self).form_valid(form)
        return render(request, self.template_name, {'form': form})


def split_payment(price, splits_number=1, interest=float(2.5), taxa_avista=float(2.5), taxa_aprazo=float(3.5)):
    new_price = price - (price*taxa_avista/100)
    new_price = new_price - (new_price * interest/100)
    total_interest, split_value = price, price
    parcelations = list(range(1,splits_number+1))
    if splits_number != 1:
        if splits_number > 6:
            taxa_aprazo = float(3.55)
        split_value = (new_price*100) / (splits_number*100-(float(functools.reduce(lambda x,y:x+y,parcelations))*interest))
        total_interest = split_value*splits_number
        total_interest = total_interest / (1-(taxa_aprazo/100))
    # return total_interest - price, new_price, total_interest, round(total_interest/splits_number,2)
    return round(total_interest/splits_number,2)

def split_text_generate(parcelation,parcela):
    split_text = "{} x de R$ {}".format(parcelation, parcela)
    if parcelation > 1:
        split_text += " com juros"
    else:
        split_text += " sem juros"
    return split_text.replace('.',',')

def calculate_splits(price, minimal_split_price):
    total_parcelas = int(price/minimal_split_price)
    if total_parcelas > 12:
        total_parcelas = 12
    parcelations = list(range(1,total_parcelas+1))
    options = []
    for parcelation in parcelations:
        parcela = split_payment(price=price,splits_number=parcelation)

        options.append({'split_number': parcelation, 'split_price': parcela,
                        'split_text': split_text_generate(parcelation=parcelation, parcela=parcela)})
    return options

