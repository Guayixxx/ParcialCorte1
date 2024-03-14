import boto3
import requests
from datetime import datetime

def lambda_handler(event, context):
    bucket_name = 'parcial1'
    print("entro a la fincion")
    for page_num in range(1, 6):
        url = f'https://casas.mitula.com.co/searchRE/nivel1-Cundinamarca/nivel2-Bogot%C3%A1/orden-0/q-bogot%C3%A1/pag-{page_num}?req_sgmt=REVTS1RPUDtVU0VSX1NFQVJDSDtTRVJQOw=='
        html_content = requests.get(url).content

        # Obtener la fecha actual
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Guardar el HTML en S3 con el formato deseado
        s3_key = f'casas/contenido-pag-{page_num}-{current_date}.html'
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=html_content)

    return {
        'statusCode': 200,
        'body': 'Páginas HTML descargadas y guardadas en S3.'
    }