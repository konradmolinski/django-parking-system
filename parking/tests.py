from datetime import datetime, timedelta
import pytz
import random
import string
import json
from django.test import TestCase
from django.conf import settings
from parking.models import Subscription, Client, PaymentRegister, ParkingEntry
from rest_framework.test import RequestsClient
from .utils import parking_cost, sub_cost

timezone = pytz.timezone(settings.TIME_ZONE)
client = RequestsClient()

class ParkingEntryWhileNoSpotsTestCase(TestCase):

    def create_client_with_parking_entry(self, plate_nr=random.randint(1,1000)):

        client = Client(plate_num=f"plateno{plate_nr}")
        parking_entry = ParkingEntry(billing_type='ADH', client=client, plate_num=client.plate_num)
        client.save()
        parking_entry.save()
        return parking_entry

    def setUp(self):

        for x in list(range(settings.PARKING_SPOTS)):
            self.create_client_with_parking_entry(x)

    def test_available_space(self):
        self.assertEqual(ParkingEntry.free_spots(), 0)

    def test_create_parking_entry_while_no_free_spots(self):

        data = {"plate_nr": f"platenrrrr{random.randint(1,1000)}"}
        headers = {"Content-type": 'application/json'}

        response = client.post(url="http://localhost:8000/api/get-ticket", json=data, headers=headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ParkingEntry.objects.all().count(), settings.PARKING_SPOTS)

class FreeParkingSpotsAmountTestCases(TestCase):

    def create_client_with_parking_entry(self, plate_nr=random.randint(1, 1000)):
        client = Client(plate_num=f"plateno{plate_nr}")
        parking_entry = ParkingEntry(billing_type='ADH', client=client, plate_num=client.plate_num)
        client.save()
        parking_entry.save()
        return parking_entry

    def test_empty_parking(self):
        response = client.get(url="http://localhost:8000/api/free-spots")
        self.assertEqual(response.json()['free_spots'], settings.PARKING_SPOTS)

    def test_free_spots_amount(self):

        for x in list(range(0, settings.PARKING_SPOTS)):
            self.create_client_with_parking_entry(x)
            response = client.get(url="http://localhost:8000/api/free-spots")
            self.assertEqual(response.json()['free_spots'], settings.PARKING_SPOTS - x - 1)

class PlateNumberLengthTestCases(TestCase):

    def test_empty_plate_num(self):

        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/get-ticket", json={"plate_nr": ""}, headers=headers)
        self.assertEqual(response.status_code, 400)

        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/subscription", json={"plate_nr": ""}, headers=headers)
        self.assertEqual(response.status_code, 400)

        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/voucher", json={"plate_nr": ""}, headers=headers)
        self.assertEqual(response.status_code, 400)


    def test_various_plate_num_length(self):

        headers = {'Content-type': 'application/json'}
        max_length = ParkingEntry._meta.get_field('plate_num').max_length
        letters = string.printable

        plate_num = "".join(random.choice(letters) for i in range(max_length + 1))
        response = client.post(url="http://localhost:8000/api/get-ticket", json={"plate_nr": plate_num},
                               headers=headers)
        self.assertEqual(response.status_code, 400)

        plate_num = "".join(random.choice(letters) for i in range(max_length + 1))
        response = client.post(url="http://localhost:8000/api/subscription", json={"plate_nr": plate_num},
                               headers=headers)
        self.assertEqual(response.status_code, 400)

        plate_num = "".join(random.choice(letters) for i in range(max_length + 1))
        response = client.post(url="http://localhost:8000/api/voucher", json={"plate_nr": plate_num},
                               headers=headers)
        self.assertEqual(response.status_code, 400)

        for x in list(range(1, max_length + 1)):
            plate_num = "".join(random.choice(letters) for i in range(x))
            response = client.post(url="http://localhost:8000/api/get-ticket", json={"plate_nr": plate_num},
                                    headers=headers)
            self.assertEqual(response.status_code, 200)

class MultipleParkingEntryTestCase(TestCase):

    def create_client_with_parking_entry(self, plate_nr=random.randint(1, 1000)):
        client = Client(plate_num=f"plateno{plate_nr}")
        parking_entry = ParkingEntry(billing_type='ADH', client=client, plate_num=client.plate_num)
        client.save()
        parking_entry.save()
        return parking_entry

    def setUp(self):
        self.parking_entry = self.create_client_with_parking_entry()

    def test_multiple_parking_entry_by_same_plate_num(self):
        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/get-ticket",
                               json={"plate_nr": self.parking_entry.plate_num}, headers=headers)
        self.assertEqual(response.status_code, 400)

class ReturnWrongTicketValueTestCases(TestCase):

    def create_client_with_parking_entry(self, plate_nr=random.randint(1, 1000)):
        client = Client(plate_num=f"plateno{plate_nr}")
        parking_entry = ParkingEntry(billing_type='ADH', client=client, plate_num=client.plate_num)
        client.save()
        parking_entry.save()
        return parking_entry

    def test_nonnumeric_ticket_value(self):
        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/return-ticket",
                               json={"ticket_id": "".join(random.choice(string.ascii_letters
                                                                        ))}, headers=headers)
        self.assertEqual(response.status_code, 400)

        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/pay",
                               json={"ticket_id": "".join(random.choice(string.ascii_letters
                                                                        )),
                                     "payment_status" : "P"}, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_return_nonexistent_ticket(self):
        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/return-ticket",
                               json={"ticket_id": str(random.randint(1, 1000))}, headers=headers)
        self.assertEqual(response.status_code, 404)

        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/pay",
                               json={"ticket_id": str(random.randint(1, 1000)),
                                     "payment_status" : "P"}, headers=headers)
        self.assertEqual(response.status_code, 404)

    def setUp(self):
        self.parking_entry = self.create_client_with_parking_entry()

    def test_return_already_returned_ticket(self):
        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/return-ticket",
                               json={"ticket_id": str(self.parking_entry.id)}, headers=headers)
        self.assertEqual(response.status_code, 200)

        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/return-ticket",
                               json={"ticket_id": str(self.parking_entry.id)}, headers=headers)

        self.assertEqual(response.status_code, 400)

class ReturnWrongPaymentDataTestCases(TestCase):

    def create_client_with_parking_entry(self, plate_nr=random.randint(1, 1000)):
        client = Client(plate_num=f"plateno{plate_nr}")
        parking_entry = ParkingEntry(billing_type='ADH', client=client, plate_num=client.plate_num)
        client.save()
        parking_entry.save()
        return parking_entry

    def setUp(self):
        self.parking_entry = self.create_client_with_parking_entry()

    def test_already_paid_ticket_payment(self):

        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/return-ticket",
                               json={"ticket_id": str(self.parking_entry.id)}, headers=headers)
        self.assertEqual(response.status_code, 200)

        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/pay",
                               json={"ticket_id": str(self.parking_entry.id),
                                     "payment_status": "P"}, headers=headers)
        self.assertEqual(response.status_code, 200)

        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/pay",
                               json={"ticket_id": str(self.parking_entry.id),
                                     "payment_status": "P"}, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_wrong_payment_status_payment(self):
        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/pay",
                               json={"ticket_id": str(self.parking_entry.id),
                                     "payment_status": "EH"}, headers=headers)
        self.assertEqual(response.status_code, 400)

class AmountValueWhileLeavingParkingTestCases(TestCase):

    timezone = pytz.timezone(settings.TIME_ZONE)

    def create_client_with_parking_entry(self, plate_nr=random.randint(1, 1000)):
        client = Client(plate_num=f"plateno{plate_nr}")
        parking_entry = ParkingEntry(billing_type='ADH', client=client, plate_num=client.plate_num)
        client.save()
        parking_entry.save()
        return parking_entry

    def create_client_with_parking_entry_and_subscription(self, plate_nr=random.randint(1, 1000),
                                                          start_date=timezone.localize(datetime.today()),
                                                          end_date=timezone.localize(datetime.today() + timedelta(days=5))):
        client = Client(plate_num=f"plateno{plate_nr}")
        payment = PaymentRegister(amount=sub_cost.get_subscription_cost(start_date, end_date), status='P')
        subscription = Subscription(client_id=client, start_date=start_date, end_date=end_date, payment_id=payment)
        parking_entry = ParkingEntry(billing_type='SUB', client=client, plate_num=client.plate_num)
        client.save()
        payment.save()
        subscription.save()
        parking_entry.save()
        return parking_entry

    def setUp(self, timezone=timezone):
        self.ad_hoc_parking_entry = self.create_client_with_parking_entry(plate_nr=1)
        self.sub_parking_entry = self.create_client_with_parking_entry_and_subscription(plate_nr=2)
        self.sub_overtime_parking_entry = self.create_client_with_parking_entry_and_subscription(plate_nr=3,
            start_date=timezone.localize(datetime.today() - timedelta(days=5)),
            end_date=timezone.localize(datetime.today()))

        self.sub_in_future_parking_entry = self.create_client_with_parking_entry_and_subscription(plate_nr=4,
            start_date=timezone.localize(datetime.today() + timedelta(days=5)),
            end_date=timezone.localize(datetime.today() + timedelta(days=10)))

    def test_amount_value_while_ad_hoc_billing_type(self, timezone=timezone):
        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/return-ticket",
                               json={"ticket_id": str(self.ad_hoc_parking_entry.id)}, headers=headers)

        amount = parking_cost.calculate_parking_cost(self.ad_hoc_parking_entry.start_date,
                                                     timezone.localize(datetime.now()))
        self.assertEqual(response.json()['amount'], amount)

    def test_amount_value_while_sub_billing_type(self):
        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/return-ticket",
                               json={"ticket_id": str(self.sub_parking_entry.id)}, headers=headers)

        self.assertEqual(response.json()['amount'], 0)

    def test_amount_value_while_sub_with_overtime(self, timezone=timezone):
        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/return-ticket",
                               json={"ticket_id": str(self.sub_overtime_parking_entry.id)}, headers=headers)

        subscription = Subscription.objects.get(client_id=self.sub_overtime_parking_entry.client)
        amount = parking_cost.calculate_parking_cost(subscription.end_date, timezone.localize(datetime.now()))
        self.assertEqual(response.json()['amount'], amount)

    def test_amount_value_while_sub_date_in_future(self, timezone=timezone):
        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/return-ticket",
                               json={"ticket_id": str(self.sub_in_future_parking_entry.id)}, headers=headers)

        amount = parking_cost.calculate_parking_cost(self.ad_hoc_parking_entry.start_date,
                                                     timezone.localize(datetime.now()))
        self.assertEqual(response.json()['amount'], amount)

class SubscriptionOverloadTestCase(TestCase):

    def create_subscription_with_client(self, plate_nr=random.randint(1,1000), start_date=datetime.today(),
                                        end_date=datetime.today() + timedelta(days=5)):
        client = Client(plate_num=f"plateno{plate_nr}")
        payment = PaymentRegister(amount=1, status='P')
        subscription = Subscription(client_id=client, start_date=start_date, end_date=end_date, payment_id=payment)
        client.save()
        payment.save()
        subscription.save()
        return subscription

    def setUp(self):
        timezone = pytz.timezone(settings.TIME_ZONE)
        for x in list(range(0, settings.PARKING_SPOTS -5)):
            self.create_subscription_with_client(x, timezone.localize(datetime.now()),
                                                 timezone.localize(datetime.now() + timedelta(days=28)))

    def test_available_spaces(self):
        self.assertEqual(ParkingEntry.free_spots(), 5)

    def test_create_more_subscriptions_than_places(self):

        for x in range(0, 5):
            data = {
                "end_date": datetime.now().strftime("%Y-%m-%d"),
                "start_date": (datetime.now()+timedelta(days=28)).strftime("%Y-%m-%d"),
                "plate_nr": f"platenrrrr{x}",
            }
            headers = {'Content-type': 'application/json'}

            response = client.post(url="http://localhost:8000/api/pay-sub", json=data, headers=headers)
            self.assertEqual(response.status_code, 400)
        self.assertEqual(Subscription.objects.all().count(), settings.PARKING_SPOTS - 5)

class SubscriptionOverloadInFutureTestCase(TestCase):

    def create_subscription_with_client(self, plate_nr=random.randint(1,1000),
                                        start_date=timezone.localize(datetime.today()),
                                        end_date=timezone.localize(datetime.today() + timedelta(days=7))):
        client = Client(plate_num=f"plateno{plate_nr}")
        payment = PaymentRegister(amount=1, status='P')
        subscription = Subscription(client_id=client, start_date=start_date, end_date=end_date, payment_id=payment)
        client.save()
        payment.save()
        subscription.save()
        return subscription

    def setUp(self):
        timezone = pytz.timezone(settings.TIME_ZONE)
        for x in list(range(0, settings.PARKING_SPOTS -5)):
            self.create_subscription_with_client(plate_nr=x,
                                                 start_date=timezone.localize(datetime.today() + timedelta(days=14)),
                                                 end_date=timezone.localize(datetime.today() + timedelta(days=21)))

    def test_free_spots_while_subscriptions_in_future(self):
        self.assertEqual(ParkingEntry.free_spots(), settings.PARKING_SPOTS)

    def test_create_subscription_with_date_bigger_then_max_subscription_date(self):

        for x in range(0, 5):
            data = {
                "end_date": (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d"),
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "plate_nr": f"platenrrrr{x}",
            }
            headers = {'Content-type': 'application/json'}

            response = client.post(url="http://localhost:8000/api/pay-sub", json=data, headers=headers)
            self.assertEqual(response.status_code, 400)
        self.assertEqual(Subscription.objects.all().count(), settings.PARKING_SPOTS - 5)

    def test_create_subscription_with_date_smaller_then_max_subscription_date(self):

        for x in range(0, 5):
            data = {
                "end_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "plate_nr": f"platenrrrr{x}",
            }
            headers = {'Content-type': 'application/json'}

            response = client.post(url="http://localhost:8000/api/pay-sub", json=data, headers=headers)
            self.assertEqual(response.status_code, 200)

        self.assertEqual(Subscription.objects.all().count(), settings.PARKING_SPOTS)
        self.assertEqual(ParkingEntry.free_spots(), settings.PARKING_SPOTS - 5)

    def test_create_subscription_with_date_as_max_subscription_date(self):

        for x in range(0, 5):
            data = {
                "end_date": (datetime.now() + timedelta(days=13)).strftime("%Y-%m-%d"),
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "plate_nr": f"platenrrrr{x}",
            }
            headers = {'Content-type': 'application/json'}

            response = client.post(url="http://localhost:8000/api/pay-sub", json=data, headers=headers)
            self.assertEqual(response.status_code, 200)

        self.assertEqual(Subscription.objects.all().count(), settings.PARKING_SPOTS)
        self.assertEqual(ParkingEntry.free_spots(), settings.PARKING_SPOTS - 5)

class SubscriptionModelFunctionsTestCases(TestCase):

    def create_subscription_with_client(self, plate_nr=random.randint(1,1000), start_date=datetime.today(),
                                        end_date=datetime.today() + timedelta(days=5)):
        client = Client(plate_num=f"plateno{plate_nr}")
        payment = PaymentRegister(amount=1, status='P')
        subscription = Subscription(client_id=client, start_date=start_date, end_date=end_date, payment_id=payment)
        client.save()
        payment.save()
        subscription.save()
        return subscription

    def setUp(self):
        timezone = pytz.timezone(settings.TIME_ZONE)
        for x in list(range(5)):
            self.create_subscription_with_client(x, timezone.localize(datetime.now()),
                                                 timezone.localize(datetime.now() + timedelta(days=28)))

    def test_subscriptions_available_func(self):
        self.assertEqual(Subscription.subscriptions_available(), settings.PARKING_SPOTS * 0.9 - 5)

    def test_max_possible_subscription_time(self):
        self.assertEqual(Subscription.max_possible_subscription_time(), 28)

class ClientSubscriptionInRangeFunctionTestCase(TestCase):

    def create_subscription_with_client(self, plate_nr=random.randint(1,1000), start_date=datetime.today(),
                                        end_date=datetime.today() + timedelta(days=5)):
        client = Client(plate_num=f"plateno{plate_nr}")
        payment = PaymentRegister(amount=1, status='P')
        subscription = Subscription(client_id=client, start_date=start_date, end_date=end_date, payment_id=payment)
        client.save()
        payment.save()
        subscription.save()
        return client

    def setUp(self):
        self.client = self.create_subscription_with_client()

    def test_has_subscription_in_range_function_exact(self):
        timezone = pytz.timezone(settings.TIME_ZONE)
        start_date = timezone.localize(datetime.today())
        end_date = timezone.localize(datetime.today() + timedelta(days=5))
        self.assertEqual(Client.has_subscription_in_range(self.client, start_date, end_date), False)

    def test_has_subscription_in_range_function_pre(self):
        timezone = pytz.timezone(settings.TIME_ZONE)
        start_date = timezone.localize(datetime.today() - timedelta(days=3))
        end_date = timezone.localize(datetime.today() + timedelta(days=3))
        self.assertEqual(Client.has_subscription_in_range(self.client, start_date, end_date), False)

    def test_has_subscription_in_range_function_post(self):
        timezone = pytz.timezone(settings.TIME_ZONE)
        start_date = timezone.localize(datetime.today() + timedelta(days=2))
        end_date = timezone.localize(datetime.today() + timedelta(days=10))
        self.assertEqual(Client.has_subscription_in_range(self.client, start_date, end_date), False)

    def test_has_subscription_in_range_function(self):
        timezone = pytz.timezone(settings.TIME_ZONE)
        start_date = timezone.localize(datetime.today() + timedelta(days=20))
        end_date = timezone.localize(datetime.today() + timedelta(days=30))
        self.assertEqual(Client.has_subscription_in_range(self.client, start_date, end_date), True)

class SubscriptionWrongDateInputTestCases(TestCase):

    def test_clients_subscription_double_booking(self):
        data = {
            "end_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "start_date": (datetime.now()).strftime("%Y-%m-%d"),
            "plate_nr": "plate",
        }
        headers = {'Content-type': 'application/json'}

        response = client.post(url="http://localhost:8000/api/subscription", json=data, headers=headers)
        self.assertEqual(response.status_code, 200)

        response = client.post(url="http://localhost:8000/api/pay-sub", json=data, headers=headers)
        self.assertEqual(response.status_code, 200)

        data = {
            "end_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "start_date": (datetime.now()).strftime("%Y-%m-%d"),
            "plate_nr": "plate",
        }
        headers = {'Content-type': 'application/json'}

        response = client.post(url="http://localhost:8000/api/subscription", json=data, headers=headers)
        self.assertEqual(response.status_code, 400)

        response = client.post(url="http://localhost:8000/api/pay-sub", json=data, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_start_date_bigger_then_end_date_insert(self):
        data = {
            "end_date": (datetime.now()).strftime("%Y-%m-%d"),
            "start_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "plate_nr": "plate1",
        }
        headers = {'Content-type': 'application/json'}

        response = client.post(url="http://localhost:8000/api/subscription", json=data, headers=headers)
        self.assertEqual(response.status_code, 400)

        response = client.post(url="http://localhost:8000/api/pay-sub", json=data, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_too_big_date_value_insert(self):
        data = {
            "end_date": datetime(3000, 2, 2).strftime("%Y-%m-%d"),
            "start_date": datetime(3000, 3, 3).strftime("%Y-%m-%d"),
            "plate_nr": "plate3",
        }
        headers = {'Content-type': 'application/json'}

        response = client.post(url="http://localhost:8000/api/subscription", json=data, headers=headers)
        self.assertEqual(response.status_code, 400)

        response = client.post(url="http://localhost:8000/api/pay-sub", json=data, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_wrong_date_format_input(self):
        data = {
            "end_date": '564-43-0',
            "start_date": 'aaaa-bb-vv',
            "plate_nr": "plate3",
        }
        headers = {'Content-type': 'application/json'}

        response = client.post(url="http://localhost:8000/api/subscription", json=data, headers=headers)
        self.assertEqual(response.status_code, 400)

        response = client.post(url="http://localhost:8000/api/pay-sub", json=data, headers=headers)
        self.assertEqual(response.status_code, 400)

class VoucherHoursAmountWrongDateInputTestCase(TestCase):

    def test_nonnumeric_hours_amount_value(self):
        headers = {'Content-type': 'application/json'}
        data = {
            "voucher_hours": "".join(random.choice(string.ascii_letters)),
            "plate_nr": "abc123",
        }
        response = client.post(url="http://localhost:8000/api/voucher",
                               json=data,
                               headers=headers)
        self.assertEqual(response.status_code, 400)

class ClientVoucherAmountTestCase(TestCase):

    def test_client_voucher_transaction(self):
        headers = {'Content-type': 'application/json'}
        data = {
            "voucher_hours": "50",
            "plate_nr": "abc123",
        }
        response = client.post(url="http://localhost:8000/api/pay-voucher",
                               json=data,
                               headers=headers)

        self.assertEqual(float(response.json()['current_voucher_amount']), 3600*50)

        response = client.post(url="http://localhost:8000/api/pay-voucher",
                               json=data,
                               headers=headers)

        self.assertEqual(float(response.json()['current_voucher_amount']), 3600*50*2)

    def create_client_with_parking_entry(self, plate_nr=random.randint(1, 1000)):
        client = Client(plate_num=f"plateno{plate_nr}", voucher=timedelta(seconds=3600))
        parking_entry = ParkingEntry(start_date=(datetime.now() - timedelta(seconds=600)), billing_type='VCR',
                                     client=client, plate_num=client.plate_num)
        client.save()
        parking_entry.save()
        return parking_entry

    def setUp(self):
        self.parking_entry = self.create_client_with_parking_entry()

    def test_client_voucher_amount_after_parking_escape(self):
        headers = {'Content-type': 'application/json'}
        response = client.post(url="http://localhost:8000/api/return-ticket",
                               json={"ticket_id": self.parking_entry.id}, headers=headers)
        self.assertEqual(float(response.json()['voucher_time_left']), 3000)


