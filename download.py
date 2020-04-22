import csv
import requests
import json
import string
import math
import random
import logging

import vars


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
    if id == vars.PROVIDER_INF_OBJ_ID:
        """ Происходит его наполнение """
        param_dict = fill_inf_obj(line, point)
        """ POST запрос на создание объекта """
        response, new_obj_id = request(id, param_dict)
        return response, new_obj_id

    """ Если передан id провайдера 'Заготовитель' """
    if id == vars.PROVIDER_ORG_ID:
        param_dict = fill_org(line)
        response, new_obj_id = request(id, param_dict)
        return response, new_obj_id

    """ Если передан id провайдера 'Пункт заготовки' """
    if id == vars.PROVIDER_POINT_ID:
        param_dict = fill_point(line)
        response, new_obj_id = request(id, param_dict)
        return response, new_obj_id

    """ Если передан id провайдера 'Телефон' """
    if id == vars.PROVIDER_PHONE_ID:
        param_dict = fill_phone(line)
        response, new_obj_id = request(id, param_dict)
        return response


def fill_inf_obj_additional_info(line):
    """ Наполняет additional_info в Информационном объекте """
    additional_info_dict = {
        'id2gis': line[vars.INPUT_ID],
    }
    for item in line:
        if item in vars.INPUT_SOC_LIST:
            """ Если название столбца == Социальным сетям """
            if not line[item] == '':
                """ И его значение не пустое? Пишем! """
                additional_info_dict[item] = line[item]
    additional_info_dict = json.dumps(additional_info_dict)
    return additional_info_dict


def fill_inf_obj(line, point):
    additional_info = fill_inf_obj_additional_info(line)
    param_dict = {
        vars.PROVIDER_NAME: line[vars.INPUT_NAME],
        vars.PROVIDER_EMAIL: line[vars.INPUT_EMAIL],
        vars.PROVIDER_ADDRESS: line[vars.INPUT_ADDRESS],
        vars.PROVIDER_GEOM: line[vars.INPUT_GEOM],
        vars.PROVIDER_ADDITIONAL_INFO: additional_info
    }
    """ 
    Если передан point=True, значит это ИО типа Пункт заготовки.
    По умолчанию type_of_object=ORGANIZATION (при point=Flase)
    """
    if point:
        param_dict[vars.PROVIDER_TYPE_OF_OBJECT] = vars.PROCUREMENT_POINT
    return param_dict


def fill_org(line):
    param_dict = {
        vars.PROVIDER_INF_OBJ: current_inf_obj_org,
        vars.PROVIDER_FULL_NAME: line[vars.INPUT_NAME],
        vars.PROVIDER_ADDRESS_OF_ORGANIZATION: line[vars.INPUT_ADDRESS],
        vars.PROVIDER_TYPE_OF_ORGANIZATION: 'ORG',
        vars.PROVIDER_OGRN: get_num(13),
        vars.PROVIDER_INN: get_num(10),
        vars.PROVIDER_ANNUAL_REVENUE: get_num(1)
    }
    """ Проверка на наличие в csv необязательных параметров (в данном случае только URL) """
    if line[vars.INPUT_SITE]:
        """ Комментирование условия ниже позволяет проверить работоспособность логирования 400 ошибки """
        if vars.INPUT_SITE[0:7] != 'https://' or vars.INPUT_SITE[0:6] != 'http://':
            param_dict[vars.PROVIDER_URL] = 'https://' + line[vars.INPUT_SITE]
        else:
            param_dict[vars.PROVIDER_URL] = line[vars.INPUT_SITE]
    return param_dict


def fill_point(line):
    param_dict = {
        vars.PROVIDER_INF_OBJ: current_inf_obj_point,
        vars.PROVIDER_ORGANIZATION: current_org,
        vars.PROVIDER_ANNUAL_VOLUME: get_num(1),
        vars.PROVIDER_STATUS: 'LEGAL'
    }
    return param_dict


def fill_phone(line):
    param_dict = {
        vars.PROVIDER_INF_OBJ: current_inf_obj_point,
        vars.PROVIDER_TYPE_OF_PHONE: 'ACCOUNTING',
        vars.PROVIDER_VALUE: line[vars.INPUT_PHONE]
    }
    return param_dict


def request(id, param_dict):
    """ Возврат - словарь, содержащий ответ для лога и id нового объекта для дальнейшей работы """
    response = requests.post(vars.FEATURES_URL % id, data=param_dict)
    if response.status_code != 201:
        """ Во избежания дальнейших ошибок, возвращаем new_obj_id = None """
        new_obj_id = None
        return response, new_obj_id
    answer = response.json()
    new_obj_id = answer['id']
    return answer, new_obj_id


def responses_result(name, *responses):
    """
    Функция возвращает общий результат ответов.
    Успешный ответ приходит словарём.
    """
    for response in responses:
        if not isinstance(response, dict) and response is not None:
            """ 
            Но если приходит не словарь, значит была ошибка.
            Тогда вырисовывется вилка...
            """
            try:
                """ Четырехсотые ответы без труда будут преобразованы """
                answer_dict = json.loads(response.text)
                """ 
                Так как ошибка может быть по нескольким полям,
                Получаем ключи и перебераем по ним ошибки 
                """
                answer_keys = answer_dict.keys()
                string = ''
                for key in answer_keys:
                    """ Собираем строку и пишем в лог """
                    string += key + ' - ' + answer_dict[key][0] + ' '
                logger.info(name + '...' + string)
                return False

            except:
                """ 
                А вот 500+ ответы приходят строкой, 
                с преобразованием которой возникают сложности.
                Поэтому ищем индекс слова ОШИБКА 
                и срезаем всю его строку
                """
                print(response.status_code)
                str = response.text
                index_start = str.find('ОШИБКА')
                index_end = str.find('\n', index_start)
                string = str[index_start:index_end]
                logger.error(name + '...' + string)
                logger.debug(name + '\n' + response.text)
                return False
    logger.info(name + '...OK')
    return True


"""def log(result, name):
    f = open('log.txt', 'a+')
    f.write(str(vars.log_row_counter) + '. ' + name + '...' + result + '\n')
    f.close()
    vars.log_row_counter += 1
"""

if __name__ == "__main__":
    logging.basicConfig(filename='log.txt', filemode='w', format='%(levelname)s - %(message)s', level='INFO')
    logging.getLogger('urllib3').setLevel('CRITICAL')
    logger = logging.getLogger()
    """ Словарь прочитанных 'id родителя' """
    id_dict = {}

    """ Открытие файла как словарь """
    with open('input.csv', encoding='utf-8-sig') as f_obj:
        reader = csv.DictReader(f_obj, delimiter=';')
        """ Построчная работа со словарём """
        for line in reader:
            """ Если id родителя уже читался """
            if line[vars.INPUT_PARENT_ID] in id_dict:
                """ Для Заготовителя, id которого содержится в словаре """
                current_org = id_dict[line[vars.INPUT_PARENT_ID]]['org_id']

                """ Создается Информационный объект типа PROCUREMENT_POINT (point=True) """
                inf_obj_point_response, current_inf_obj_point = create_object(vars.PROVIDER_INF_OBJ_ID, line, point=True)

                """ Создается наследуемый Пункт заготовки """
                point_response, current_point = create_object(vars.PROVIDER_POINT_ID, line)

                """ Ответы передаются в функцию, которая возвращает ОК или текст ошибки """
                result = responses_result(line[vars.INPUT_NAME], inf_obj_point_response, point_response)

                if result:
                    """ Если функция вернула ошибки, значит в создании объектов нет смысла. Удаляем """
                    requests.delete(vars.FEATURES_URL % vars.PROVIDER_INF_OBJ_ID + str(current_inf_obj_point))

            else:
                """ Создание информационного объекта типа ORGANIZATION """
                inf_obj_org_response, current_inf_obj_org = create_object(vars.PROVIDER_INF_OBJ_ID, line)

                """ Создание информационного объекта типа PROCUREMENT_POINT """
                inf_obj_point_response, current_inf_obj_point = create_object(vars.PROVIDER_INF_OBJ_ID, line, point=True)

                """ Создание Заготовителя """
                org_response, current_org = create_object(vars.PROVIDER_ORG_ID, line)

                """ Создание Пункта заготовки """
                point_response, current_point = create_object(vars.PROVIDER_POINT_ID, line)

                """ Добавление телефона, если имеется """
                phone_response = None
                if line[vars.INPUT_PHONE]:
                    phone_response = create_object(vars.PROVIDER_PHONE_ID, line)

                """ Результат - строка, которая запишется в лог """
                result = responses_result(line[vars.INPUT_NAME], inf_obj_org_response, inf_obj_point_response, org_response,
                                          point_response, phone_response)
                if result:
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
                                # id Заготовителя
                                'org_id': int(current_inf_obj_org),
                                # id Информационного объекта типа Пункт заготовки
                                'inf_obj_point_id': int(current_inf_obj_point) 
                            }
                    }
                    """
                    id_dict[line[vars.INPUT_PARENT_ID]] = {
                        'org_id': current_org,
                        'inf_obj_point_id': current_inf_obj_point
                    }

                else:
                    """ 
                    Если result хотя бы по одному объекту возвращает error, 
                    тогда удаляются все раннее созданные объекты
                    """
                    requests.delete(vars.FEATURES_URL % vars.PROVIDER_INF_OBJ_ID + str(current_inf_obj_point))
                    requests.delete(vars.FEATURES_URL % vars.PROVIDER_INF_OBJ_ID + str(current_inf_obj_org))
