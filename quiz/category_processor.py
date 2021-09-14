'''----category context processor--- '''
from .models import Category
from functools import lru_cache


def category_list(request):
    ''' shows a list of categories available 
        context processor
    '''
    @lru_cache(maxsize=80)
    def cat():
        cat_items = Category.objects.all()
        return cat_items
    
    cat_items = cat()
    #print(cat_items)
    

    return { 'cat_items': cat_items }
