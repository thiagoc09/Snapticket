# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 03:30:28 2024

@author: bruno
"""

"""
import boto3
import csv
import os
import boto3
import os
from concurrent.futures import ThreadPoolExecutor
import time

start_time = time.time()

acces_key_id='AKIAQ3EGR3RLPS2OMU54'
secret_acces_key='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'

def compare_faces(source_image_path, target_image_path):
    rekognition = boto3.client('rekognition', 
                               region_name='us-east-1',
                               aws_access_key_id=acces_key_id,
                               aws_secret_access_key=secret_acces_key)

    with open(source_image_path, 'rb') as source_image_file:
        source_image_bytes = source_image_file.read()

    with open(target_image_path, 'rb') as target_image_file:
        target_image_bytes = target_image_file.read()

    response = rekognition.compare_faces(
        SourceImage={
            'Bytes': source_image_bytes
        },
        TargetImage={
            'Bytes': target_image_bytes
        }
    )

    if len(response['FaceMatches']) > 0:
        return(True)
        #print('Pessoa identificada na segunda foto.')
        #for match in response['FaceMatches']:
        #    print('Similaridade: {}%'.format(match['Similarity']))
    else:
        return(False)
        #print('Pessoa não identificada na segunda foto.')






fotos_cadstrais='C:\\Users\\thiago.caetano\\Desktop\\SnapTicket\\rekognition\\imagens\\fotos_caastro'
fotos_festa='C:\\Users\\thiago.caetano\\Desktop\\SnapTicket\\rekognition\\imagens\\fotos_festa'

dir_cadastro=os.listdir(fotos_cadstrais)
dir_fotos_festa=os.listdir(fotos_festa)

dic={}
for foto_cadastro in dir_cadastro:
    #print(i.replace('.jpg',''))
    nome=foto_cadastro.replace('.jpg','')
    lista_fotos=[]
    for foto_festa in  dir_fotos_festa:
        if compare_faces(fotos_cadstrais+"\\"+foto_cadastro, fotos_festa+"\\"+foto_festa):
            lista_fotos.append(foto_festa)
        else:
            pass
    dic[nome]=lista_fotos



for nome in dic:
    print(nome)
    print("apareceu nas seguntes fotos:")
    print(dic[nome])
    print()
    
end_time = time.time()
total_time = end_time - start_time
print('tempo de execução:',total_time)


"""

import boto3
import os
from concurrent.futures import ThreadPoolExecutor
import time

# Inicialização do cliente AWS Rekognition

start_time = time.time()


acces_key_id = 'AKIAQ3EGR3RLPS2OMU54'
secret_acces_key = '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'
rekognition = boto3.client('rekognition', 
                           region_name='us-east-1',
                           aws_access_key_id=acces_key_id,
                           aws_secret_access_key=secret_acces_key)

def compare_faces(source_image_bytes, target_image_bytes):
    response = rekognition.compare_faces(
        SourceImage={'Bytes': source_image_bytes},
        TargetImage={'Bytes': target_image_bytes}
    )
    return len(response['FaceMatches']) > 0

def load_images_from_directory(directory_path):
    image_data = {}
    for image_name in os.listdir(directory_path):
        with open(os.path.join(directory_path, image_name), 'rb') as image_file:
            image_data[image_name] = image_file.read()
    return image_data

def find_matches(cadastro_image_name, cadastro_image_data, fotos_festa_data):
    matches = []
    for festa_image_name, festa_image_data in fotos_festa_data.items():
        if compare_faces(cadastro_image_data, festa_image_data):
            matches.append(festa_image_name)
    return cadastro_image_name.replace('.jpg', ''), matches

# Carregar as imagens em memória
fotos_cadstrais_path = 'C:\\Users\\thiago.caetano\\Desktop\\SnapTicket\\rekognition\\imagens\\fotos_caastro'
fotos_festa_path = 'C:\\Users\\thiago.caetano\\Desktop\\SnapTicket\\rekognition\\imagens\\fotos_festa'

cadastro_data = load_images_from_directory(fotos_cadstrais_path)
festa_data = load_images_from_directory(fotos_festa_path)

# Paralelizar as comparações
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(find_matches, cadastro_name, cadastro_data, festa_data)
               for cadastro_name, cadastro_data in cadastro_data.items()]

# Coletar e exibir resultados
result_dict = {future.result()[0]: future.result()[1] for future in futures}
for nome, fotos in result_dict.items():
    print(nome)
    print("apareceu nas seguntes fotos:")
    print(fotos)
    print()


end_time = time.time()
total_time = end_time - start_time
print('tempo de execução:',total_time)
