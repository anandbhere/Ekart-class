from django.shortcuts import render,redirect,HttpResponse
from productapp.models import Product
from django.db.models import Q
from storeapp.models import Cart
# Create your views here.
'''
views provise response to client by using:
1) HttpResponse()
2) render(request,'filename.html',data)
'''
def homepage(request):
    #return HttpResponse('Hello from Home Page')
    context={}
    context['msg']="Hello all, Good Morning!!!"
    context['x']=1000
    context['y']=200
    context['data']=[10,20,30,40,50,60]
    return render(request,'storeapp/home.html',context)

# def contactpage(request):
#     return HttpResponse('Hello from Contact Page')

# def aboutpage(request):
#     return HttpResponse('Hello from About Page')

# def edit(request,id):
#     print("ID to be edited:",id)
#     return HttpResponse("ID to be updated:"+id)

# def delete(request,id):
#     print("ID to be Delete:",id)
#     return HttpResponse("ID to be deleted:"+id)

# def addition(request,x,y):
#     res=int(x)+int(y)
#     print ("Addition is:",res)
#     return HttpResponse("Addition is:"+str(res))

def home(request):
#fetch available products from database
    p=Product.objects.filter(is_available=True)
    print(p)
    context={}
    context['pdata']=p
    return render(request,'storeapp/index.html',context)

def product_details(request,pid):
    #fetch p details with id
    p= Product.objects.get(id=pid)
    print(p)

    context ={}
    context['product']=p

    return render(request,'storeapp/product_details.html',context)

def place_order(request):
    if request.user.is_authenticated:
        return render(request,'storeapp/place_order.html')
    else:
        return redirect('accountapp/login')


    return render(request,'storeapp/place_order.html')

def about(request):
    return render(request,'storeapp/about.html')

def cart(request):
    print("Is Logged in",request.user.is_authenticated)
    if request.user.is_authenticated:
        return render(request,'storeapp/cart.html')
    else:
        return redirect('accountapp/login')

def contact(request):
    return render(request,'storeapp/contact.html')

def cat_filter(request,catv):
    #print(catv)
    q1 = Q(cat=catv) 
    q2 = Q(is_available=True)
    p=Product.objects.filter(q1 & q2)
    context={}
    context['pdata']=p
    return render(request,'storeapp/index.html',context)

def pricerange(request):
    context = {}
    
    min =(request.GET['min'])
    max =(request.GET['max'])

    #print(min)
    #print(max)
    if not min.isdigit() or not max.isdigit():
        context['errmsg']="Price must be in digit"
        return render(request,'storeapp/index.html',context)

    elif int(min)<0 or int(max)<0:
        context['errmsg']="Price cannot be negative"
        return render(request,'storeapp/index.html',context)
    
    elif int(min)>int(max):
        context['errmsg']="Minimum price cannot be greater than max "
        return render(request,'storeapp/index.html',context)
    else:
        min = int (min)
        max = int (max)
        q1 = Q(price__gte = min )
        q2 = Q(price__lte = max )
        q3 = Q(is_available = True)

        p = Product.objects.filter(q1 & q2 & q3)
        context = {}
        context['pdata'] = p
        return render(request,'storeapp/index.html',context)

   

def sort(request):
    context = {}
    qpara = request.GET['q']
    #print(qpara)

    if qpara == "asc":
        #p = Product.objects.order_by('price').filter(is_available=True)
        x = "price"
    else:
        #p = Product.objects.order_by('-price').filter(is_available=True)
        x = "-price"
    p = Product.objects.order_by(x).filter(is_available=True)
    context['pdata'] = p
    return render(request,'storeapp/index.html',context)


def search(request):

    context = {}
    para =  request.GET['search']

    q1 = Q(name__icontains = para)
    q2 = Q(pdetails__icontains = para)

    p = Product.objects.filter(q1 | q2)

    context['pdata'] = p
    return render(request,'storeapp/index.html',context)


#cart Functionality

def addTo_cart(request,prod_id):
    if request.user.is_authenticated:
        print(prod_id)
        user_id = request.user
        product_obj = Product.objects.get(id = prod_id)
        c = Cart.objects.create(uid = user_id,pid = product_obj)
        c.save()
        return HttpResponse("Product added successfullly")
    else:
        return redirect('/accountapp/login')