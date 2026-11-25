"""Проверки загрузки фотографий из веб-форм и Django Admin."""

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import Preserve, Product


def photo(filename="recipe.png", color="red", size=(8, 8)):
    content = BytesIO()
    Image.new("RGB", size, color=color).save(content, "PNG")
    return SimpleUploadedFile(
        filename, content.getvalue(), content_type="image/png"
    )


class PreservePhotoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(name="Брусника", category="ягоды")
        cls.admin = get_user_model().objects.create_superuser("photographer")

    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.media = Path(temporary.name)
        settings = self.settings(MEDIA_ROOT=self.media)
        settings.enable()
        self.addCleanup(settings.disable)
        self.client.force_login(self.admin)
        self.create_url = reverse("preserves:create")
        self.data = {"name": "Варенье", "product": self.product.pk}

    def test_multipart_upload_saves_file_and_shows_it_in_recipe(self):
        self.assertContains(
            self.client.get(self.create_url), 'enctype="multipart/form-data"'
        )
        response = self.client.post(
            self.create_url, {**self.data, "photo": photo()}
        )
        preserve = Preserve.objects.get()
        self.assertRedirects(response, preserve.get_absolute_url())
        self.assertTrue((self.media / preserve.photo.name).is_file())
        self.assertTrue(preserve.photo.name.startswith("preserves/"))
        detail = self.client.get(preserve.get_absolute_url())
        self.assertContains(detail, f'src="{preserve.photo.url}"')

    def test_optional_photo_shows_placeholder(self):
        self.client.post(self.create_url, self.data)
        preserve = Preserve.objects.get()
        self.assertFalse(preserve.photo)
        self.assertContains(
            self.client.get(preserve.get_absolute_url()),
            "Фотография ещё не добавлена.",
        )

    def test_invalid_uploads_produce_errors_without_writing(self):
        invalid = (
            SimpleUploadedFile("fake.png", b"not an image"),
            photo("wrong.jpg"),
            photo(size=(4097, 8)),
            SimpleUploadedFile("big.png", b"x" * (5 * 1024 * 1024 + 1)),
        )
        for upload in invalid:
            response = self.client.post(
                self.create_url, {**self.data, "photo": upload}
            )
            self.assertIn("photo", response.context["form"].errors)
        self.assertFalse(Preserve.objects.exists())
        self.assertEqual(list(self.media.iterdir()), [])

    def test_update_keeps_address_and_can_clear_the_image(self):
        preserve = Preserve.objects.create(
            name=self.data["name"], product=self.product
        )
        address = preserve.get_absolute_url()
        url = reverse("preserves:update", args=[preserve.pk])
        self.assertRedirects(self.client.post(
            url, {**self.data, "name": "Джем", "photo": photo()}
        ), address)
        preserve.refresh_from_db()
        self.assertTrue(preserve.photo)
        self.assertEqual(preserve.get_absolute_url(), address)
        self.assertRedirects(self.client.post(
            url, {**self.data, "photo-clear": "on"}
        ), address)
        preserve.refresh_from_db()
        self.assertFalse(preserve.photo)

    def test_admin_uploads_and_replaces_photo(self):
        preserve = Preserve.objects.create(
            name=self.data["name"], product=self.product
        )
        url = reverse("admin:preserves_preserve_change", args=[preserve.pk])
        fields = {
            **self.data, "slug": preserve.slug, "_save": "1",
            "batches-TOTAL_FORMS": "0", "batches-INITIAL_FORMS": "0",
            "batches-MIN_NUM_FORMS": "0", "batches-MAX_NUM_FORMS": "1000",
        }
        invalid = self.client.post(url, {**fields, "photo": photo("fake.jpg")})
        self.assertIn("photo", invalid.context["adminform"].form.errors)
        paths = []
        for color in ("red", "blue"):
            response = self.client.post(url, {**fields, "photo": photo(
                color=color
            )})
            self.assertEqual(response.status_code, 302)
            preserve.refresh_from_db()
            paths.append(preserve.photo.name)
            self.assertTrue((self.media / paths[-1]).exists())
        self.assertNotEqual(*paths)
        self.assertContains(
            self.client.get(preserve.get_absolute_url()), preserve.photo.url
        )
