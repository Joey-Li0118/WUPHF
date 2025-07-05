from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import User #makes a user 
from .utils import notify


class WuphfReceiver(models.Model):
    name = models.CharField(max_length=50)
    sms = models.CharField(max_length=20, null=True, blank=True)
    facebook = models.CharField(max_length=100, null=True, blank=True)
    twitter = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length = 100, null = True, blank = True)
    def __str__(self):
        return self.name # returns the name of who received the wuphf
    def socials(self):
        return [self.sms, self.facebook, self.twitter, self.email]
    # Receivers: [Dwight, Jim, Pam]

class Wuphf(models.Model):
    sender = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "sendingnotif")
    #For example, if a Pizza has multiple Topping objects – that is, a 
    #Topping can be on multiple pizzas and each Pizza has multiple toppings – here’s how you’d represent that:
    receivers = models.ManyToManyField(WuphfReceiver) 
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        listofreceiver = ", ".join([receiver.email for receiver in self.receivers.all() if receiver.email])
        return f"{self.sender.username} - {self.message[:50]} - {listofreceiver}" 
    
    def send_wuphf(self):
        for receiver in self.receivers.all():  # Get all related receivers
            if receiver.email:
                notify.sendEmail(receiver.email, self.message)  # Access email field of each receiver
            if receiver.sms:
                print("phone_message...")
            if receiver.facebook:
                print("Facebook messaging...")
            if receiver.twitter:
                print("tweeting...")
                #notify.sendTweet()



class Socials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="social_account")
    facebook = models.CharField(max_length=100, null=True, blank=True)
    twitter = models.CharField(max_length=100, null=True, blank=True)
    



#     question_text = models.CharField(max_length=200) #database column name
#     pub_date = models.DateTimeField("date published") #database column name
#     def __str__(self):
#         return self.question_text
#     def was_published_recently(self):
#         return self.pub_date >= timezone.now() - datetime.timedelta(days=1)





# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete = models.CASCADE) #tells database that each choice related to a single question...supports 1-1 x-1 x-x
#     choice_text = models.CharField(max_length = 200)
#     votes = models.IntegerField(default= 0)
#     def __str__(self):
#         return self.choice_text
    




# >>> from polls.models import Choice, Question

# # Make sure our __str__() addition worked.
# >>> Question.objects.all()
# <QuerySet [<Question: What's up?>]>

# # Django provides a rich database lookup API that's entirely driven by
# # keyword arguments.
# >>> Question.objects.filter(id=1)
# <QuerySet [<Question: What's up?>]>
# >>> Question.objects.filter(question_text__startswith="What")
# <QuerySet [<Question: What's up?>]>

# # Get the question that was published this year.
# >>> from django.utils import timezone
# >>> current_year = timezone.now().year
# >>> Question.objects.get(pub_date__year=current_year)
# <Question: What's up?>

# # Request an ID that doesn't exist, this will raise an exception.
# >>> Question.objects.get(id=2)
# Traceback (most recent call last):
#     ...
# DoesNotExist: Question matching query does not exist.

# # Lookup by a primary key is the most common case, so Django provides a
# # shortcut for primary-key exact lookups.
# # The following is identical to Question.objects.get(id=1).
# >>> Question.objects.get(pk=1)
# <Question: What's up?>

# # Make sure our custom method worked.
# >>> q = Question.objects.get(pk=1)
# >>> q.was_published_recently()
# True

# # Give the Question a couple of Choices. The create call constructs a new
# # Choice object, does the INSERT statement, adds the choice to the set
# # of available choices and returns the new Choice object. Django creates
# # a set (defined as "choice_set") to hold the "other side" of a ForeignKey
# # relation (e.g. a question's choice) which can be accessed via the API.
# >>> q = Question.objects.get(pk=1)

# # Display any choices from the related object set -- none so far.
# >>> q.choice_set.all()
# <QuerySet []>

# # Create three choices.
# >>> q.choice_set.create(choice_text="Not much", votes=0)
# <Choice: Not much>
# >>> q.choice_set.create(choice_text="The sky", votes=0)
# <Choice: The sky>
# >>> c = q.choice_set.create(choice_text="Just hacking again", votes=0)

# # Choice objects have API access to their related Question objects.
# >>> c.question
# <Question: What's up?>

# # And vice versa: Question objects get access to Choice objects.
# >>> q.choice_set.all()
# <QuerySet [<Choice: Not much>, <Choice: The sky>, <Choice: Just hacking again>]>
# >>> q.choice_set.count()
# 3

# # The API automatically follows relationships as far as you need.
# # Use double underscores to separate relationships.
# # This works as many levels deep as you want; there's no limit.
# # Find all Choices for any question whose pub_date is in this year
# # (reusing the 'current_year' variable we created above).
# >>> Choice.objects.filter(question__pub_date__year=current_year)
# <QuerySet [<Choice: Not much>, <Choice: The sky>, <Choice: Just hacking again>]>

# # Let's delete one of the choices. Use delete() for that.
# >>> c = q.choice_set.filter(choice_text__startswith="Just hacking")
# >>> c.delete()