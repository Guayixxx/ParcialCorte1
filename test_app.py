import pytest
from datetime import datetime
from moto import mock_s3
from unittest.mock import MagicMock
import requests
import boto3


@pytest.fixture
def mock_requests_get(mocker):
    # Mockear la función requests.get
    mocker.patch('requests.get')


@pytest.fixture
def mock_s3_client():
    # Mockear el cliente de S3
    with mock_s3():
        yield


def test_lambda_handler(mock_requests_get, mock_s3_client):

    mocked_response = MagicMock()
    mocked_response.content = b'<html><body>Mocked HTML</body></html>'
    requests.get.return_value = mocked_response

    from app import lambda_handler  # Asegúrate de importar el módulo correcto
    event = {}
    context = {}
    result = lambda_handler(event, context)

    # Modifica la URL según sea necesario
    requests.get.assert_called_with(
        'https://casas.mitula.com.co/searchRE/nivel1-Cundinamarca/\
            nivel2-Bogot%C3%A1/orden-0/q-bogot%C3%A1/\
                pag-1?req_sgmt=REVTS1RPUDtVU0VSX1NFQVJDSDtTRVJQOw==')

    # Verificar que los HTML se guardaron correctamente en S3
    assert result['statusCode'] == 200
    assert result['body'] == 'Páginas HTML descargadas y guardadas en S3.'

    # Modificar según la estructura de tu bucket y la fecha actual
    expected_s3_key = f'casas/contenido-pag-1-\
        {datetime.now().strftime("%Y-%m-%d")}.html'
    s3_client = boto3.client('s3')
    response = s3_client.list_objects(Bucket='parcial1')
    assert expected_s3_key in [obj['Key']
                               for obj in response.get('Contents', [])]
