from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from core.models import User, Host, Storage, GraphLib, Group


class Group_Form(forms.ModelForm):
    """
    """
    class Meta:
        model = Group
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name'),'class':'span6'}),
        }

    def get_absolute_url(self):
        return reverse('group', args=[str(self.instance.id)])

    def get_add_url(self):
        return reverse('group add')

    def get_list_url(self):
        return reverse('group list')

    def get_update_url(self):
        if not self.instance.id:
            return self.get_add_url()
        return reverse('group update', args=[str(self.instance.id)])

    def get_delete_url(self):
        return reverse('group delete', args=[str(self.instance.id)])


class User_Form(forms.ModelForm):
    """
    Base User Form. Subclassed for make custom User Form.
    """
    class Meta:
        model = User
        fields = ('username','email','graph_lib','is_superuser','groups')
        widgets = {
            'username': forms.TextInput({'placeholder':_('Username'),'class':'span6'}),
            'email': forms.TextInput({'placeholder':_('Email'),'class':'span6'}),
            'password': forms.PasswordInput({'placeholder':_('Password'),'class':'span6'}),
            'graph_lib': forms.SelectMultiple({'class':'span6'}),
            'groups': forms.SelectMultiple({'class':'span6'}),
        }


class User_Admin_EditForm(User_Form):
    """
    Form with sensitive fields.
    """
    class Meta(User_Form.Meta):
        exclude = ('password','last_login','is_staff','date_joined')


class User_CreationForm(User_Form):
    """
    Form with sensitive fields.
    """
    class Meta(User_Form.Meta):
        exclude = ('last_login','is_staff','date_joined','is_active')


class User_EditForm(User_Admin_EditForm):
    """
    Form with fewer fields.
    """
    class Meta(User_Form.Meta):
        fields = ('username','email','graph_lib')


class User_PasswordForm(User_Form):
    """
    Form for change password.
    """
    old = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'placeholder':_('Old password')}))
    new_1 = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'placeholder':_('New password')}))
    new_2 = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'placeholder':_('Confirmation')}))

    class Meta(User_Form.Meta):
        model = User
        fields = ()
    
    def is_valid(self):
        if not self.instance.check_password(self.data['old']):
            self.errors['old'] = _('Bad old password')
        if self.data['new_1'] != self.data['new_2']:
            self.errors['new'] = _('Password and confirmation are not same')
        if self.errors:
            return False
        return True

    def save(self, *args, **kwargs):
        self.instance.set_password(self.data['new_1'])
        self.instance.save()
        return self.instance


class Storage_Form(forms.ModelForm):
    """
    Basic Storage ModelForm.
    """
    class Meta:
        model = Storage
        widgets = {
            'name': forms.TextInput({'placeholder':_('Name')}),
            'address': forms.TextInput({'placeholder':_('Address')}),
            'port': forms.TextInput({'placeholder':_('Port')}),
            'port': forms.TextInput({'placeholder':_('Port')}),
            'url_prefix': forms.TextInput({'placeholder':_('URL prefix')}),
            'login': forms.TextInput({'placeholder':_('Login')}),
            'password': forms.TextInput({'placeholder':_('Password')}),
        }


class GraphLib_Form(forms.ModelForm):
    """
    Basic GraphLib ModelForm.
    """
    class Meta:
        model = GraphLib
        widgets = {
            'name': forms.TextInput({'placeholder':_("Library's name")}),
        }


class Host_Form(forms.ModelForm):
    """
    Basic Host ModelForm.
    """
    class Meta:
        model = Host
        widgets = {
            'name': forms.TextInput({'placeholder':_("Host's name")}),
            'hostID': forms.TextInput({'placeholder':'ID'}),
        }
