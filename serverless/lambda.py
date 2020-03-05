# -*- coding: utf-8 -*-

import boto3
import os
import json
import datetime

from contextlib import closing

def lambda_handler(event, context):
    
    name = event["name"]
    topup_qty = event["topup_qty"]

    xdate = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    print('Event: ' + json.dumps(event))
    #print('Date time: ' +xdate)
    print('Lang: ' + event["language"])
    
    #Sending notification about new post to SNS
    #client = boto3.client('sns')
    #client.publish(
    #    TopicArn = os.environ['SNS_TOPIC'],
    #    Message=json.dumps({'default': json.dumps(event)}),
    #    MessageStructure='json'
    #)
    
    msisdnBlock = ""
    for c in event["msisdn"]:
      msisdnBlock += c + " "
    
    print('Msisdn: ' +msisdnBlock)
    
    if event["language"].lower() == "portuguese" :
      rest = 'Olá ' + event["name"] + '! Obrigado por escolher a India Telecom. O seu telemóvel ' + msisdnBlock + ' foi carregado com ' + event["topup_qty"] + ' rupias com sucesso. Visite a nossa página para conhecer os nossos produtos e serviços! A sua mensagem é ' + event["message"] + '. Iphone já não há, mas há sempre alegria'
      voiceId = 'Ines'
    elif event["language"].lower() == "hindi" :
      rest = 'नमस्ते  ' + event["name"] + ' भारत टेलीकॉम को चुनने के लिए धन्यवाद। आपका मोबाइल फोन ' + msisdnBlock + ' सफलता के साथ ' + event["topup_qty"] + ' रुपये के साथ ऊपर था। हमारे नए उत्पादों और सेवाओं को जानने के लिए हमारी वेबसाइट पर जाएँ! आपका संदेश ' + event["message"] + ' है। Iphone अनुपलब्ध है, लेकिन वहाँ हमेशा है'
      voiceId = 'Aditi'
    elif event["language"].lower() == "french" :
      rest = 'Bonjour ' + event["name"] + '! Merci d’avoir choisi India Telecom. Votre téléphone portable ' + msisdnBlock + ' a été rechargé avec ' + event["topup_qty"] + ' roupies avec succès. Visitez notre site web pour connaître nos nouveaux produits et services! Votre message est ' + event["message"]  + '. Iphone n\'est pas disponible, mais il y a toujours de la joie'
      voiceId = 'Celine'
    else:
      rest = 'Hello ' + event["name"] + '! Thank you for choosing India Telecom. Your mobile phone ' + msisdnBlock + ' was top up with ' + event["topup_qty"] + ' rupees with success. Visit our website to know our new products and services! You message is ' + event["message"] +'. Iphone is unavailable, but there is always joy'
      voiceId = 'Raveena'

    #Because single invocation of the polly synthesize_speech api can 
    # transform text with about 1,500 characters, we are dividing the 
    # post into blocks of approximately 1,000 characters.
    textBlocks = []
    while (len(rest) > 1100):
        begin = 0
        end = rest.find(".", 1000)

        if (end == -1):
            end = rest.find(" ", 1000)
            
        textBlock = rest[begin:end]
        rest = rest[end:]
        textBlocks.append(textBlock)
    textBlocks.append(rest)            

    #For each block, invoke Polly API, which will transform text into audio
    polly = boto3.client('polly')
    for textBlock in textBlocks: 
        response = polly.synthesize_speech(
            OutputFormat='mp3',
            Text = textBlock,
            VoiceId = voiceId
        )
        
        #Save the audio stream returned by Amazon Polly on Lambda's temp 
        # directory. If there are multiple text blocks, the audio stream
        # will be combined into a single file.
        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                output = os.path.join("/tmp/", event["msisdn"]+xdate)
                with open(output, "a") as file:
                    file.write(stream.read())

    s3 = boto3.client('s3')
    s3.upload_file('/tmp/' + event["msisdn"]+xdate, 
      os.environ['BUCKET_NAME'], 
      event["msisdn"] + "-" + xdate + "-" +  event["language"] + ".mp3")
    s3.put_object_acl(ACL='public-read', 
      Bucket=os.environ['BUCKET_NAME'], 
      Key= event["msisdn"] + "-" + xdate + "-" +  event["language"] + ".mp3")

    location = s3.get_bucket_location(Bucket=os.environ['BUCKET_NAME'])
    region = location['LocationConstraint']
    
    if region is None:
        url_begining = "https://s3.amazonaws.com/"
    else:
        url_begining = "https://s3-" + str(region) + ".amazonaws.com/" \
    
    url = url_begining \
            + str(os.environ['BUCKET_NAME']) \
            + "/" \
            #+ str(event["msisdn"]) \
            #+ event["msisdn"] + "-" + xdate \
            #+ ".mp3"
         
    url = url + event["msisdn"]  + "-" + xdate + "-" +  event["language"] + ".mp3"
    
    return {
        'statusCode': 200,
        #'body': json.dumps(url)
        'body': url
    }
