from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout

# Create your views here.
def user_login(request):
    context = {}
    if request.method=="GET":

        return render(request,'accounts/login.html')
    else:
        
        uname = request.POST['uname']
        upass = request.POST['upass']

        #validations
        if uname =='' or upass == '':
            context['errmsg'] = 'Username or Password cannot be empty'
            return render(request,'accounts/login.html',context)
        else:
            u= authenticate(username = uname, password = upass)
            #print("value",u)
            #print(u.username,u.password)
            if u is not None:
                login(request,u)
                return redirect('/')

            else:
                context['errmsg']= "Invalid username or password"
                return render(request,'accounts/login.html',context)


def user_register(request):
    context = {}
    if request.method=="GET":

        return render(request,'accounts/register.html')
    else:
        #fetch and store form data
        uname = request.POST['uname']
        uemail = request.POST['uemail']
        upass = request.POST['upass']
        ucpass = request.POST['ucpass']

        # validation
        if uname =='' or uemail == '' or upass =='' or ucpass == '':
            context['errmsg'] = "Fields cannot be empty"
            return render(request,'accounts/register.html', context)

        elif upass != ucpass :
            context['errmsg'] = "Password and Confirm Password Missmatch"
            return render(request,'accounts/register.html', context)

        elif len(upass)<8 :
            context['errmsg'] = "Password is less than 8 characters "
            return render(request,'accounts/register.html', context)
            
        elif upass.isdigit():
            context['errmsg'] = "Password should not numeric entirely   "
            return render(request,'accounts/register.html', context)    
        else:
            u = User.objects.create(username = uname, email = uemail )
            u.set_password(upass)
            u.save()
            context['Success'] = "User created successfully"
            return render(request,'accounts/register.html',context)


def user_logout(request):
    logout(request)
    return redirect('/')