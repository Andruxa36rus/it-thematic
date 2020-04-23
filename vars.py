"""
CONSTATNS
"""

""" API """
PROVIDERS_LIST_URL = 'https://dev.it-thematic.ru/ikpz-upload-scripts/ugeoapi/api/v1/ugeoapi/providers/'
PROVIDER_URL = PROVIDERS_LIST_URL+'%i/'
FEATURES_URL = PROVIDER_URL+'features/'
DELETE_URL = FEATURES_URL+'purge/'

""" PROVIDERS INFO """
# INFORMATION_OBJECT = 'ikpz_informationobject'
# ORGANIZATION = 'ikpz_organization'
# TELEPHONE = 'ikpz_telephone'
PROCUREMENT_POINT = 'PROCUREMENT_POINT'

PROVIDER_INF_OBJ_ID = 4
PROVIDER_ORG_ID = 5
PROVIDER_POINT_ID = 6
PROVIDER_PHONE_ID = 10

PROVIDER_INF_OBJ_NAME = 'name'
PROVIDER_INF_OBJ_EMAIL = 'email'
PROVIDER_INF_OBJ_ADDRESS = 'address'
PROVIDER_INF_OBJ_GEOM = 'geom'
PROVIDER_INF_OBJ_ADDITIONAL_INFO = 'additional_info'
PROVIDER_INF_OBJ_TYPE = 'type_of_object'

PROVIDER_RELATED_INF_OBJ = 'information_object'

PROVIDER_ORG_FULL_NAME = 'full_name'
PROVIDER_ORG_ADDRESS = 'address_of_organization'
PROVIDER_ORG_TYPE = 'type_of_organization'
PROVIDER_ORG_OGRN = 'ogrn'
PROVIDER_ORG_INN = 'inn'
PROVIDER_ORG_ANNUAL_REVENUE = 'annual_revenue'
PROVIDER_ORG_URL = 'url'

PROVIDER_POINT_ANNUAL_VOLUME = 'annual_volume'
PROVIDER_POINT_STATUS = 'status'
PROVIDER_POINT_ORGANIZATION = 'organization'

PROVIDER_PHONE_TYPE = 'type_of_phone'
PROVIDER_PHONE_VALUE = 'value'


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
    'vk': 'Соц. сети VK',
    'ok': 'Соц. сети одноклассники',
    'facebook': 'Соц. сети Facebook',
    'instagram': 'Соц. сети Insagram',
    'youtube': 'Соц. сети youtube',
}
