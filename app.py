import boto3
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Configurar el cliente de S3
s3 = boto3.client('s3')

def download_and_save_to_s3(url, page_num):
    # Descargar la página web
    response = requests.get(url)
    if response.status_code == 200:
        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        # Guardar el contenido en S3
        now = datetime.now()
        file_key = f'casas/contenido-pag-{page_num}-{now.strftime("%Y-%m-%d")}.html'
        s3.put_object(Bucket='parcial1', Key=file_key, Body=response.text)
        print(f'Guardado en S3: s3://bucket-raw/{file_key}')
    else:
        print(f'Error al descargar la página {url}')
    print("hola mundo")

def lambda_handler(event, context):
    base_url = 'https://casas.mitula.com.co/searchRE/nivel1-Cundinamarca/nivel2-Bogot%C3%A1/orden-0/q-bogot%C3%A1/pag-'
    for page_num in range(1, 6):
        url = f'{base_url}{page_num}?req_sgmt=REVTS1RPUDtVU0VSX1NFQVJDSDtTRVJQOw=='
        download_and_save_to_s3(url, page_num)

    return {
        'statusCode': 200,
        'body': 'Datos de finca raíz descargados y guardados en S3'
    }