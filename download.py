import csv
import requests
import json
import math
import random

import vars


def get_provider_id(provider):
    """ Получаем id нужных нам провайдеров """
    response = requests.get(vars.PROVIDERS_LIST_URL+'?search='+provider)
    answer = json.loads(response.text)
    return answer['results'][0]['id']


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


def create_object(id, line, point=False):
    """
    Функция определяет какой объект нужно создать
    из списка провайдеров и создает его.
    ИО/Заготовитель/ПЗ/Телефон
    В итоге выполнения вложенной функции request()
    возвращает { 'response': ответ, 'new_obj_id': id вновь созданного объекта }
    """

    """ Если передан id провайдера 'Информационный объект' """
    if id == inf_obj_id:
        """ Происходит его наполнение """
        param_dict = fill_inf_obj(line, point)
        """ POST запрос на создание объекта """
        response = request(id, param_dict)
        return response

    """ Если передан id провайдера 'Заготовитель' """
    if id == org_id:
        param_dict = fill_org(line)
        response = request(id, param_dict)
        return response

    """ Если передан id провайдера 'Пункт заготовки' """
    if id == point_id:
        param_dict = fill_point(line)
        response = request(id, param_dict)
        return response

    """ Если передан id провайдера 'Телефон' """
    if id == phone_id:
        param_dict = fill_phone(line)
        response = request(id, param_dict)
        return response


def fill_inf_obj(line, point):
    additional_info_dict = {'id2gis': line[vars.ID]}
    additional_info = json.dumps(additional_info_dict)
    param_dict = {
        'name': line[vars.NAME],
        'email': line[vars.EMAIL],
        'address': line[vars.ADDRESS],
        'geom': line[vars.GEOM],
        'additional_info': additional_info
    }
    """ 
    Если передан point=True, значит это ИО типа Пункт заготовки.
    По умолчанию type_of_object=ORGANIZATION (при point=Flase)
    """
    if point:
        param_dict['type_of_object'] = 'PROCUREMENT_POINT'
    return param_dict


def fill_org(line):
    param_dict = {
        'information_object': current_inf_obj_org,
        'full_name': line[vars.NAME],
        'address_of_organization': line[vars.ADDRESS],
        'type_of_organization': 'ORG',
        'ogrn': get_num(13),
        'inn': get_num(10),
        'annual_revenue': get_num(1)
    }
    """ Проверка на наличие в csv необязательных параметров (в данном случае только URL) """
    if line[vars.SITE]:
        if vars.SITE[0:7] != 'https://' or vars.SITE[0:6] != 'http://':
            param_dict['url'] = 'https://' + line[vars.SITE]
        else:
            param_dict['url'] = line[vars.SITE]
    return param_dict


def fill_point(line):
    param_dict = {
        'information_object': current_inf_obj_point,
        'organization': current_org,
        'annual_volume': get_num(1),
        'status': 'LEGAL'
    }
    return param_dict


def fill_phone(line):
    param_dict = {
        'information_object': current_inf_obj_point,
        'type_of_phone': 'ACCOUNTING',
        'value': line[vars.PHONE]
    }
    return param_dict


def request(id, param_dict):
    """ Возврат - словарь, содержащий ответ для лога и id нового объекта для дальнейшей работы """
    response = requests.post(vars.FEATURES_URL % id, data=param_dict)
    if response.status_code != 201:
        """ Во избежания дальнейших ошибок, возвращаем new_obj_id = None """
        new_obj_id = None
        return {'response': response, 'new_obj_id': new_obj_id}
    answer = response.json()
    new_obj_id = answer['id']
    return {'response': answer, 'new_obj_id': new_obj_id}


def responses_result(*responses):
    """
    Функция возвращает общий результат ответов.
    Успешный ответ приходит словарём.
    """
    for response in responses:
        if not isinstance(response, dict) and response is not None:
            """ 
            Но если приходит не словарь, значит была ошибка.
            Тогда преобразуем ответ в словарь
            """
            answer_dict = json.loads(response.text)
            """ 
            Так как ошибка может быть по нескольким полям,
            Получаем ключи и перебераем по ним ошибку 
            """
            answer_keys = answer_dict.keys()
            string = 'error\n'
            for key in answer_keys:
                """ Собираем строку и возвращаем ее для будущего лога """
                string += key + ' - ' + answer_dict[key][0] + ' '
            return string
    return 'OK'


def log(result, name):
    f = open('log.txt', 'a+')
    f.write(str(vars.log_row_counter) + '. ' + name + '...' + result + '\n')
    f.close()
    vars.log_row_counter += 1


if __name__ == "__main__":
    """ Словарь прочитанных 'id родителя' """
    id_dict = {}
    """ Получение id провайдераов, согласно описанию подхода управления данными """
    inf_obj_id = get_provider_id(vars.INFORMATION_OBJECT)
    org_id = get_provider_id(vars.ORGANIZATION)
    point_id = get_provider_id(vars.PROCUREMENT_POINT)
    phone_id = get_provider_id(vars.TELEPHONE)


    """ Открытие файла как словарь """
    with open('input.csv', encoding='utf-8-sig') as f_obj:
        reader = csv.DictReader(f_obj, delimiter=';')
        """ Построчная работа со словарём """
        for line in reader:
            """ Если id родителя уже читался """
            if line[vars.PARENT_ID] in id_dict:
                """ Для Заготовителя, id которого содержится в словаре """
                current_org = id_dict[line[vars.PARENT_ID]]['org_id']

                """ Создается Информационный объект типа PROCUREMENT_POINT (point=True) """
                response = create_object(inf_obj_id, line, point=True)
                inf_obj_point_response = response['response']
                current_inf_obj_point = response['new_obj_id']

                """ Создается наследуемый Пункт заготовки """
                point_response = create_object(point_id, line)
                point_response = response['response']
                current_point = response['new_obj_id']

                """ Ответы передаются в функцию, которая возвращает ОК или текст ошибки """
                result = responses_result(inf_obj_point_response, point_response)
                log(result, line[vars.NAME])

                if result != 'OK':
                    """ Если функция вернула ошибки, значит в создании объектов нет смысла. Удаляем """
                    requests.delete(vars.FEATURES_URL % inf_obj_id + str(current_inf_obj_point))

            else:
                """ Создание информационного объекта типа ORGANIZATION """
                response = create_object(inf_obj_id, line)
                inf_obj_org_response = response['response']
                current_inf_obj_org = response['new_obj_id']

                """ Создание информационного объекта типа PROCUREMENT_POINT """
                response = create_object(inf_obj_id, line, point=True)
                inf_obj_point_response = response['response']
                current_inf_obj_point = response['new_obj_id']

                """ Создание Заготовителя """
                response = create_object(org_id, line)
                org_response = response['response']
                current_org = response['new_obj_id']

                """ Создание Пункта заготовки """
                response = create_object(point_id, line)
                point_response = response['response']
                current_point = response['new_obj_id']

                """ Добавление телефона, если имеется """
                phone_response = None
                if line[vars.PHONE]:
                    phone_response = create_object(phone_id, line)

                """ Результат - строка, которая запишется в лог """
                result = responses_result(inf_obj_org_response, inf_obj_point_response, org_response, point_response, phone_response)
                log(result, line[vars.NAME])
                if result == 'OK':
                    """ 
                    Так как этот id родителя встречается впервые,
                    и введенные данные - валидны, 
                    то следует добавить их в словарь идентификаторов
                    
                    ID Информационного объекта, от которого наследуются
                    Заготовитель и Пункты заготовки, 
                    хранится в словаре словарей, имеющим структуру:
                    { 
                        int(id родителя): # Числовой id родителя из csv
                            { 
                                # id Информационного объекта типа Заготовитель
                                'inf_obj_org_id': int(current_inf_obj_org),
                                # id Информационного объекта типа Пункт заготовки
                                'inf_obj_point_id': int(current_inf_obj_point) 
                            }
                    }
                    """
                    id_dict[line[vars.PARENT_ID]] = {
                        'org_id': current_org,
                        'inf_obj_point_id': current_inf_obj_point
                    }

                else:
                    """ 
                    Если result хотя бы по одному объекту возвращает error, 
                    тогда удаляются все раннее созданные объекты
                    """
                    requests.delete(vars.FEATURES_URL % inf_obj_id  + str(current_inf_obj_point))
                    requests.delete(vars.FEATURES_URL % inf_obj_id  + str(current_inf_obj_org))
