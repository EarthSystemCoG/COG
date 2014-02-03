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
from django.views.decorators.http import require_GET, require_POST

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
        item = DataCartItem(cart=datacart, identifier=id, name=name, type=type)
        item.save()
        
        # save additional metadata
        if metadata is not None:
            metadata = simplejson.loads(metadata)
            
            for key, values in metadata.items():
                itemKey = DataCartItemMetadataKey(item=item, key=key)
                itemKey.save()
                for value in values:
                    itemValue = DataCartItemMetadataValue(key=itemKey, value=value)
                    itemValue.save()
                    #print ('saved key=%s value=%s' % (itemKey.key, itemValue.value))

    # return new number of items in cart
    response_data['datacart_size'] = len( datacart.items.all() )
    
    return HttpResponse(simplejson.dumps(response_data), mimetype='application/json') 
    
# view to add an item to a user data cart
@login_required
@require_POST
@csrf_exempt
def datacart_delete(request, site_id, user_id):
        
    # check User object
    user = get_object_or_404(User, pk=user_id)
    
    # security check
    if not request.user.id != user_id:
        raise Exception("User not authorized to modify datacart")
    
    # TODO:: check site, redirect in case
    item_id = request.POST['item']
    
    # NOTE: make sure this item belongs to the user's data cart
    datacart = DataCart.objects.get(user=user)
    
    item = DataCartItem.objects.get(id=item_id, cart=datacart)
    item.delete()
    
    # return new number of items in cart
    response_data = {}    
    # return id of item just deleted so it can be hidden
    response_data['item_id'] = item_id
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


'''
def _isValid(field, value, response_data):
     
    if re.search(INVALID_CHARS, value):
        response_data['error'] = "Field: '%s' contains invalid characters: '%s'" % (field, value)
        return False
    else:
        return True
'''