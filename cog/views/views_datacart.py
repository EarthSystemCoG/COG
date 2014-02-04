from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.core.urlresolvers import reverse
from cog.models import *
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
import re
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.views.decorators.http import require_GET, require_POST, require_http_methods

INVALID_CHARS = "[<>&#%{}\[\]\$]"

# view to display the data cart for a given site, user
@require_GET
def datacart_display(request, site_id, user_id):
    
    # TODO:: check site, redirect in case
    
    # load User object
    user = get_object_or_404(User, pk=user_id)
    
    datacart = DataCart.objects.get(user=user)
        
    return render_to_response('cog/datacart/datacart.html', { 'datacart': datacart }, context_instance=RequestContext(request))    
    
# view to add an item to a user data cart
# NOTE: no CSRF token required, but request must be authenticated
@login_required
@require_POST
@csrf_exempt
def datacart_add(request, site_id, user_id):
        
    # load User object
    user = get_object_or_404(User, pk=user_id)
    
    # security check
    if not request.user.id != user_id:
        raise Exception("User not authorized to modify datacart")
        
    datacart = DataCart.objects.get(user=user)
    
    response_data = {}

    # retrieve data item attributes from request
    id = request.POST['id']
    name = request.POST['name']
    type = request.POST['type']
    metadata = request.POST['metadata']
    #print 'JSON METADATA=%s' % metadata
    
    # check item is not in cart already
    items = DataCartItem.objects.filter(cart=datacart, identifier=id)
    if len(items.all()) > 0:
        response_data['message'] = 'This item is already in the Data Cart'
        
    else:
        # add item to the cart
        item = DataCartItem.fromJson(datacart, id, name, type, metadata)

    # return new number of items in cart
    response_data['datacart_size'] = len( datacart.items.all() )
    
    return HttpResponse(simplejson.dumps(response_data), mimetype='application/json') 
    
# view to delete an item to a user data cart
@login_required
#@require_http_methods(["GET", "POST"])
@require_POST
@csrf_exempt
def datacart_delete(request, site_id, user_id):
        
    # check User object
    user = get_object_or_404(User, pk=user_id)
    
    # security check
    if not request.user.id != user_id:
        raise Exception("User not authorized to modify datacart")
    
    # TODO:: check site, redirect in case
    identifier = request.REQUEST['item']
    
    # NOTE: make sure this item belongs to the user's data cart
    datacart = DataCart.objects.get(user=user)
    
    item = DataCartItem.objects.get(identifier=identifier, cart=datacart)
    item.delete()
    
    # return new number of items in cart
    response_data = {}    
    # return id of item just deleted so it can be hidden
    response_data['item'] = identifier
    # return number of remaining items
    response_data['datacart_size'] = len( user.datacart.items.all() )
        
    return HttpResponse(simplejson.dumps(response_data), mimetype='application/json') 

# view to completely empty a user data cart
# NOTE: no CSRF token required, but request must be authenticated
@login_required
@require_POST
@csrf_exempt
def datacart_empty(request, site_id, user_id):
    
    # check User object
    user = get_object_or_404(User, pk=user_id)
    
    # security check
    if not request.user.id != user_id:
        raise Exception("User not authorized to modify datacart")

    # user data cart    
    datacart = DataCart.objects.get(user=user)
    
    # delete all items associated with user data cart
    DataCartItem.objects.filter(cart=datacart).delete()
    
    return HttpResponseRedirect(reverse('datacart_display', args=[site_id, user_id]))