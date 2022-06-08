from datetime import datetime, timedelta
import pytz
from django.test import TestCase
from django.conf import settings
from parking.models import Subscription, Client, PaymentRegister, ParkingEntry
from rest_framework.test import RequestsClient
import random
import json

client = RequestsClient()
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






