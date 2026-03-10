# ****************************************************************************#
#                                                                             #
#                                                         :::      ::::::::   #
#    utils.py                                           :+:      :+:    :+:   #
#                                                     +:+ +:+         +:+     #
#    By: bfitte <bfitte@student.42lyon.fr>          +#+  +:+       +#+        #
#                                                 +#+#+#+#+#+   +#+           #
#    Created: 2026/03/10 07:03:26 by bfitte            #+#    #+#             #
#    Updated: 2026/03/10 07:03:27 by bfitte           ###   ########lyon.fr   #
#                                                                             #
# ****************************************************************************#

def value_by_token(token: int, voc: dict) -> str | None:
    try:
        return [key for key, value in voc.items() if value == token][0]
    except IndexError:
        return None


def check_last_token(type: str, token: int, voc: dict) -> int:
    if type == 'string':
        stop: str = '"'
    else:
        stop = '}'
    last_value: str = value_by_token(token, voc)
    index: int = last_value.rfind(stop)
    if index != len(last_value) - 1:
        nb_char_to_remove: int = len(last_value) - index - 1
        new_token: int = voc.get(last_value[:-nb_char_to_remove])
        if new_token is None:
            return voc.get(stop)
        else:
            return new_token
    else:
        return token


def check_last_token_param(type: str, token: int, voc: dict) -> int | None:
    if type == 'string':
        stop: str = '"'
    else:
        stop = '}'
    last_value: str = value_by_token(token, voc)
    index: int = last_value.find(stop)
    if index != 0:
        nb_char_to_remove: int = len(last_value) - index
        new_token: int = voc.get(last_value[:-nb_char_to_remove])
        if new_token is None:
            return None
        else:
            return new_token
    else:
        return None


def add_name(dicts: list[dict], prompt: str, name: str) -> None:
    for dict in dicts:
        if dict.get('prompt') == prompt:
            dict.update({'name': name})
            break


def add_parameters(dicts: list[dict], prompt: str, key: str, value: str) ->\
                    None:
    for dict in dicts:
        if dict.get('prompt') == prompt:
            if dict.get('parameters') is None:
                dict.update({'parameters': {key: value}})
            else:
                dict.get('parameters').update({key: value})
