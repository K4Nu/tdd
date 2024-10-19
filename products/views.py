import os
from .models import Product,ProductImage,Category
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.shortcuts import redirect
from .forms import ProductForm,CategoryForm
from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import HttpResponse
import datetime
import uuid
from django.views.generic import ListView, DetailView
from django.http import Http404


def index(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/add_product.html'
    success_url = reverse_lazy('index')  # Adjust 'index' to the correct URL name

    def form_valid(self, form):
        # Save the product instance but don't commit to DB yet
        self.object = form.save(commit=False)
        self.object.save()

        # Handle multiple images
        images = self.request.FILES.getlist('images')
        product_name = form.cleaned_data.get("name")
        for i,image in enumerate(images):
            unique_filename = f"{product_name}_{uuid.uuid4().hex[:8]}_{i}{os.path.splitext(image.name)[-1]}"
            img_path = os.path.join("product_images", unique_filename)
            try:
                with Image.open(image) as img:
                    img_content=ContentFile(image.read())
                    saved_img_path=default_storage.save(img_path, img_content)
                    ProductImage.objects.create(product=self.object, image=saved_img_path)
            except Exception as e:
                print(f'Error {image.name} {e}')

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

class Products(ListView):
    pass

class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product.html"

    def get_object(self, *args, **kwargs):
        parent_slug=self.kwargs.get("parent_slug")
        child_slug=self.kwargs.get("child_slug")
        product_id=self.kwargs.get("pk")

        try:
            parent_category=Category(slug=parent_slug, parent__isnull=True)
            child_category=Category(slug=child_slug,parent=parent_category)
            product=Product.objects.get(pk=product_id,category=child_category)

        except Category.DoesNotExist:
            raise Http404("Category not found")

        except Product.DoestNotExist:
            raise Http404("Product not found")

class CreateCategoryView(CreateView):
    model = Category
    form_class = CategoryForm  # Use the form class correctly
    template_name = 'products/create_category.html'  # Make sure you have a template
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        # Get the name of the subcategory from the form
        name = form.cleaned_data.get("name")
        # Get the selected choices (which are parent categories) from the form
        choices = form.cleaned_data.get("choices")
        # For each choice (parent category), create a new subcategory under it
        for choice in choices:
            # Get the parent category by its name
            parent_category = Category.objects.filter(name=choice).first()
            if parent_category:
                # Create the new subcategory under the parent
                Category.objects.create(name=name, parent=parent_category)

        # Redirect to success URL after creating the subcategories
        return redirect(self.success_url)