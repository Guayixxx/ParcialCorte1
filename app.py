import csv
from datetime import datetime
import io
import boto3
from bs4 import BeautifulSoup
import requests

s3 = boto3.client('s3')


def lambda_handler(event, context):
    bucket_name = 'parcial1'
    print("entro a la función")
    for page_num in range(1, 6):
        url = f'https://casas.mitula.com.co/\
                searchRE/nivel1-Cundinamarca/\
                    nivel2-Bogot%C3%A1/orden-0/\
                        q-bogot%C3%A1/pag-{page_num}?req_sgmt=\
                            REVTS1RPUDtVU0VSX1NFQVJDSDtTRVJQOw=='
        html_content = requests.get(url).content

        # Obtener la fecha actual
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Guardar el HTML en S3 con el formato deseado
        s3_key = f'casas/contenido-pag-{page_num}-{current_date}.html'
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=html_content)

    return {
        'statusCode': 200,
        'body': 'Páginas HTML descargadas y guardadas en S3.'
    }


def extraer(event, context):
    # Extrae información relevante del evento
    s3_event = event['Records'][0]['s3']
    bucket_name = s3_event['bucket']['name']
    object_key = s3_event['object']['key']

    # Descarga el archivo HTML desde S3
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    html_content = response['Body'].read().decode('utf-8')

    # Verificar que sea un archivo .html
    if object_key.endswith('.html'):
        # Extraer los datos con BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        propiedades = soup.find_all('div', class_='listing-card__title')
        precios = soup.find_all('div', class_='price')
        habitaciones = soup.find_all('span', {'data-test': 'bedrooms'})
        metros_cuadrados = soup.find_all(
            'div', class_='listing-card__property')

        # Construye la ruta del archivo en el nuevo bucket
        current_date = datetime.utcnow()
        year, month, day = current_date.strftime(
            '%Y'), current_date.strftime('%m'), current_date.strftime('%d')
        new_bucket_name = 'bucket-finalnodamas'
        new_folder_path = f'casas/year={year}/month={month}/day={day}/'
        new_object_key = f'{new_folder_path}{year}-{month}-{day}.csv'

        # Escribe los datos en un archivo CSV
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        csv_writer.writerow(
            ['Propiedad', 'Precio', 'Habitaciones', 'Metros_cuadrados'])

        for propiedad, precio, habitacion, \
            metro_cuadrado in zip(propiedades,
                                  precios, habitaciones, metros_cuadrados):
            propiedad = \
                propiedad.text.\
                strip().replace('\n', ' ') if propiedad else None
            precio = precio.text.strip().replace('\n', ' ') if precio else None
            habitacion = habitacion.text.strip().split()[0].replace(
                '\n', ' ') if habitacion else None
            metro_cuadrado = metro_cuadrado.find('span').text.strip().replace(
                '\n', ' ') if metro_cuadrado else None

            csv_writer.writerow(
                [propiedad, precio, habitacion, metro_cuadrado])

        # Guarda el archivo CSV en el nuevo bucket
        s3.put_object(Bucket=new_bucket_name, Key=new_object_key,
                      Body=csv_data.getvalue())

        # Verificar si se necesita crear el directorio
        if current_date.strftime('%Y-%m-%d') == f"{year}-{month}-{day}":
            s3.put_object(Bucket=new_bucket_name, Key=new_folder_path, Body='')

    return {
        'statusCode': 200,
        'body': 'Procesamiento exitoso'
    }
