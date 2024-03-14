import boto3
import csv
from datetime import datetime
from io import StringIO
from bs4 import BeautifulSoup
import urllib.parse

s3 = boto3.client('s3')


def extract_data_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extraer precio
    price_tag = soup.find('div', class_='listing')['data-price']
    price = price_tag.replace(',', '')  # Eliminar comas si están presentes

    # Extraer metraje
    area_tag = soup.find('div', class_='listing')['data-floorarea']
    area = area_tag.split()[0]  # Obtener solo el número

    # Extraer número de habitaciones
    rooms = soup.find('div', class_='listing')['data-rooms']

    # Extraer características adicionales (si las hay)
    additional_features = {}
    additional_info_tags = soup.find_all('div', class_='listing-card__image')
    for tag in additional_info_tags:
        # Puedes agregar lógica adicional para extraer características específicas aquí
        # Por ejemplo, si las características están dentro de etiquetas específicas
        # Puedes utilizar métodos de BeautifulSoup para encontrar y extraer esa información.
        pass

    return price, area, rooms, additional_features


def lambda_handler(event, context):
    # Obtener el nombre del bucket y el nombre del archivo que se subió
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    # Obtener la fecha actual
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    day = current_date.day
    date_str = current_date.strftime("%Y-%m-%d")

    # Obtener el contenido del archivo HTML desde S3
    response = s3.get_object(Bucket=bucket, Key=key)
    html_content = response['Body'].read().decode('utf-8')

    # Extraer datos del HTML
    price, area, bedrooms = extract_data_from_html(html_content)

    # Guardar los datos en un archivo CSV
    csv_data = [price, area, bedrooms]
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(csv_data)

    # Construir la ruta del archivo CSV en función de la fecha actual
    target_bucket = 'bucket-finalnodamas'  # Reemplaza con el nombre de tu bucket de destino
    target_key = f'casas/year={year}/month={month}/day={day}/{date_str}.csv'

    # Guardar el archivo CSV en el nuevo bucket de S3
    s3.put_object(Bucket=target_bucket, Key=target_key, Body=csv_buffer.getvalue())

    return {
        'statusCode': 200,
        'body': 'Datos extraídos y guardados correctamente.'
    }
