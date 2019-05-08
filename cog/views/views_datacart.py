from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from cog.models import *
from django.contrib.auth.decorators import login_required
import re
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from cog.views.views_search import SEARCH_DATA, SEARCH_OUTPUT
from django.core.exceptions import ObjectDoesNotExist
from django_openid_auth.models import UserOpenID
from cog.views.utils import getQueryDict
from cog.site_manager import siteManager

try:
    import esgfpid
except ImportError:
    pass

INVALID_CHARS = "[<>&#%{}\[\]\$]"


# view to display the data cart for a given node, user
@require_GET
@login_required
def datacart_display(request, site_id, user_id):
        
    # load User object
    user = get_object_or_404(User, pk=user_id)
    # security checl
    if user != request.user:
        return HttpResponseForbidden("Un-authorized attempt to access another user datacart!")
    try:
        datacart = DataCart.objects.get(user=user)
    except DataCart.DoesNotExist:
        datacart = None

    return render(request,
                  'cog/datacart/datacart.html', 
                  {'datacart': datacart})    
    

# view to display a user datacart by openid
@require_GET
@login_required
def datacart_byopenid(request):
    
    if request.method == 'GET':
    
        openid = request.GET['openid']
        
        # load User object
        userOpenid = get_object_or_404(UserOpenID, claimed_id=openid)
        
        # redirect to user profile page on local node
        return HttpResponseRedirect(reverse('datacart_display', 
                                    kwargs={'site_id': Site.objects.get_current().id, 'user_id': userOpenid.user.id}))
            
    else:
        return HttpResponseNotAllowed(['GET'])
    

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
    response_data['datacart_size'] = len(datacart.items.all())
    # return identifier of newly added datcart item
    response_data['item'] = identifier
    
    return HttpResponse(json.dumps(response_data), content_type='application/json') 


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
    back = request.GET.get('back', '/')
    return HttpResponseRedirect(back)


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
    back = request.GET.get('back', '/')
    return HttpResponseRedirect(back)


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
    queryDict = getQueryDict(request)
    ids = queryDict.getlist('id')
        
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
                wget_key = index_node
                shard = item.getValue('shard')
                if shard is not None and len(shard.strip())>0:
                    wget_key += "|" + shard
                if wget_key not in response_data:
                    response_data[wget_key] = []
                response_data[wget_key].append(item.identifier)
    
    '''
    Example response_data:
    {
        u'esgf-node.jpl.nasa.gov|localhost:8982': [u'CMAC.NASA-GSFC.AIRS.mon.v1|esg-datanode.jpl.nasa.gov'], 
        u'esgf-node.jpl.nasa.gov': [u'obs4MIPs.NASA-JPL.QuikSCAT.mon.v1|esgf-node.jpl.nasa.gov'],
        u'pcmdi9.llnl.gov':
            [
              u'cmip5.output1.INM.inmcm4.1pctCO2.day.atmos.day.r1i1p1.v20110323|pcmdi9.llnl.gov',
              u'cmip5.output1.INM.inmcm4.esmHistorical.fx.atmos.fx.r0i0p0.v20110927|pcmdi9.llnl.gov',
              u'cmip5.output1.INM.inmcm4.1pctCO2.day.ocean.day.r1i1p1.v20110323|pcmdi9.llnl.gov'
           ]
    }
    '''
    return HttpResponse(json.dumps(response_data), content_type='application/json') 
    

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
    
    # TODO:: check node, redirect in case
    identifier = request.POST['item']
    
    # NOTE: make sure this item belongs to the user's data cart
    (datacart, _) = DataCart.objects.get_or_create(user=user)

    item = DataCartItem.objects.get(identifier=identifier, cart=datacart)
    item.delete()
    
    # return new number of items in cart
    response_data = {}    
    # return id of item just deleted so it can be hidden
    response_data['item'] = identifier
    # return number of remaining items
    response_data['datacart_size'] = len(datacart.items.all())
        
    return HttpResponse(json.dumps(response_data), content_type='application/json') 


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


# view to generate a collection PID for the selected items in the data cart
@login_required
@require_POST
@csrf_exempt
def datacart_pid(request, site_id, user_id):

    # check User object
    user = get_object_or_404(User, pk=user_id)

    # security check
    if not request.user.id != user_id:
        raise Exception("User not authorized to modify datacart")

    pid_messaging_service_credentials = []
    priority = 1
    for cred in settings.PID_CREDENTIALS:
        parts = cred.split('|')

        if len(parts) == 6:

            ssl_enabled = False
            if parts[5].strip().upper() == 'TRUE':
                ssl_enabled = True

            pid_messaging_service_credentials.append({'url': parts[0].strip(),
                                                      'port': parts[1].strip(),
                                                      'vhost': parts[2].strip(),
                                                      'user': parts[3].strip(),
                                                      'password': parts[4].strip(),
                                                      'ssl_enabled': ssl_enabled,
                                                      'priority': priority})
            priority += 1

    # get list of dataset_pids and dataset_ids
    try:
        datacart = DataCart.objects.get(user=user)
    except DataCart.DoesNotExist:
        datacart = None

    queryDict = getQueryDict(request)
    ids = queryDict.getlist('id')

    dataset_ids = {}
    if datacart:
        for item in datacart.items.all():
            # filter selected datasets only
            if item.identifier in ids:
                dataset_ids[item.identifier.split('|')[0]] = item.getValue('pid')

    # call PID library to generate collection PID
    connector = esgfpid.Connector(handle_prefix=settings.PID_PREFIX,
                                  messaging_service_exchange_name=settings.PID_MESSAGING_SERVICE_EXCHANGE,
                                  messaging_service_credentials=pid_messaging_service_credentials,
                                  )

    connector.start_messaging_thread()
    pid = connector.create_data_cart_pid(dataset_ids)
    connector.finish_messaging_thread()

    print 'Generated data cart PID for %d datasets: %s' % (len(ids), pid)

    return HttpResponse(json.dumps(pid), content_type="application/json")
