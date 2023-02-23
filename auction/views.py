from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django_nextjs.render import render_nextjs_page_sync
from pinata import Pinata
from decouple import config
import os
from .forms import AddUriToArray
import requests
import json
from django.http import HttpResponse


# Create your views here.
@csrf_exempt
def homePageView(request):

    # return render(request, "homepage.html", {})
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