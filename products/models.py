from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    name=models.CharField(max_length=255)
    slug=models.CharField(max_length=255)
    parent=models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    class Meta:
        verbose_name_plural="Categories"
        constraints = [
            models.UniqueConstraint(fields=['slug', 'parent'], name='unique_slug_per_parent')
        ]
        ordering=["name"]

    def __str__(self):
        # Display as "Parent > Child" if it has a parent
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("category_detail", args=[self.slug])

class Product(models.Model):
    """Text choices can only have 2 values"""

    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        CHILD_BOY = "B", "Child Boy"
        CHILD_GIRL = "G", "Child Girl"
        OTHER = "O", "Other"

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.OTHER)
    size = models.CharField(max_length=3, blank=True)
    color = models.CharField(max_length=80)
    description = models.CharField(max_length=500)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    available=models.BooleanField(default=True)

    def change_stock(self, quantity):
        self.stock += quantity
        if self.stock <= 0:
            self.stock = 0  # Ensures stock doesn't go below 0
            self.available = False
        else:
            self.available = True  # Automatically set available to True if stock is positive

    def __str__(self):
        return f"{self.name} - {self.gender} - {self.size}"

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.category.parent.slug, self.category.child_slug, self.pk])

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"

