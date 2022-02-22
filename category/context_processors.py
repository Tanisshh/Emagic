from .models import Category

# for accessing all catagory in entire project

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)
