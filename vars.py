"""
CONSTATNS
"""

""" API """
PROVIDERS_LIST_URL = 'https://dev.it-thematic.ru/ikpz-upload-scripts/ugeoapi/api/v1/ugeoapi/providers/'
PROVIDER_URL = PROVIDERS_LIST_URL+'%i/'
FEATURES_URL = PROVIDER_URL+'features/'
DELETE_URL = FEATURES_URL+'purge/'

""" PROVIDERS INFO """
INFORMATION_OBJECT = 'ikpz_informationobject'
ORGANIZATION = 'ikpz_organization'
PROCUREMENT_POINT = 'PROCUREMENT_POINT'
TELEPHONE = 'ikpz_telephone'

PROVIDER_INF_OBJ_ID = 4
PROVIDER_ORG_ID = 5
PROVIDER_POINT_ID = 6
PROVIDER_PHONE_ID = 10

PROVIDER_NAME = 'name'
PROVIDER_EMAIL = 'email'
PROVIDER_ADDRESS = 'address'
PROVIDER_GEOM = 'geom'
PROVIDER_ADDITIONAL_INFO = 'additional_info'
PROVIDER_TYPE_OF_OBJECT = 'type_of_object'

PROVIDER_INF_OBJ = 'information_object'
PROVIDER_FULL_NAME = 'full_name'
PROVIDER_ADDRESS_OF_ORGANIZATION = 'address_of_organization'
PROVIDER_TYPE_OF_ORGANIZATION = 'type_of_organization'
PROVIDER_OGRN = 'ogrn'
PROVIDER_INN = 'inn'
PROVIDER_ANNUAL_REVENUE = 'annual_revenue'
PROVIDER_URL = 'url'

PROVIDER_ANNUAL_VOLUME = 'annual_volume'
PROVIDER_STATUS = 'status'
PROVIDER_ORGANIZATION = 'organization'

PROVIDER_TYPE_OF_PHONE = 'type_of_phone'
PROVIDER_VALUE = 'value'


""" FIELDS """
INPUT_NAME = 'Наименование'
INPUT_EMAIL = 'Емайл'
INPUT_PHONE = 'Телефон1'
INPUT_SITE = 'Сайт'
INPUT_ID = 'id 2gis'
INPUT_PARENT_ID = 'id родителя'
INPUT_ADDRESS = 'Адрес'
INPUT_GEOM = 'geometry'

INPUT_SOC_DICT = {
    'INPUT_SOC_VK': 'Соц. сети VK',
    'INPUT_SOC_OK': 'Соц. сети одноклассники',
    'INPUT_SOC_FB': 'Соц. сети Facebook',
    'INPUT_SOC_INST': 'Соц. сети Insagram',
    'INPUT_SOC_YT': 'Соц. сети youtube',
}

INPUT_SOC_LIST = [
    'Соц. сети VK',
    'Соц. сети одноклассники',
    'Соц. сети Facebook',
    'Соц. сети Insagram',
    'Соц. сети youtube',
]

""" VARS """
log_row_counter = 1
