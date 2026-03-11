# ****************************************************************************#
#                                                                             #
#                                                         :::      ::::::::   #
#    initiate_request.py                                :+:      :+:    :+:   #
#                                                     +:+ +:+         +:+     #
#    By: bfitte <bfitte@student.42lyon.fr>          +#+  +:+       +#+        #
#                                                 +#+#+#+#+#+   +#+           #
#    Created: 2026/03/11 12:40:27 by bfitte            #+#    #+#             #
#    Updated: 2026/03/11 12:40:28 by bfitte           ###   ########lyon.fr   #
#                                                                             #
# ****************************************************************************#

import json
from .errors import FormatError
from llm_sdk import Small_LLM_Model


def init_dict(prompt: str, final_dict: list[dict]) -> None:
    """Create the dictionnary for this request.

    Args:
        prompt (str): The request.

    Raises:
        FormatError: If the request isn't a string.
    """
    if isinstance(prompt, str):
        final_dict.append({'prompt': prompt})
    else:
        raise FormatError('Request must be a string.')


def init_name(tokens_list: list[int], model: Small_LLM_Model):
    """Format the prompt to the LLM when I ask for the function name.

    Args:
        tokens_list (list[int]): The prompt in token format.

    Raises:
        UnknownCharacterError: If the model doesn't know the asked letter.
    """
    for token in model.encode('"name": "').tolist()[0]:
        tokens_list.append(token)


def init_parameters(tokens_list: list[int], model: Small_LLM_Model):
    """Format the prompt to the LLM when I ask for the function parameters.

    Args:
        tokens_list (list[int]): The prompt in token format.

    Raises:
        UnknownCharacterError: If the model doesn't know the asked letter.
    """
    for token in model.encode('"parameters": {').tolist()[0]:
        tokens_list.append(token)


def param_question_one(prompt: str, model: Small_LLM_Model,
                       func_dict: list[dict]) -> list[int]:
    """Configures the start of the prompt for llm in order to find the
    function name.
    """
    functions: str = ""

    # We retrieve the names and descriptions of each function.
    functions_list: list = [{
        "name": f.get('name'),
        "description": f.get('description')
    } for f in func_dict]

    # We serialize the dict to a JSON formatted string
    functions = json.dumps(functions_list)
    tokens: list[int] = model.encode(
        f"Request:{prompt}\nFunctions:({functions})\n"
        "Return a JSON object with the function call.{").tolist()[0]

    return tokens


def param_question_two(prompt: str, model: Small_LLM_Model,
                       func_dict: list[dict], chosen_func: list[int]) ->\
                        list[int]:
    """Configures the start of the prompt for llm in order to find the
    function parameters.
    """
    # We retrieve the previously chosen function name.
    func_name: str = "".join(model.decode(chosen_func))
    func_dic: dict = [
        func for func in func_dict
        if func.get('name') == func_name
    ][0]

    tokens = model.encode(f'Task:{prompt}\n{json.dumps(func_dic)}\n'
                          'JSON: {').tolist()[0]

    return tokens
