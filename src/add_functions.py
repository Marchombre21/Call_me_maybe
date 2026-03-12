# ****************************************************************************#
#                                                                             #
#                                                         :::      ::::::::   #
#    add_functions,py                                   :+:      :+:    :+:   #
#                                                     +:+ +:+         +:+     #
#    By: bfitte <bfitte@student.42lyon.fr>          +#+  +:+       +#+        #
#                                                 +#+#+#+#+#+   +#+           #
#    Created: 2026/03/11 13:24:07 by bfitte            #+#    #+#             #
#    Updated: 2026/03/11 13:24:08 by bfitte           ###   ########lyon.fr   #
#                                                                             #
# ****************************************************************************#

from .utils import check_last_token_param, value_by_token
from .errors import UnknownCharacterError


def add_string(string: str, tokens_list: list[int], voc: dict[str,
                                                              int]) -> None:
    """Add a string to the prompt to the LLM after changing it to its token
    format.

    Args:
        tokens_list (list[int]): The prompt in token format.

    Raises:
        UnknownCharacterError: If the model doesn't know the asked letter.
    """
    for letter in string:
        if letter == ' ':
            letter = 'Ġ'
        token: int | None = voc.get(letter)
        if token:
            tokens_list.append(token)
        else:
            raise UnknownCharacterError(letter)


def add_token_one(token: int, tokens_list: list[int], voc: dict[str, int],
                  chosen_func: list[int]) -> None:
    """Add token to the prompt to the LLM.

    Args:
        tokens_list (list[int]): The prompt in token format
    """
    tokens_list.append(token)

    # We store the name of the function in a separate variable to retrieve
    # it later.
    if token != voc.get('"'):
        chosen_func.append(token)


def add_token_two(token: int, tokens_list: list[int], futurs_params: list[str],
                  voc: dict[str, int], chosen_param: list[int]) -> None:

    tokens_list.append(token)

    # We store the parameters of the function in a separate variable to
    # retrieve it later.
    # For the last token, we constrain the content according to its type.
    type_p: str = futurs_params[1]
    if type_p == 'string':
        stop: str = '"'
    else:
        if len(futurs_params) >= 4:
            stop = ','
        else:
            stop = '}'
    if (type_p == 'string' and stop in value_by_token(token, voc)):
        new_token: int | None = check_last_token_param('string', token, voc)
        if new_token:
            chosen_param.append(new_token)
    elif (type_p in ['number', 'integer']
          and stop in value_by_token(token, voc)):
        new_token = check_last_token_param('number', token, voc)
        if new_token:
            chosen_param.append(new_token)
    else:
        chosen_param.append(token)
