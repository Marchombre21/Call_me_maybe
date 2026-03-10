# ****************************************************************************#
#                                                                             #
#                                                         :::      ::::::::   #
#    constain_generator.py                              :+:      :+:    :+:   #
#                                                     +:+ +:+         +:+     #
#    By: bfitte <bfitte@student.42lyon.fr>          +#+  +:+       +#+        #
#                                                 +#+#+#+#+#+   +#+           #
#    Created: 2026/03/05 10:37:30 by bfitte            #+#    #+#             #
#    Updated: 2026/03/05 10:37:31 by bfitte           ###   ########lyon.fr   #
#                                                                             #
# ****************************************************************************#

import re
import numpy as np
import json
from llm_sdk import Small_LLM_Model
from re import Pattern
from .utils import (value_by_token,
                    check_last_token,
                    add_name, add_parameters,
                    check_last_token_param)


class FunctionCalling():

    def __init__(self):
        self.__final_dicts: list[dict] = []
        self.__request_tokens: list[int] = []
        self.__name_authorized_token: list[int] = []
        self.__param_authorized_tokens: list[int] = []
        self.__chosen_func: list[int] = []
        self.__chosen_param: list[int] = []
        self.__futurs_params: list[str] = []
        self.__voc: dict = {}
        self.__step: int = 1
        self.__functions_dict: list[dict] = []

    def set_voc(self, voc_dict: dict):
        """Record the dict returned by json.load containing the llm vocabulary
        (key) associated with their token value (value).
        'r': Prevents the interpreter from treating '\' as standard escape
        characters (useless here but it's good practice).
        '^': Start form the line beginning.
        '+': Requires that this group of characters appear one or more times.
        '$': Ensures that the match ends at the very last character of the
        evaluated string.
        """
        if isinstance(voc_dict, dict):
            self.__voc = voc_dict
            if len(self.__name_authorized_token) == 0:
                pattern: Pattern = re.compile(r'^[a-z_"]+$')
                for token_str, token_value in self.__voc.items():
                    if pattern.match(token_str):
                        self.__name_authorized_token.append(token_value)

    def set_functions(self, func_dict: dict) -> None:
        if isinstance(func_dict, list):
            self.__functions_dict = func_dict

    def init_dict(self, prompt: str, model: Small_LLM_Model):
        # Gérer avec une erreur s'il n'y a pas la lettre
        self.__final_dicts.append({'prompt': prompt})

    def init_name(self, tokens_list: list[int]):
        # Gérer avec une erreur s'il n'y a pas la lettre
        for letter in '"name":"':
            tokens_list.append(self.__voc.get(letter))

    def init_parameters(self, tokens_list: list[int]):
        # Gérer avec une erreur s'il n'y a pas la lettre
        for letter in '"parameters":{':
            tokens_list.append(self.__voc.get(letter))

    def add_string(self, string: str, tokens_list: list[int]):
        for letter in string:
            tokens_list.append(self.__voc.get(letter))

    def add_token(self, token: int, tokens_list: list[int]):
        tokens_list.append(token)
        if self.__step == 1 and token != self.__voc.get('"'):
            self.__chosen_func.append(token)
        if self.__step == 2:
            type_p: str = self.__futurs_params[1]
            if type_p == 'string':
                stop: str = '"'
            else:
                if len(self.__futurs_params) >= 4:
                    stop = ','
                else:
                    stop = '}'
            if (type_p == 'string' and stop in
                    value_by_token(token, self.__voc)):
                new_token: int | None = check_last_token_param('string',
                                                               token,
                                                               self.__voc)
                if new_token:
                    self.__chosen_param.append(new_token)
            elif (type_p == 'number' and stop in
                    value_by_token(token, self.__voc)):
                new_token: int | None = check_last_token_param('number',
                                                               token,
                                                               self.__voc)
                if new_token:
                    self.__chosen_param.append(new_token)
            else:
                self.__chosen_param.append(token)

    def _init_request(self, tokens: list[int], prompt: str,
                      model: Small_LLM_Model) -> None:

        self.__request_tokens = tokens

        if self.__step == 1:
            self.init_dict(prompt, model)
            self.init_name(self.__request_tokens)

        if self.__step == 2:
            self.init_parameters(self.__request_tokens)
            params: dict | None = self.search_params_type(model)
            if not params:
                self.add_string('No arguments', self.__request_tokens)
            else:
                for key, value in params.items():
                    self.__futurs_params.append(key)
                    self.__futurs_params.append(value.get('type', 'any'))
                if self.__futurs_params[1] == 'string':
                    self.add_string('"' + self.__futurs_params[0] + '":"',
                                    self.__request_tokens)
                else:
                    self.add_string('"' + self.__futurs_params[0] + '":',
                                    self.__request_tokens)

    def param_question(self, prompt: str, model: Small_LLM_Model) -> list[int]:

        if self.__step == 1:
            functions: str = ""
            functions_list: list = [{
                "name": f.get('name'),
                "description": f.get('description')
            } for f in self.__functions_dict]
            functions = json.dumps(functions_list)
            tokens: list[int] = model.encode(
                f"Request:{prompt}\nFunctions:({functions})\n"
                "Return a JSON object with the function call.{").tolist()[0]

        if self.__step == 2:
            func_name: str = "".join(model.decode(self.__chosen_func))
            func_dic: dict = [
                func for func in self.__functions_dict
                if func.get('name') == func_name
            ][0]

            tokens = model.encode(f'Task:{prompt}\n{json.dumps(func_dic)}\n'
                                  'JSON: {').tolist()[0]

        return tokens

    def init_autor_tokens(self):
        self.__param_authorized_tokens = []
        if self.__futurs_params[1] == 'string':
            for value in self.__voc.values():
                self.__param_authorized_tokens.append(value)
        if self.__futurs_params[1] == 'number':
            if len(self.__futurs_params) >= 4:
                pattern: Pattern = re.compile(r'^([-0-9.,]+|}}|})$')
            else:
                pattern = re.compile(r'^([-0-9.]+|}}|})$')
            for token_str, token_value in self.__voc.items():
                if pattern.match(token_str):
                    self.__param_authorized_tokens.append(token_value)

    def ask_llm(self, prompt: str, model: Small_LLM_Model) -> None:
        self.__step = 1
        self.__chosen_func = []
        tokens: list[int] = self.param_question(prompt, model)
        self._init_request(tokens, prompt, model)
        chosen_token: int = 12

        if self.__step == 1:
            while '"' not in value_by_token(chosen_token, self.__voc):
                logits: list[float] = model.get_logits_from_input_ids(
                    self.__request_tokens)
                chosen_token = self.handle_logits(logits, model)
                self.add_token(chosen_token, self.__request_tokens)
            func_name: str = "".join(model.decode(self.__chosen_func))
            add_name(self.__final_dicts, prompt, func_name)
            self.__step = 2

        if self.__step == 2:
            tokens = self.param_question(prompt, model)
            self._init_request(tokens, prompt, model)
            logits: list[float] = model.get_logits_from_input_ids(
                self.__request_tokens)
            chosen_token = self.handle_logits(logits, model)

            while len(self.__futurs_params) >= 4:
                self.init_autor_tokens()
                self.__chosen_param = []
                if self.__futurs_params[1] == 'string':
                    stop: str = '"'
                else:
                    stop = ','

                while stop not in value_by_token(chosen_token, self.__voc):
                    logits = model.get_logits_from_input_ids(
                        self.__request_tokens)
                    chosen_token = self.handle_logits(logits, model)
                    self.add_token(chosen_token, self.__request_tokens)
                    print(model.decode(self.__request_tokens))
                    print()
                param_str: str = "".join(model.decode(self.__chosen_param))
                add_parameters(self.__final_dicts, prompt,
                               self.__futurs_params[0], param_str)
                del self.__futurs_params[0:2]
                if self.__futurs_params[1] == 'string':
                    self.add_string('"' + self.__futurs_params[0] + '":"',
                                    self.__request_tokens)
                else:
                    self.add_string('"' + self.__futurs_params[0] + '":',
                                    self.__request_tokens)
                logits = model.get_logits_from_input_ids(self.__request_tokens)
                chosen_token = self.handle_logits(logits, model)

            if len(self.__futurs_params) == 2:
                self.__chosen_param = []
                if self.__futurs_params[1] == 'string':
                    stop: str = '"'
                else:
                    stop = '}'
                self.init_autor_tokens()
                while stop not in value_by_token(chosen_token, self.__voc):
                    logits = model.get_logits_from_input_ids(
                        self.__request_tokens)
                    chosen_token = self.handle_logits(logits, model)
                    self.add_token(chosen_token, self.__request_tokens)
                    print(model.decode(self.__request_tokens))
                param_str: str = "".join(model.decode(self.__chosen_param))
                add_parameters(self.__final_dicts, prompt,
                               self.__futurs_params[0], param_str)
                self.__request_tokens[len(self.__request_tokens) - 1] =\
                    check_last_token(
                    self.__futurs_params[1], chosen_token, self.__voc)
                print(model.decode(self.__request_tokens))
                del self.__futurs_params[0:2]

    def search_params_type(self, model: Small_LLM_Model) -> dict | None:
        func_name: str = "".join(model.decode(self.__chosen_func))
        return [
            func.get('parameters') for func in self.__functions_dict
            if func.get('name') == func_name
        ][0]

    def handle_logits(self, logits: list[float],
                      model: Small_LLM_Model) -> int:

        logits_np: list[float] = np.array(logits)
        mask: list[bool] = np.ones(len(logits_np), dtype=bool)

        if self.__step == 1:
            mask[self.__name_authorized_token] = False

        if self.__step == 2:
            mask[self.__param_authorized_tokens] = False

        logits_np[mask] = -np.inf
        return int(np.argmax(logits_np))

    def get_answer(self) -> list[dict]:
        return self.__final_dicts
