import csv
import requests
import json
import random
import logging

import vars

file_log = logging.FileHandler('log.txt', 'w')
console_out = logging.StreamHandler()
logging.basicConfig(handlers=(file_log, console_out), format='%(levelname)s - %(message)s', level='INFO')


def get_num(length):
    """ Заполняем строку нужное количество раз случайным числом и возвращаем int """
    number = ''
    if length == 1:
        """ Если заказ на одно число, то оно не 0 """
        number = random.randint(1, 9)
    else:
        for i in range(0, length):
            if i == 0:
                """ Первое число не нулевое """
                number += str(random.randint(1, 9))
            else:
                number += str(random.randint(0, 9))
    return int(number)


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


def create_object(id, line, point=False):
    """
    Функция определяет какой объект нужно создать
    из списка провайдеров и создает его.
    ИО/Заготовитель/ПЗ/Телефон
    В итоге выполнения вложенной функции request()
    возвращает id типом либо int либо None
    """
    param_dict = {}
    new_obj_id = None

    if id == vars.PROVIDER_INF_OBJ_ID:
        """ Если передан id провайдера 'Информационный объект' - наполняем """
        param_dict = fill_inf_obj(line, point)

    elif id == vars.PROVIDER_ORG_ID:
        """ Если передан id провайдера 'Заготовитель' """
        param_dict = fill_org(line)

    elif id == vars.PROVIDER_POINT_ID:
        """ Если передан id провайдера 'Пункт заготовки' """
        param_dict = fill_point(line)

    elif id == vars.PROVIDER_PHONE_ID:
        """ Если передан id провайдера 'Телефон' """
        param_dict = fill_phone(line)

    """ POST запрос на создание объекта, там же осуществляется обработка ошибки """
    new_obj_id = request(id, param_dict, line)

    return new_obj_id


def fill_inf_obj_additional_info(line):
    """ Наполняет additional_info в Информационном объекте """
    additional_info_dict = {
        'id2gis': line[vars.INPUT_ID]
    }
    for item in line:
        if item in vars.INPUT_SOC_DICT.values():
            """ Если название столбца == Социальным сетям """
            key = get_key(vars.INPUT_SOC_DICT, item)
            if not line[item] == '':
                """ И его значение не пустое? Пишем! """
                additional_info_dict.setdefault('social', {})[key] = line[item]
    additional_info_dict = json.dumps(additional_info_dict)
    return additional_info_dict


def fill_inf_obj(line, point):
    additional_info = fill_inf_obj_additional_info(line)
    param_dict = {
        vars.PROVIDER_INF_OBJ_NAME: line[vars.INPUT_NAME],
        vars.PROVIDER_INF_OBJ_EMAIL: line[vars.INPUT_EMAIL],
        vars.PROVIDER_INF_OBJ_ADDRESS: line[vars.INPUT_ADDRESS],
        vars.PROVIDER_INF_OBJ_GEOM: line[vars.INPUT_GEOM],
        vars.PROVIDER_INF_OBJ_ADDITIONAL_INFO: additional_info
    }
    """ 
    Если передан point=True, значит это ИО типа Пункт заготовки.
    По умолчанию type_of_object=ORGANIZATION (при point=Flase)
    """
    if point:
        param_dict[vars.PROVIDER_INF_OBJ_TYPE] = vars.PROCUREMENT_POINT
    return param_dict


def fill_org(line):
    param_dict = {
        vars.PROVIDER_RELATED_INF_OBJ: current_inf_obj_org,
        vars.PROVIDER_ORG_FULL_NAME: line[vars.INPUT_NAME],
        vars.PROVIDER_ORG_ADDRESS: line[vars.INPUT_ADDRESS],
        vars.PROVIDER_ORG_TYPE: 'ORG',
        vars.PROVIDER_ORG_OGRN: get_num(13),
        vars.PROVIDER_ORG_INN: get_num(10),
        vars.PROVIDER_ORG_ANNUAL_REVENUE: get_num(1)
    }
    """ Проверка на наличие в csv необязательных параметров (в данном случае только URL) """
    if line[vars.INPUT_SITE]:
        if vars.INPUT_SITE[0:7] != 'https://' or vars.INPUT_SITE[0:6] != 'http://':
            param_dict[vars.PROVIDER_ORG_URL] = 'https://' + line[vars.INPUT_SITE]
        else:
            param_dict[vars.PROVIDER_ORG_URL] = line[vars.INPUT_SITE]
    return param_dict


def fill_point(line):
    param_dict = {
        vars.PROVIDER_RELATED_INF_OBJ: current_inf_obj_point,
        vars.PROVIDER_POINT_ORGANIZATION: current_org,
        vars.PROVIDER_POINT_ANNUAL_VOLUME: get_num(1),
        vars.PROVIDER_POINT_STATUS: 'LEGAL'
    }
    return param_dict


def fill_phone(line):
    param_dict = {
        vars.PROVIDER_RELATED_INF_OBJ: current_inf_obj_point,
        vars.PROVIDER_PHONE_TYPE: 'ACCOUNTING',
        vars.PROVIDER_PHONE_VALUE: line[vars.INPUT_PHONE]
    }
    return param_dict


def request(id, param_dict, line):
    """ Возвращает id нового объекта, либо - ошибку в лог и None """
    response = requests.post(vars.FEATURES_URL % id, data=param_dict)
    if 400 <= response.status_code <= 499:
        logging.error(line[vars.INPUT_NAME] + ' ' + response.text + ' | ' + str(line))
        return None
    elif 500 <= response.status_code <= 599:
        logging.critical(line[vars.INPUT_NAME] + ' ' + response.text + ' | ' + str(line))
        return None
    answer = response.json()
    new_obj_id = answer['id']
    return new_obj_id


if __name__ == "__main__":
    """ Словарь прочитанных 'id родителя' """
    id_dict = {}
    """ Открытие файла как словарь """
    with open('input.csv', encoding='utf-8-sig') as f_obj:
        reader = csv.DictReader(f_obj, delimiter=';')
        """ Построчная работа со словарём """
        for line in reader:
            """ Если id родителя ранее не читался """
            if line[vars.INPUT_PARENT_ID] not in id_dict:
                """ Создание информационного объекта типа ORGANIZATION """
                current_inf_obj_org = create_object(vars.PROVIDER_INF_OBJ_ID, line)
                if current_inf_obj_org is None:
                    """ 
                    Если current_inf_obj_org == None, (id текущего Информационного объекта типа Заготовитель)
                    значит объект не был создан. Ошибка уже в логе. Продолжение бессмысленно
                    """
                    continue

                """ Создание Заготовителя """
                current_org = create_object(vars.PROVIDER_ORG_ID, line)
                if current_org is None:
                    """ Если создании Организации завершилось с ошибкой, то ее ИО нам тоже не пригодится. Выходим """
                    requests.delete(vars.FEATURES_URL % vars.PROVIDER_INF_OBJ_ID + str(current_inf_obj_org))
                    continue

                """ 
                ID Информационного объекта, от которого наследуются
                Заготовитель и Пункты заготовки, 
                хранится в словаре словарей, имеющим структуру:
                { 
                    int(id родителя): # Числовой id родителя из csv
                        { 
                            # id Заготовителя
                            'org_id': int(current_org),
                            # id Информационного объекта типа Пункт заготовки
                            'inf_obj_point_id': int(current_inf_obj_point) 
                        }
                }
                """
                id_dict[line[vars.INPUT_PARENT_ID]] = {
                    'org_id': current_org
                }

            """ 
            Для создания Информационного объекта типа PROCUREMENT_POINT (point=True) 
            нужно знать id Организации. Берем из словаря и создаем
            """
            current_org = id_dict[line[vars.INPUT_PARENT_ID]]['org_id']

            current_inf_obj_point = create_object(vars.PROVIDER_INF_OBJ_ID, line, point=True)
            if current_inf_obj_point is None:
                """ 
                Если current_inf_obj_point == None, (id текущего Информационного объекта типа Пункт заготовки"
                значит объект не был создан. Ошибка уже в логе. Продолжение бессмысленно
                """
                continue

            """ Сразу запишем id только что созданного Информационного объекта типа Пункт заготовки """
            id_dict[line[vars.INPUT_PARENT_ID]]['inf_obj_point_id'] = current_inf_obj_point

            """ Создается наследуемый Пункт заготовки """
            current_point = create_object(vars.PROVIDER_POINT_ID, line)

            """ Если None - значит была ошибка, и она уже в логе. Значит только что созданный ИО нам не нужен. Выход """
            if current_point is None:
                requests.delete(vars.FEATURES_URL % vars.PROVIDER_INF_OBJ_ID + str(current_inf_obj_point))
                continue

            """ Добавление телефона, если имеется """
            if line[vars.INPUT_PHONE]:
                phone = create_object(vars.PROVIDER_PHONE_ID, line)

            logging.info(line[vars.INPUT_NAME] + '...OK')
