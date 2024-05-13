from datetime import timedelta, datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from model_mommy import mommy
from model_mommy.recipe import foreign_key
from oauth2_provider.models import Application, AccessToken
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase, RequestsClient

from apps.common.models import Address, UserAddress
from apps.professional.models import Professional, ServiceProfessional
from apps.service_core.models import Category, Service, Attendance, PricingCriterionOptions
from apps.customer.models import Customer
from apps.payment.models import CreditCard


# Create your tests here.

# class ExecutivesLeadTest(APITestCase):
#     get_url = reverse('api:api_executiveslead')
#     client = RequestsClient()
#     def test_get_all(self):
#         response = self.client.get(self.get_url)
#         assert response.status_code == 200
#
#     def test_get_with_filter(self):
#         response = self.client.get(self.get_url+'?search=teste')
#         assert response.status_code == 200
#
#     def test_get_with_order(self):
#         response = self.client.get(self.get_url+'?ordering=-id')
#         assert response.status_code == 200
#
#     def test_get_with_fields(self):
#         response = self.client.get(self.get_url+'?fields=id,name')
#         assert response.status_code == 200

class Autentication(object):

    def create_token(self, user):

        app = Application.objects.create(
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='https://www.none.com/oauth2/callback',
            name='dummy',
            user=user
        )
        access_token = AccessToken.objects.create(
            user=user,
            scope='read write',
            expires=datetime.now() + timedelta(seconds=300),
            token='secret-access-token-key' + str(user.email),
            application=app
        )
        return access_token

    def create_authorization_header(self, token):
        return "Bearer {0}".format(token)



class ProfileApiTest(Autentication, APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mommy.make(User, email='teste@email.com', password='password', first_name='Teste')
        cls.customer = mommy.make(Customer, user=cls.user)
        cls.address = mommy.make(Address, _fill_optional=True)
        cls.user_professional = mommy.make(User, email='teste_professional@email.com', password='password', first_name='Teste')
        cls.professional = mommy.make(Professional, user=cls.user_professional,  address=cls.address)

    def setUp(self):
        self.token_customer = self.create_authorization_header(self.create_token(self.user))
        self.token_professional = self.create_authorization_header(self.create_token(self.user_professional))

    def test_profile_customer(self):
        url = reverse('api:api_profile')
        response = self.client.get(url, HTTP_AUTHORIZATION=self.token_customer)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_profile_professional(self):
        url = reverse('api:api_profile')
        response = self.client.get(url, HTTP_AUTHORIZATION=self.token_professional)
        self.assertEqual(response.status_code,status.HTTP_200_OK)


class LoginApiTest(Autentication, APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='teste@email.com', email='teste@email.com', password='password', first_name='Teste')
        cls.customer = mommy.make(Customer, user=cls.user)
        cls.auth_token =  mommy.make(Token, user=cls.user)
        user = User.objects.get(pk=cls.user.id)

    def setUp(self):
        self.token = self.create_authorization_header(self.create_token(self.user))

    def test_get_login(self):
        url = reverse('api:api_account_login')
        response = self.client.get(url, {'email': 'teste@email.com', 'password': 'password'})
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    # def test_login(self):
    #     url = reverse('api:api_account_login')
    #     response = self.client.post(url, {'email': 'teste@email.com', 'password': 'password'}, content_type="application/json")
    #     self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_token_push(self):
        url = reverse('api:api_token')
        response = self.client.post(url, {'registration_id': 'ljklajsdkljasdlkjaslkjas'}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_celphone_update(self):
        url = reverse('api:api_celphone')
        response = self.client.post(url,{'celphone': '81987666730'}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_convert_token(self):
        url = reverse('api:api_account_login_convert_token')
        response = self.client.post(url,{'key': self.auth_token.key}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

class CategoryApiTest(APITestCase):
    get_url = reverse('api:api_category')
    quantity_male = 10
    quantity_female = 10
    quantity_male_female = 10

    def setUp(self):
        self.category_recipe_male = mommy.make(Category,gender='Masculino', _quantity=self.quantity_male)
        self.category_recipe_female = mommy.make(Category,gender='Feminino', _quantity=self.quantity_male)
        self.category_recipe_male_female = mommy.make(Category,gender='Todos', _quantity=self.quantity_male_female)

    def test_get_all_categorys(self):
        response = self.client.get(self.get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']),
                         self.quantity_male + self.quantity_female + self.quantity_male_female)

    def test_get_male_categorys(self):
        get_url = self.get_url + '?gender=male'
        response = self.client.get(get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), self.quantity_male + self.quantity_male_female)

    def test_get_female_categorys(self):
        get_url = self.get_url + '?gender=female'
        response = self.client.get(get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), self.quantity_female + self.quantity_male_female)


class ServiceApiTest(APITestCase):
    get_url = reverse('api:api_service')
    quantity_male = 10
    quantity_female = 10
    quantity_male_female = 10

    def setUp(self):
        self.category_recipe_male = mommy.make(Service,gender='Masculino', _quantity=self.quantity_male)
        self.category_recipe_female = mommy.make(Service,gender='Feminino', _quantity=self.quantity_female)
        self.category_recipe__male_female = mommy.make(Service,gender='Todos', _quantity=self.quantity_male_female)

    def test_get_all_services(self):
        response = self.client.get(self.get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']),self.quantity_male+self.quantity_female+self.quantity_male_female)

    def test_get_male_services(self):
        get_url = self.get_url + '?gender=male'
        response = self.client.get(get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), self.quantity_male + self.quantity_male_female)

    def test_get_female_services(self):
        get_url = self.get_url + '?gender=female'
        response = self.client.get(get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), self.quantity_female + self.quantity_male_female)


class AttendanceAnonymusApiTest(APITestCase):
    get_url = reverse('api:api_attendance')
    # client = RequestsClient()
    # client_api = APIClient()

    def setUp(self):
        self.user = mommy.make(User, email='teste@email.com', password='password',first_name='Teste')
        self.customer = mommy.make(Customer, user=self.user)
        self.attendances = mommy.make(Attendance, customer=self.customer, _quantity=20)
        self.services = mommy.make(Service, gender='Masculino', _quantity=5)

    def test_get_all_attendances_not_logged(self):
        response = self.client.get(self.get_url, )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_create_attendance_by_initial_service_not_logged(self):
        get_url = self.get_url
        service = self.services[0].id
        response = self.client.post(get_url,{'service': service })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AttendanceCustomerListCreateApiTest(Autentication, APITestCase):
    get_url = reverse('api:api_attendance')

    def setUp(self):
        self.user = mommy.make(User, email='teste@email.com', password='password',first_name='Teste')
        self.customer = mommy.make(Customer, user=self.user)
        address = mommy.make(Address, _fill_optional=True)
        self.professional = mommy.make(Professional, address=address)
        self.attendances = mommy.make(Attendance, customer=self.customer,
                                      status='confirmated',
                                      professional= self.professional,
                                      _fill_optional = ['scheduling_date'],
                                      _quantity=20)
        self.token = self.create_authorization_header(self.create_token(self.user))
        self.services = mommy.make(Service, gender='Masculino', _quantity=5)
        self.service_professional = mommy.make(ServiceProfessional, professional=self.professional,
                                               minimum_price=10, maximum_price=15)

    def test_get_all_attendances_logged_historic(self):
        get_url = self.get_url + '?historic=true'
        attendances = Attendance.objects.filter(customer=self.customer)
        response = self.client.get(get_url, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_attendances_logged_not_historic(self):
        get_url = self.get_url + '?historic=false'
        attendances = Attendance.objects.filter(customer=self.customer)
        response = self.client.get(get_url, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_attendance_by_initial_service(self):
        get_url = self.get_url
        service = self.services[0].id
        response = self.client.post(get_url,{'service': service }, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer']['id'], self.customer.id)
        self.assertEqual(response.data['initial_service']['id'], service)

    def test_create_attendance_by_professional(self):
        get_url = self.get_url
        response = self.client.post(get_url,{'professional': self.professional.id,
                                             'services': [{'id': self.service_professional.id}]}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer']['id'], self.customer.id)
        self.assertEqual(response.data['initial_service']['id'], self.service_professional.service.id)


class AttendanceDraftCustomerUpdateApiTest(Autentication, APITestCase):
    get_url = reverse('api:api_attendance')

    def setUp(self):
        self.user = mommy.make(User, email='teste@email.com', password='password',first_name='Teste')
        self.customer = mommy.make(Customer, user=self.user)
        self.address = mommy.make(Address, _fill_optional=True)
        self.user_address = mommy.make(UserAddress, user=self.user, _fill_optional=True)
        self.professional = mommy.make(Professional, address=self.address)
        self.token = self.create_authorization_header(self.create_token(self.user))
        self.services = mommy.make(Service, gender='Masculino', _quantity=5)
        self.service_professional = mommy.make(ServiceProfessional, professional=self.professional, _quantity=5,
                                               minimum_price=10, maximum_price=15)
        self.service_professional = mommy.make(ServiceProfessional, service=self.services[0], professional=self.professional,
                                               minimum_price=10, maximum_price=15)
        self.other_professional = mommy.make(Professional, address=self.address, _quantity=10)

    def test_get_professional(self):
        self.attendance = mommy.make(Attendance, customer=self.customer,
                                     status='draft',
                                     initial_service=self.services[0],
                                     address = self.user_address)
        url = reverse('api:api_attendance_professional', kwargs={'pk':self.attendance.id})
        response = self.client.get(url, {}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_professional(self):
        self.attendance = mommy.make(Attendance, customer=self.customer,
                                     status='draft',
                                     initial_service=self.services[0],
                                     address = self.user_address)
        url = reverse('api:api_attendance_professional', kwargs={'pk':self.attendance.id})
        response = self.client.post(url, {'professional': self.professional.id}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id'], self.attendance.id)
        self.assertEqual(response.data['professional']['id'], self.professional.id)

    def test_remove_professional(self):
        self.attendance = mommy.make(Attendance, customer=self.customer,
                                     status='draft',
                                     professional=self.professional,
                                     initial_service=self.services[0],
                                     address = self.user_address)
        url = reverse('api:api_attendance_professional', kwargs={'pk':self.attendance.id})
        response = self.client.post(url, {'professional': 0}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id'], self.attendance.id)
        self.assertEqual(response.data['professional'], None)

    def test_update_status_draft_to_complete_draft_whitout_card(self):
        self.attendance = mommy.make(Attendance, customer=self.customer,
                                     status='draft',
                                     initial_service=self.services[0],
                                     address = self.user_address,
                                     )
        url = reverse('api:api_attendance_detail', kwargs={'pk':self.attendance.id})
        response = self.client.patch(url, {'status': 'complete_draft'}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'][0], 'Cartão de crédito não informado')

    def test_update_card_attendance(self):
        self.attendance = mommy.make(Attendance, customer=self.customer,
                                     status='draft',
                                     initial_service=self.services[0],
                                     address = self.user_address,
                                     )
        card = {
            'number': '4242424242424242',
            'verification_value': '123',
            'name': 'Teste Iugu',
            'month': '1',
            'year': '2030'
        }
        card_url = reverse('api:api_credit_card')
        response_card = self.client.post(card_url, card, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response_card.status_code, status.HTTP_201_CREATED)
        url = reverse('api:api_attendance_creditcard', kwargs={'pk':self.attendance.id})
        response = self.client.post(url, {'credit_card': response_card.data['id']}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['credit_card']['id'], response_card.data['id'])

    def test_update_address_attendance(self):
        self.attendance = mommy.make(Attendance, customer=self.customer,
                                     status='draft',
                                     initial_service=self.services[0],
                                     )
        user_address = mommy.make(UserAddress, user=self.user, _fill_optional=True)
        url = reverse('api:api_attendance_address', kwargs={'pk':self.attendance.id})
        response = self.client.post(url, {'address': user_address.id}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['address']['id'],  user_address.id)

    def test_update_status_draft_to_complete_draft(self):
        self.attendance = mommy.make(Attendance, customer=self.customer,
                                     status='draft',
                                     initial_service=self.services[0],
                                     address=self.user_address,
                                     )
        card = {
            'number': '4242424242424242',
            'verification_value': '123',
            'name': 'Teste Iugu',
            'month': '1',
            'year': '2030'
        }
        response_card = self.client.post(reverse('api:api_credit_card'), card, HTTP_AUTHORIZATION=self.token)
        response_attendance = self.client.post(reverse('api:api_attendance_creditcard', kwargs={'pk':self.attendance.id})
                                    , {'credit_card': response_card.data['id']}, HTTP_AUTHORIZATION=self.token)
        url = reverse('api:api_attendance_detail', kwargs={'pk':self.attendance.id})
        response = self.client.patch(url, {'status': 'complete_draft'}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'complete_draft')

    def test_update_observation_whitout_pricing_criterion(self):
        self.attendance = mommy.make(Attendance, customer=self.customer,
                                     status='draft',
                                     initial_service=self.services[0],
                                     address=self.user_address,
                                     )
        url = reverse('api:api_attendance_observation', kwargs={'pk':self.attendance.id})
        observation = 'Lorem Ipsion, Lorem Ipsun'
        response = self.client.post(url, {'observation': observation}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['observation'], observation)

    def test_get_pricing_criterion(self):
        self.pricing_criterion_option = mommy.make(PricingCriterionOptions)
        self.service = mommy.make(Service, pricing_criterion=self.pricing_criterion_option.pricing_criterion)
        self.attendance = mommy.make(Attendance, customer=self.customer,
                                     status='draft',
                                     initial_service=self.service,
                                     address=self.user_address,
                                     )
        url = reverse('api:api_attendance_observation', kwargs={'pk':self.attendance.id})
        response = self.client.get(url, {}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'],self.service.pricing_criterion.id)
        self.assertEqual(response.data['options'][0]['id'], self.pricing_criterion_option.id)

    def test_get_pricing_criterion_none(self):
        self.service = mommy.make(Service)
        self.attendance = mommy.make(Attendance, customer=self.customer,
                                     status='draft',
                                     initial_service=self.service,
                                     address=self.user_address,
                                     )
        url = reverse('api:api_attendance_observation', kwargs={'pk':self.attendance.id})
        response = self.client.get(url, {}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,{})

    def test_update_observation_using_pricing_criterion(self):
        self.pricing_criterion_option = mommy.make(PricingCriterionOptions)
        self.service = mommy.make(Service, pricing_criterion=self.pricing_criterion_option.pricing_criterion)
        self.attendance = mommy.make(Attendance, customer=self.customer,
                                     status='draft',
                                     initial_service=self.service,
                                     address=self.user_address,
                                     )
        url = reverse('api:api_attendance_observation', kwargs={'pk':self.attendance.id})
        observation = 'Lorem Ipsion, Lorem Ipsun'
        response = self.client.post(url, {'observation': observation,
                                          'pricing_criterion_option': self.pricing_criterion_option.id},
                                    HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['observation'], observation)
        self.assertEqual(response.data['pricing_criterion_option']['id'], self.pricing_criterion_option.id)

class AddressApiTest(Autentication, APITestCase):
    get_url = reverse('api:api_address_list')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = mommy.make(User, email='teste@email.com', password='password', first_name='Teste')
        cls.user = user
        cls.customer = mommy.make(Customer, user=cls.user)
        cls.single_user_address = mommy.make(UserAddress, user=user, _fill_optional=True)

    def setUp(self):
        self.token = self.create_authorization_header(self.create_token(self.user))
        self.user_address = mommy.make(UserAddress, user=self.user, _fill_optional=True, _quantity=3)
        self.single_user_address = mommy.make(UserAddress, user=self.user, _fill_optional=True)

    def test_get_cep(self):
        url = reverse('api:api_address', kwargs={'cep': '50670400'})
        response = self.client.get(self.get_url, {}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_address(self):
        response = self.client.get(self.get_url, {}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_address(self):
        address = {
            'postal_code': '50670400',
            'address': 'Rua Teste TEste TEste',
            'number': '123123',
            'complemento': '',
            'neighborhood': 'Iputinga',
            'city': 'Recife',
            'state': 'PE'
        }
        response = self.client.post(self.get_url, address, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.user.id)

    def test_create_address_with_name(self):
        address = {
            'name': 'casa',
            'postal_code': '50670400',
            'address': 'Rua Teste TEste TEste',
            'number': '123123',
            'complemento': '',
            'neighborhood': 'Iputinga',
            'city': 'Recife',
            'state': 'PE'
        }
        response = self.client.post(self.get_url, address, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.user.id)

    def test_update_address(self):
        single_user_address = mommy.make(UserAddress, user=self.user, _fill_optional=True)
        url = reverse('api:api_address_detail', kwargs={'pk': single_user_address.id})
        address = {
            'name': 'casa',
            'postal_code': '50670400',
            'address': 'Rua Teste TEste TEste',
            'number': '123123',
            'complemento': '',
            'neighborhood': 'Iputinga',
            'city': 'Recife',
            'state': 'PE'
        }
        response = self.client.put(url, address, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['postal_code'], address['postal_code'])

    def test_detail_address(self):
        single_user_address = mommy.make(UserAddress, user=self.user, _fill_optional=True)
        url = reverse('api:api_address_detail', kwargs={'pk': single_user_address.id})
        response = self.client.get(url, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['postal_code'], single_user_address.postal_code)

    def test_delete_address(self):
        single_user_address = mommy.make(UserAddress, user=self.user, _fill_optional=True)
        url = reverse('api:api_address_detail', kwargs={'pk': single_user_address.id})
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CardApiTest(Autentication, APITestCase):
    get_url = reverse('api:api_credit_card')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = mommy.make(User, email='teste@email.com', password='password', first_name='Teste')
        cls.user = user
        customer = mommy.make(Customer, user=cls.user, iugu_client_id=None)
        cls.customer = customer
        card_data = '{"data": {"year": "2020", "first_name": "Joao", "number": "4242424242424242", ' \
                    '"last_name": "Carlos", "verification_value": "422", "month": "10"}, ' \
                    '"account_id": "4F0BDE14961D4AE4A9917575CC6A862A", "method": "credit_card"}'
        iugu_payment_token = '{"method": "credit_card", "extra_info": {"holder_name": "Joao Carlos",' \
                             ' "year": 2020, "bin": "424242", "display_number": "XXXX-XXXX-XXXX-4242", ' \
                             '"brand": "VISA", "month": 10}, "test": true, "id": "4770449C7C954B5FBDAF3A6FABDA564D"}'
        cls.user_credit_card = mommy.make(CreditCard,card_data=card_data, iugu_payment_token=iugu_payment_token,
                                          customer=customer, _quantity=3)
        cls.single_credit_card = mommy.make(CreditCard,card_data=card_data, iugu_payment_token=iugu_payment_token,
                                            customer=customer)

    def setUp(self):
        self.token = self.create_authorization_header(self.create_token(self.user))

    def test_list_credit_card(self):
        response = self.client.get(self.get_url, {}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_credit_card(self):
        card = {
            'number': '4242424242424242',
            'verification_value': '123',
            'name': 'Teste Iugu',
            'month': '1',
            'year': '2030'
        }
        response = self.client.post(self.get_url, card, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_detail_credit_card(self):
        url = reverse('api:api_credit_card_detail', kwargs={'pk': self.single_credit_card.id})
        response = self.client.get(url, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_credit_card(self):
        url = reverse('api:api_credit_card_detail', kwargs={'pk': self.single_credit_card.id})
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # escolher um horário com profissional
    # escolher um horário sem profissional
    # mudar o status de waiting_confirmation para confirmated
    # mudar o status de confirmated para on_transfer
    # mudar o status de on_transfer para waiting_confirmation
    # mudar o status de in_attendance para completed
    # mudar o status de waiting_confirmation para expired
