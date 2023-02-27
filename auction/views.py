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
from .models import EndAuction
from django.core.cache import caches
from .decorators import only_staff
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def userInfo(request):
    user = request.user
    if user is not None:
        isStaff = user.is_staff
        data = {
            'username': user.username,
            'isStaff': isStaff,
        }
        return Response(data)

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

        auctionEnd = EndAuction (nftId=nftId, winner=winner, price=price)
        auctionEnd.save()

        cache = caches['auctions']

        allBids = cache.get(nftId) or {}
        bidsList = allBids.get('bids', [])

        # Creazione del dizionario
        auctionData = {
            'winner': winner,
            'price': price,
            'bids': bidsList,
        }

        # Conversione in JSON
        auctionJson = json.dumps(auctionData)

        # Restituzione della risposta HTTP con il JSON
        return HttpResponse(auctionJson, content_type='application/json')

    return HttpResponse()

@csrf_exempt
def sellNft(request):

    return render_nextjs_page_sync(request)

@csrf_exempt
def account(request):

    return render_nextjs_page_sync(request)