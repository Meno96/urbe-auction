from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django_nextjs.render import render_nextjs_page_sync
from pinata import Pinata
from decouple import config
import os
from .forms import AddUriToArray
import requests
import json
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connections
from .models import EndAuction, IpAddress
from django.core.cache import caches
from .decorators import only_staff
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

# Return actual IP
@csrf_exempt
def getActualIP(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Create IP object with actual date
@csrf_exempt
def addIp(actualIp):
    ipAddress = IpAddress(
        ipAddress=actualIp, pubDate=datetime.now())
    ipAddress.save()

@api_view(['GET'])
def userInfo(request):
    user = request.user
    if user is not None:
        isStaff = user.is_staff

        # Stores the last IP that have logged in to the platform as admin, shows a warning 
        # message when this is different from the previous one
        checkIp = None
        if request.user.is_staff:
            dbIp = IpAddress.objects.all().values().last()
            actualIp = getActualIP(request)

            if not dbIp:
                addIp(actualIp)
            else:
                if actualIp != dbIp['ipAddress']:
                    addIp(actualIp)
                    checkIp = True

        data = {
            'username': user.username,
            'isStaff': isStaff,
            'checkIp': checkIp,
        }

        return Response(data)

@api_view(['GET'])
def fetchTxHash(request):
    tokenId = request.META.get('HTTP_TOKENID')
    try:
        txHash = EndAuction.objects.get(nftId=tokenId).txHash
    except EndAuction.DoesNotExist:
        return Response({'error': 'No element found for tokenId'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'txHash': txHash})

@login_required(login_url='accounts:sign-in')
@csrf_exempt
def homePageView(request):    
    if request.method == 'POST':
        if os.getenv('REDIS_URL'):
            nftId = request.POST.get('nftId')
            bidder = request.POST.get('bidder')
            bidPrice = request.POST.get('bidPrice')
            
            cache = caches['auctions']

            all_bids = cache.get(nftId) or {}

            # aggiunge la nuova puntata alla lista delle puntate
            bid = {'bidder': bidder, 'bidPrice': bidPrice}
            all_bids.setdefault('bids', []).append(bid)

            # salva il dizionario di tutte le puntate per l'oggetto
            cache.set(nftId, all_bids, None)

            allBids = cache.get(nftId) or {}
            bidsList = allBids.get('bids', [])
            
            return HttpResponse()
        
    return render_nextjs_page_sync(request)

@csrf_exempt
def addNft(request):
    if request.method == 'POST':
        form = AddUriToArray(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            image = form.cleaned_data.get('image')
            image_name = image.name.replace(".png", "")

            pinataApiKey = config('PINATA_API_KEY')
            pinataApiSecret = config('PINATA_API_SECRET')

            pinata_url = 'https://api.pinata.cloud/pinning/pinFileToIPFS'
            headers = {
                'pinata_api_key': pinataApiKey,
                'pinata_secret_api_key': pinataApiSecret,
            }
            data = {
                'pinataOptions': json.dumps({
                    'cidVersion': 0
                })
            }
            files = {
                'file': (image_name, image.read())
            }
            response = requests.post(pinata_url, headers=headers, data=data, files=files)

            responseJson = response.json()
            ipfsHash = responseJson['IpfsHash']

            tokenUriMetadata = {
                'name': name,
                'image': f"ipfs://{ipfsHash}",
            }

            metadataUploadUrl = 'https://api.pinata.cloud/pinning/pinJSONToIPFS'
            metadataFileName = f"{image_name}_metadata.json" 
            data = {
                'pinataOptions': '{"cidVersion":1}',
                'pinataContent': tokenUriMetadata,
                'pinataMetadata': {'name': metadataFileName}
            }


            response = requests.post(metadataUploadUrl, headers=headers, json=data)

            responseJson = response.json()
            tokenUri = responseJson['IpfsHash']
            tokenUri = f"ipfs://{tokenUri}"

            # Render a response to show the uploaded token URI
            jsonTokenUri = {'tokenUri': tokenUri}
            return HttpResponse(json.dumps(jsonTokenUri), content_type='application/json')

    return render_nextjs_page_sync(request)

@only_staff
@csrf_exempt
def endAuction(request):
    if request.method == 'POST':
        nftId = request.POST.get('nftId')
        winner = request.POST.get('winner')
        price = request.POST.get('price')
        txHash = request.POST.get('txHash')

        auctionEnd = EndAuction (nftId=nftId, winner=winner, price=price, txHash=txHash)
        auctionEnd.save()

        return HttpResponse()

    return HttpResponse()

@csrf_exempt
def sellNft(request):

    return render_nextjs_page_sync(request)

@csrf_exempt
def account(request):

    return render_nextjs_page_sync(request)