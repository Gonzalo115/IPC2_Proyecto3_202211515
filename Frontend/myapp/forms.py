from django import forms


class addForm(forms.Form):
    nombre= forms.CharField(label="nombre", max_length=100)
    email= forms.CharField(label="email", max_length=100)
    alias= forms.CharField(label="alias", max_length=100)