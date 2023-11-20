from django.shortcuts import render,redirect,HttpResponse
from productapp.models import Product
from django.db.models import Q
from storeapp.models import Cart,Order
import razorpay
from django.core.mail import send_mail

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
    p = Product.objects.get(id=pid)
    print(p)

    context ={}
    context['product']=p

    return render(request,'storeapp/product_details.html',context)



def about(request):
    return render(request,'storeapp/about.html')

def cart(request):
    #print("Is Logged in",request.user.is_authenticated)
    if request.user.is_authenticated:
        context = {}
        #Fetch all cart product of logged   in user
        # Select * from storeapp_cart where uid = 4
        c = Cart.objects.filter(uid = request.user.id)
        #print(c)
        total = 0
        for x in c:
            total = total+(x.pid.price*x.qty)

        nos = len(c)
        context['n']= nos
        context['amt'] = total
        context['products'] = c
        return render(request,'storeapp/cart.html',context)
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
        context = {}
        user_id = request.user
        product_obj = Product.objects.get(id = prod_id)
        q1 = Q(uid = user_id)
        q2 = Q(pid = prod_id)
        check = Cart.objects.filter(q1 & q2)
        print(check)
        context['product'] = product_obj    
        
        if len(check):
            context['msg1'] = "Product already exist in the cart"
            return render(request,"storeapp/product_details.html",context)

        else:
            c= Cart.objects.create(uid = request.user ,pid =product_obj)
            c.save()
            context['msg2'] = "Product successfully added in cart"
            return render(request,"storeapp/product_details.html",context)

        # c = Cart.objects.create(uid = user_id,pid = product_obj)
        # c.save()
        
    else:
        return redirect('/accountapp/login')

#get quantity change  in the cart item 
def changeqty(request,cid):
    qparam = request.GET['q']
    print(cid)
    print(qparam)
    c = Cart.objects.filter(id = cid)
    print(c)
    print(c[0])
    x= c[0].qty

    #increase/decre
    if qparam == "plus":
        x= x+1
    else:
        if x>1:
            x=x-1

    #update
    c.update(qty=x)
    return redirect('/cart')




def removecart(request,remove_id):
    c=Cart.objects.get(id=remove_id)
   # print(r)
    c.delete()
    return redirect('/cart')


## Order management
import random
def generate_orderId():
    n=random.randrange(1000,9999)
    order_id = n
    o = Order.objects.filter(order_id = order_id)
    if len(o) == 0:
        return order_id
    else:
        generate_orderId() 



def place_order(request):
    context = {}
    if request.user.is_authenticated:

        oid = generate_orderId()
        print(oid)
        c = Cart.objects.filter(uid = request.user.id)
        for x in c:  #[cart : cart object(1)> , cart object (2)]
            o = Order.objects.create(order_id = oid, uid = x.uid, pid = x.pid ,qty = x.qty )
            o.save()
            x.delete()
        

        q1 = Q(uid = request.user.id)
        q2 = Q(is_completed = False)
        o = Order.objects.filter(q1 & q2)

        nos = len(o)
        total = 0
        for x in o:
            total = total + (x.pid.price*x.qty)


        context['orders'] = o
        context['n'] = nos
        context['amt'] = total



        return render(request,'storeapp/place_order.html',context)
    
    else:
        return redirect('accountapp/login')



def cancelOrder(request,rid):
    o = Order.objects.filter(id = rid)
    o.delete()

    oRem = Order.objects.filter(uid = request.user.id)
    context = { 'orders':oRem}
    #return render(request,'storeapp/place_order.html',context)
    return redirect('/cart')


#remove orde

#makepayment
def makepayment(request):
    context = {}
    client = razorpay.Client(auth=("rzp_test_sTaD6TcNmJOUde", "sr7TEqG3Y8C2h7im2GWybzPG"))
    q1 = Q(uid = request.user.id)
    q2 = Q(is_completed = False)
    o = Order.objects.filter(q1 & q2)
    print(o)
    total = 0
    for x in o:
        total = total +(x.pid.price*x.qty)

    famt = total*100
    data = {"amount": famt, "currency": "INR", "receipt": str(o[0].order_id) }
    print(data)
    payment = client.order.create(data=data)
    print(payment)
    context['payment']=payment

    return render(request,'storeapp/pay.html',context)

# to send email in django 
#  
def sendmail(request):
    order_id = request.GET['oid']
    pay_id = request.GET['rpayid']
    # roid = request.GET['roid']

    #update order table  is_completed to 1
    o = Order.objects.filter(order_id = order_id)
    o.update(is_completed = True)

    subject = "Ekart Order has been placed successfully"
    msg = "Your Order details are:  Order_id:"+order_id +"  "+"Payment ID:"+pay_id


    send_mail(
    subject,
    msg,
    "anandbhere46@gmail.com",
    ["harshvishe1418@gmail.com"],
    # [request.user.email],
    fail_silently=False,
    )

    return HttpResponse("send mail ,Successfully paid payment add updated cart by setting is_completed to 1")


#hxop ltcq hywk xjex


