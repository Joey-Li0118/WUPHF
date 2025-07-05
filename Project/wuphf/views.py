from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from.models import Wuphf, WuphfReceiver
from django.http import JsonResponse
from django.template import loader
from django.http import Http404
from django.views import View

class home(View):
    template_name = "wuphf/home.html"

    def get(self, request, *args, **kwargs):
        #output = ", ".join([q.question_text for q in latest_question_list]) this is for a completely static view
        context = { 
            "receivers": WuphfReceiver.objects.all(),
        }
        return render(request, self.template_name, context) #if i don't add dictionary, the html breaks


    def post(self, request, *args, **kwargs):
    # Take the form input and use it to send the wuphf
        sender = request.user
        receiver_id = request.POST.getlist('receiver')
        receivers = WuphfReceiver.objects.filter(id__in=receiver_id)  # Fetch objects
        message = str(request.POST.get('message'))[:99]
        self.send(sender, message, receivers)     
        return redirect('sent')

    # With this function, it would overwrite the above detail function
    # def detail(request, question_id):
    #     return HttpResponse(f"You're looking at question {question_id}.")

    def send(self, sender, message, receiver):
        wuphfie = Wuphf.objects.create(sender = sender, message = message)
        # wuphfie.add_to_class(field) adds a temporary field that doesn't modify the model itself
        wuphfie.receivers.add(*receiver)
        wuphfie.send_wuphf()
        
    

#/vote/42/some-text/
#vote(request, question_id=42, extra_string="some-text")

