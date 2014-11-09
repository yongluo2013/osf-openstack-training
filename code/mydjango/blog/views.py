from django.shortcuts import render_to_response 
from django.template import Context,loader
# Create your views here.
from django.http import HttpResponse
from django.forms import Form
from django.forms import CharField
from django.forms import IntegerField
# def index(req,id):
#     print id
#     return HttpResponse("<h1>helloword!</h1>")

# def index(req):
#     user = {"name":"jack","age":30}
#     t = loader.get_template("index.html")
#     c = Context({"user":user})
#     return HttpResponse(t.render(c))

def index(req):
    user = {"name":"jack","age":30}
    return render_to_response("index.html",{"user":user})

class UserForm(Form):
    
    name = CharField()
    age = IntegerField()

def regester(req):
    if req.method == "POST":
        user_form = UserForm(req.POST)
        if user_form.is_valid():
            print user_form.cleaned_data
            return HttpResponse("ok")
    else:
        user_form  = UserForm()
        return render_to_response("regester.html",{"user_form":user_form})
    
