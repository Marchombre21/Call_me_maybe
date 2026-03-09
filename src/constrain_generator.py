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


class FunctionCalling():

    def __init__(self):
        self.__prompt: str = "{'prompt': \""
        self.__name: str = '"name":"'
        self.__parameters: str = "'parameters':{"
        self.__final_tokens: list[int] = []
        self.__request_tokens: list[int] = []
        self.__name_authorized_token: list[int] = []
        self.__param_authorized_tokens: list[int] = []
        self.__chosen_func: list[int] = []
        self.__futurs_params: list[str] = []
        self.__voc: dict = {}
        self.__bracket_count: int = 0
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
            self.__final_tokens.append(self.__voc.get("["))
            if len(self.__name_authorized_token) == 0:
                pattern: Pattern = re.compile(r'^[a-z_"]+$')
                for token_str, token_value in self.__voc.items():
                    if pattern.match(token_str):
                        self.__name_authorized_token.append(token_value)

    def set_functions(self, func_dict: dict) -> None:
        if isinstance(func_dict, list):
            self.__functions_dict = func_dict

    def init_prompt(self, prompt: str):
        # Gérer avec une erreur s'il n'y a pas la lettre
        for letter in self.__prompt:
            self.__final_tokens.append(self.__voc.get(letter))
        for letter in prompt + '",':
            self.__final_tokens.append(self.__voc.get(letter))
        self.__bracket_count += 1

    def init_name(self, tokens_list: list[int]):
        # Gérer avec une erreur s'il n'y a pas la lettre
        for letter in self.__name:
            self.__final_tokens.append(self.__voc.get(letter))
            tokens_list.append(self.__voc.get(letter))

    def init_parameters(self, tokens_list: list[int]):
        # Gérer avec une erreur s'il n'y a pas la lettre
        for letter in self.__parameters:
            self.__final_tokens.append(self.__voc.get(letter))
            tokens_list.append(self.__voc.get(letter))

    def add_string(self, string: str, tokens_list: list[int]):
        for letter in string:
            tokens_list.append(self.__voc.get(letter))
            self.__final_tokens.append(self.__voc.get(letter))

    def add_token(self, token: int, tokens_list: list[int]):
        tokens_list.append(token)
        self.__final_tokens.append(token)
        if self.__step == 1 and token != self.__voc.get('"'):
            self.__chosen_func.append(token)

    def _init_request(self, tokens: list[int], prompt: str,
                      model: Small_LLM_Model) -> None:

        self.__request_tokens = tokens

        if self.__step == 1:
            self.init_prompt(prompt)
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
                    self.add_string('\'' + self.__futurs_params[0] + '\':"',
                                    self.__request_tokens)
                else:
                    self.add_string('\'' + self.__futurs_params[0] + '\':',
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
            # print(func_name)
            func_dic: dict = [
                func for func in self.__functions_dict
                if func.get('name') == func_name
            ][0]

            # functions_list: list = [{
            #     "description": func_dic.get('description'),
            #     "parameters": func_dic.get('parameters')
            # }]
            # func_s: str = json.dumps(functions_list)
            # tokens = model.encode(
            #     f'Request:"{prompt}"\nDef function:{func_s}\n'
            #     'JSON: {').tolist()[0]

            # func_desc: str = func_dic.get('description')
            # param_names: list[str] = func_dic.get('parameters').keys()
            # params_str: str = "'" + "', '".join(param_names) + "'"
            # tokens = model.encode(
            #     f'Request:"{prompt}"\nDef function:{func_desc}\n'
            #     'Task:Provide the correct values for the parameters'
            #     f' {params_str} to fullfill the request\n'
            #     'JSON: {').tolist()[0]

            tokens = model.encode(
                f'{prompt}\n{json.dumps(func_dic)}\n'
                'JSON: {').tolist()[0]

        return tokens

    def init_autor_tokens(self):
        self.__param_authorized_tokens = []
        if self.__futurs_params[1] == 'string':
            for key, value in self.__voc.items():
                if ('"' not in key or key == '"') and\
                        (',' not in key or key == ','):
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
        chosen_token: int = -1
        print(prompt)

        if self.__step == 1:
            print("1")
            while chosen_token != self.__voc.get('"'):
                logits: list[float] = model.get_logits_from_input_ids(
                    self.__request_tokens)
                chosen_token = self.handle_logits(logits, model)
                self.add_token(chosen_token, self.__request_tokens)
            self.add_string(',', self.__request_tokens)
            self.__step = 2

        if self.__step == 2:
            print("2")
            tokens = self.param_question(prompt, model)
            self._init_request(tokens, prompt, model)
            logits: list[float] = model.get_logits_from_input_ids(
                self.__request_tokens)
            chosen_token = self.handle_logits(logits, model)

            # print(model.decode(self.__request_tokens))
            while len(self.__futurs_params) >= 4:
                print("4 params")
                self.init_autor_tokens()
                if self.__futurs_params[1] == 'string':
                    stop: str = self.__voc.get('"')
                else:
                    stop = self.__voc.get(',')

                while chosen_token != stop:
                    logits = model.get_logits_from_input_ids(
                        self.__request_tokens)
                    chosen_token = self.handle_logits(logits, model)
                    self.add_token(chosen_token, self.__request_tokens)
                    print(model.decode(self.__request_tokens))
                    print()
                del self.__futurs_params[0:2]
                if self.__futurs_params[1] == 'string':
                    self.add_string(',\'' + self.__futurs_params[0] + '\':"',
                                    self.__request_tokens)
                else:
                    self.add_string('\'' + self.__futurs_params[0] + '\':',
                                    self.__request_tokens)
                logits = model.get_logits_from_input_ids(self.__request_tokens)
                chosen_token = self.handle_logits(logits, model)

            if len(self.__futurs_params) == 2:
                print("2 params")
                if self.__futurs_params[1] == 'string':
                    stop: str = self.__voc.get('"')
                    stop2: str = stop
                else:
                    stop = self.__voc.get('}}')
                    stop2 = self.__voc.get('}')
                self.init_autor_tokens()
                # print("token choisi", chosen_token)
                # print("token stop", self.__voc.get(stop))
                while chosen_token != stop and chosen_token != stop2:
                    logits = model.get_logits_from_input_ids(
                        self.__request_tokens)
                    chosen_token = self.handle_logits(logits, model)
                    self.add_token(chosen_token, self.__request_tokens)
                    print(model.decode(self.__request_tokens))
                    print()
                if self.__futurs_params[1] == 'string':
                    self.add_string('}', self.__request_tokens)
                self.add_string(',', self.__request_tokens)
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
        return np.argmax(logits_np)

    def get_answer(self) -> list[int]:
        self.__final_tokens.pop()
        self.__final_tokens.append(self.__voc.get("]"))
        return self.__final_tokens
