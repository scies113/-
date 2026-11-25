"""Проверки фильтрации и изменения партий через формы ПР11."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from preserves.models import Preserve, Product

from .models import ACTIVE_BATCH_CONFLICT, Batch


class BatchFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        product = Product.objects.create(name="Брусника", category="ягоды")
        cls.recipe = Preserve.objects.create(name="Варенье", product=product)
        cls.admin = get_user_model().objects.create_superuser("keeper")
        cls.today = timezone.localdate()

    def setUp(self):
        self.client.force_login(self.admin)
        self.create_url = reverse("batches:create")
        self.data = {
            "preserve": self.recipe.pk, "quantity": 4,
            "production_date": self.today.isoformat(),
        }

    def make_batch(self, **changes):
        return Batch.objects.create(**{
            "preserve": self.recipe, "production_date": self.today,
            "quantity": 4, **changes,
        })

    def test_create_uses_initial_date_permissions_and_post(self):
        self.assertContains(
            self.client.get(self.create_url), self.today.isoformat()
        )
        self.assertEqual(Batch.objects.count(), 0)
        response = self.client.post(
            self.create_url, {**self.data, "status": Batch.Status.DISCARDED}
        )
        batch = Batch.objects.get()
        self.assertRedirects(
            response, reverse("batches:detail", args=[batch.pk])
        )
        self.assertEqual(batch.status, Batch.Status.ACTIVE)
        self.assertEqual(batch.quantity, 4)

    def test_invalid_or_past_date_and_quantity_are_not_saved(self):
        day = self.today - timedelta(days=1)
        for patch, field in (
            ({"production_date": day.isoformat()}, "production_date"),
            ({"production_date": "2026-02-30"}, "production_date"),
            ({"quantity": 0}, "quantity"),
            ({"preserve": 99999}, "preserve"),
            ({"quantity": ""}, "quantity"),
        ):
            data = {**self.data, **patch}
            response = self.client.post(self.create_url, data)
            self.assertIn(field, response.context["form"].errors)
        self.assertEqual(Batch.objects.count(), 0)

    def test_duplicate_batches_blocked_in_form_and_database(self):
        self.make_batch()
        response = self.client.post(self.create_url, self.data)
        self.assertContains(response, ACTIVE_BATCH_CONFLICT)
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.make_batch()
        self.assertEqual(Batch.objects.count(), 1)

    def test_update_ignores_itself_and_rejects_other_active_batch(self):
        batch = self.make_batch()
        tomorrow = self.today + timedelta(days=1)
        self.make_batch(production_date=tomorrow)
        url = reverse("batches:update", args=[batch.pk])
        self.assertContains(self.client.get(url), self.today.isoformat())
        conflict = self.client.post(
            url, {**self.data, "production_date": tomorrow.isoformat()}
        )
        self.assertContains(conflict, ACTIVE_BATCH_CONFLICT)
        response = self.client.post(url, {**self.data, "quantity": 9})
        self.assertEqual(response.status_code, 302)
        batch.refresh_from_db()
        self.assertEqual(batch.quantity, 9)
        self.assertEqual(Batch.objects.count(), 2)

    def test_historic_batch_keeps_its_date_when_count_is_edited(self):
        past = self.today - timedelta(days=1)
        batch = self.make_batch(production_date=past)
        url = reverse("batches:update", args=[batch.pk])
        response = self.client.post(url, {
            **self.data, "quantity": 6, "production_date": past.isoformat()
        })
        self.assertEqual(response.status_code, 302)
        batch.refresh_from_db()
        self.assertEqual((batch.quantity, batch.production_date), (6, past))

    def test_discard_is_post_only_releases_slot_and_keeps_history(self):
        batch = self.make_batch()
        url = reverse("batches:discard", args=[batch.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertTrue(Batch.objects.active().filter(pk=batch.pk).exists())
        self.assertRedirects(self.client.post(url), reverse("batches:list"))
        batch.refresh_from_db()
        self.assertEqual(batch.status, Batch.Status.DISCARDED)
        self.assertEqual(batch.available_quantity, 0)
        self.assertEqual(self.client.post(url).status_code, 404)
        edit_url = reverse("batches:update", args=[batch.pk])
        self.assertEqual(self.client.get(edit_url).status_code, 404)
        self.assertEqual(
            self.client.post(self.create_url, self.data).status_code, 302
        )
        self.assertEqual(Batch.objects.count(), 2)

    def test_write_access_and_csrf(self):
        anonymous = Client()
        self.assertEqual(anonymous.get(self.create_url).status_code, 302)
        anonymous.force_login(get_user_model().objects.create_user("viewer"))
        self.assertEqual(anonymous.get(self.create_url).status_code, 403)
        guarded = Client(enforce_csrf_checks=True)
        guarded.force_login(self.admin)
        self.assertEqual(
            guarded.post(self.create_url, self.data).status_code, 403
        )
        guarded.get(self.create_url)
        csrf = guarded.cookies["csrftoken"].value
        self.assertEqual(
            guarded.post(
                self.create_url, {**self.data, "csrfmiddlewaretoken": csrf}
            ).status_code,
            302,
        )

    def test_filter_rejects_invalid_dates_and_conflicting_choices(self):
        product = Product.objects.create(name="Яблоко", category="фрукты")
        url = reverse("batches:search")
        invalid = self.client.get(url, {"date": "2026-02-30"})
        self.assertIn("date", invalid.context["form"].errors)
        mismatch = self.client.get(
            url, {"preserve": self.recipe.pk, "product": product.pk}
        )
        self.assertTrue(mismatch.context["form"].non_field_errors())
        fallback = self.client.get(url, {"sort": "invalid"})
        self.assertIn("sort", fallback.context["form"].errors)
