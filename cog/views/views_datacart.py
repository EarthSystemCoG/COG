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
from cog.views.views_search import SEARCH_DATA, SEARCH_OUTPUT
from django.core.exceptions import ObjectDoesNotExist


INVALID_CHARS = "[<>&#%{}\[\]\$]"

# view to display the data cart for a given site, user
@require_GET
@login_required
def datacart_display(request, site_id, user_id):
    
    # TODO:: check site, redirect in case
    
    # load User object
    user = get_object_or_404(User, pk=user_id)
    try:
        datacart = DataCart.objects.get(user=user)
    except DataCart.DoesNotExist:
        datacart = None
        
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
    identifier = request.POST['id']
    metadata = request.POST['metadata']
    #print 'JSON METADATA=%s' % metadata
    
    # check item is not in cart already
    items = DataCartItem.objects.filter(cart=datacart, identifier=identifier)
    if len(items.all()) > 0:
        response_data['message'] = 'This item is already in the Data Cart'
        
    else:
        # add item to the cart
        item = DataCartItem.fromJson(datacart, identifier, metadata)

    # return new number of items in cart
    response_data['datacart_size'] = len( datacart.items.all() )
    # return identifier of newly added datcart item
    response_data['item'] = identifier
    
    return HttpResponse(simplejson.dumps(response_data), mimetype='application/json') 

# view to add ALL current search results (as displayed in the page) to the user data cart
@login_required
@require_GET
def datacart_add_all(request, site_id, user_id):
    
    # load User object
    user = get_object_or_404(User, pk=user_id)
    try:
        datacart = DataCart.objects.get(user=user)
    except DataCart.DoesNotExist:
        datacart = None
    
    # security check
    if not request.user.id != user_id:
        raise Exception("User not authorized to modify datacart")
    
    # retrieve results from session
    data = request.session.get(SEARCH_DATA, None)
    if data is not None:
        searchOutput = data[SEARCH_OUTPUT]
        
        # loop over record
        print "Adding %s items" % len(searchOutput.results)
        for record in searchOutput.results:
            
            # check item is not in cart already
            if DataCartItem.objects.filter(cart=datacart, identifier=record.id).exists():
                print 'Item %s already in Data Cart' % record.id
            else:
                item = DataCartItem.fromRecord(datacart, record)
                print 'Added item: %s' % record.id

    # redirect to search results
    back = request.GET.get('back','/')
    return HttpResponseRedirect( back )

# view to delete ALL current search results (as displayed in the page) from the user data cart
@login_required
@require_GET
def datacart_delete_all(request, site_id, user_id):
    
    # load User object
    user = get_object_or_404(User, pk=user_id)

    try:
        datacart = DataCart.objects.get(user=user)
    except DataCart.DoesNotExist:
        datacart = None

    # security check
    if not request.user.id != user_id:
        raise Exception("User not authorized to modify datacart")
    
    # retrieve results from session
    data = request.session.get(SEARCH_DATA, None)
    if data is not None:
        searchOutput = data[SEARCH_OUTPUT]
        
        # loop over record
        print "Deleting %s items" % len(searchOutput.results)
        for record in searchOutput.results:
            
            try:
                item = DataCartItem.objects.get(cart=datacart, identifier=record.id)
                print 'Deleting item: %s' % item.id
                item.delete()
            except ObjectDoesNotExist:
                pass
            
    # redirect to search results
    back = request.GET.get('back','/')
    return HttpResponseRedirect( back )


# view to generate wget URLS for all selected datacart items
# can be invoked either through GET or POST requests
# NOTE: no CSRF token required, but request must be authenticated
@login_required
@require_http_methods(["GET", "POST"])
#@require_POST
@csrf_exempt
def datacart_wget(request, site_id, user_id):
    
    # load User object
    user = get_object_or_404(User, pk=user_id)
    
    # security check
    if not request.user.id != user_id:
        raise Exception("User not authorized to use datacart")
    
    # retrieve list of selected dataset ids
    ids = request.REQUEST.getlist('id')
    
    # map of dataset ids grouped by index node 
    response_data = {}
    
    # loop over datacart items
    try:
        datacart = DataCart.objects.get(user=user)
    except DataCart.DoesNotExist:
        datacart = None

    if datacart:
        for item in datacart.items.all():

            # filter selected datasets only
            if item.identifier in ids:

                # group selected dataset by index_node
                index_node = item.getValue('index_node')
                if index_node not in response_data:
                    response_data[index_node] = []
                response_data[index_node].append(item.identifier)
    
    '''
    Example response_data:
    {
       u'pcmdi9.llnl.gov':[
          u'cmip5.output1.INM.inmcm4.1pctCO2.day.atmos.day.r1i1p1.v20110323|pcmdi9.llnl.gov',
          u'cmip5.output1.INM.inmcm4.esmHistorical.fx.atmos.fx.r0i0p0.v20110927|pcmdi9.llnl.gov',
          u'cmip5.output1.INM.inmcm4.1pctCO2.day.ocean.day.r1i1p1.v20110323|pcmdi9.llnl.gov'
       ]
    }
    '''
    return HttpResponse(simplejson.dumps(response_data), mimetype='application/json') 
    
# view to delete an item to a user data cart
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
    identifier = request.REQUEST['item']
    
    # NOTE: make sure this item belongs to the user's data cart
    try:
        datacart = DataCart.objects.get(user=user)
    except DataCart.DoesNotExist:
        datacart = None

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
    try:
        datacart = DataCart.objects.get(user=user)
    except DataCart.DoesNotExist:
        datacart = None
    
    # delete all items associated with user data cart
    DataCartItem.objects.filter(cart=datacart).delete()
    
    return HttpResponseRedirect(reverse('datacart_display', args=[site_id, user_id]))