"""Проверки админки, остатков и ORM-выборок погреба."""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from preserves.models import Preserve, Product

from .models import Batch


class StockWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.day = date(2026, 10, 22)
        cls.product = Product.objects.create(name="Брусника", category="ягоды")
        cls.preserve = Preserve.objects.create(
            name="Брусничное варенье", product=cls.product
        )
        cls.batch = Batch.objects.create(
            preserve=cls.preserve, production_date=cls.day, quantity=8
        )

    def test_slug_and_numeric_urls_open_same_recipe(self):
        for url in (
            self.preserve.get_absolute_url(),
            reverse("preserves:detail", args=[self.preserve.pk]),
        ):
            self.assertContains(self.client.get(url), self.preserve.name)
        unknown = reverse("preserves:detail_by_slug", args=["нет-рецепта"])
        self.assertEqual(self.client.get(unknown).status_code, 404)

    def test_availability_requires_positive_active_stock_on_date(self):
        url = reverse("preserves:list")
        params = {"date": self.day.isoformat(), "q": "БРУСНИЧНОЕ"}
        response = self.client.get(url, params)
        self.assertEqual(list(response.context["preserves"]), [self.preserve])
        self.assertFalse(self.client.get(
            url, {"date": "2026-10-23"}
        ).context["preserves"])
        for status, quantity in (
            (Batch.Status.CONSUMED, 8),
            (Batch.Status.DISCARDED, 8),
            (Batch.Status.ACTIVE, 0),
        ):
            Batch.objects.filter(pk=self.batch.pk).update(
                status=status, quantity=quantity
            )
            self.assertFalse(self.client.get(url, params).context["preserves"])

    def test_generated_stock_follows_quantity_and_status(self):
        self.batch.quantity = 4
        self.batch.save(update_fields=["quantity"])
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.available_quantity, 4)
        self.batch.status = Batch.Status.DISCARDED
        self.batch.save(update_fields=["status"])
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.available_quantity, 0)
        self.assertEqual(self.batch.quantity, 4)

    def test_search_combines_filters_and_keeps_them_on_second_page(self):
        for quantity in range(1, 7):
            Batch.objects.create(
                preserve=self.preserve,
                production_date=self.day + timedelta(days=quantity),
                quantity=quantity,
            )
        Batch.objects.create(
            preserve=self.preserve, production_date=self.day, quantity=30,
            status=Batch.Status.CONSUMED,
        )
        url = reverse("batches:search")
        params = {
            "q": "БРУСНИКА",
            "preserve": self.preserve.pk, "product": self.product.pk,
            "status": Batch.Status.ACTIVE, "sort": "quantity",
        }
        with self.assertNumQueries(4):
            response = self.client.get(url, params)
        first_page = response.context["page_obj"]
        self.assertEqual(first_page.paginator.count, 7)
        self.assertContains(response, "page=2")
        self.assertContains(response, f"preserve={self.preserve.pk}")
        self.assertContains(response, f"product={self.product.pk}")
        self.assertContains(response, "sort=quantity")
        self.assertEqual(
            [row["available_quantity"] for row in first_page], [8, 6, 5, 4, 3]
        )
        response = self.client.get(url, {**params, "page": 2})
        second = response.context["page_obj"]
        self.assertEqual([row["available_quantity"] for row in second], [2, 1])
        dated = self.client.get(url, {**params, "date": self.day.isoformat()})
        self.assertEqual(dated.context["page_obj"].paginator.count, 1)

    def test_batch_detail_loads_recipe_and_product_in_one_query(self):
        with self.assertNumQueries(1):
            response = self.client.get(
                reverse("batches:detail", args=[self.batch.pk])
            )
        self.assertContains(response, self.preserve.name)
        self.assertContains(response, self.product.name)

    def test_admin_lists_search_filters_and_inlines(self):
        url = reverse("admin:index")
        self.assertEqual(self.client.get(url).status_code, 302)
        password = "test-only-password-2026"
        username = "operator"
        get_user_model().objects.create_superuser(username, password=password)
        logged_in = self.client.login(username=username, password=password)
        self.assertTrue(logged_in)
        self.assertContains(self.client.get(url), "Сырьё и заготовки")
        for name in (
            "admin:preserves_product_changelist",
            "admin:preserves_preserve_changelist",
            "admin:batches_batch_changelist",
        ):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        listing = reverse("admin:batches_batch_changelist")
        response = self.client.get(
            listing, {"q": "БРУСНИКА", "status__exact": Batch.Status.ACTIVE}
        )
        self.assertEqual(response.context["cl"].result_count, 1)
        excluded = self.client.get(
            listing, {"q": "БРУСНИКА", "status__exact": Batch.Status.CONSUMED}
        )
        self.assertEqual(excluded.context["cl"].result_count, 0)
        recipe = reverse("admin:preserves_preserve_change",
                         args=[self.preserve.pk])
        response = self.client.get(recipe)
        self.assertContains(response, "id_batches-0-status")
        self.assertRedirects(
            self.client.get(response.context["absolute_url"]),
            f"http://testserver{self.preserve.get_absolute_url()}",
        )
        product = reverse("admin:preserves_product_change",
                          args=[self.product.pk])
        self.assertContains(self.client.get(product), "id_preserves-0-name")

    def test_admin_status_change_updates_catalog_and_statistics(self):
        admin = get_user_model().objects.create_superuser("manager")
        self.client.force_login(admin)
        url = reverse("admin:batches_batch_change", args=[self.batch.pk])
        response = self.client.post(url, {
            "preserve": self.preserve.pk,
            "production_date": self.day.isoformat(),
            "quantity": self.batch.quantity,
            "status": Batch.Status.DISCARDED,
            "_save": "1",
        })
        self.assertEqual(response.status_code, 302)
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.status, Batch.Status.DISCARDED)
        self.assertEqual(self.batch.available_quantity, 0)
        stats = self.client.get(reverse("batches:statistics")).context
        self.assertEqual(stats["total_batches_count"], 1)
        self.assertEqual(stats["active_batches_count"], 0)
        self.assertEqual(stats["discarded_batches_count"], 1)
        self.assertEqual(stats["total_jars"], 0)
        stock = self.client.get(reverse("preserves:list"), {
            "date": self.day.isoformat(),
        }).context["preserves"]
        self.assertFalse(stock)
