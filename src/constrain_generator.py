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
import json
import numpy as np
from llm_sdk import Small_LLM_Model


class FunctionCalling():

    def __init__(self):
        self.__prompt: str = '{"prompt": "'
        self.__name: str = '"name": "'
        self.__parameters: str = '"parameters": '
        self.__final_tokens: list[int] = []
        self.__request_tokens: list[int] = []
        self.__name_authorized_id: list[int] = []
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
        pattern = re.compile(r'^[a-z_]+$')
        if isinstance(voc_dict, dict):
            self.__voc = voc_dict
            self.__final_tokens.append(self.__voc.get("["))
            for i, token_str in enumerate(self.__voc.keys()):
                if pattern.match(token_str):
                    self.__name_authorized_id.append(i)

    def set_functions(self, func_dict: dict) -> None:
        if isinstance(func_dict, list[dict]):
            self.__functions_dict = func_dict

    def init_prompt(self, tokens_list: list[int]):
        # Gérer avec une erreur s'il n'y a pas la lettre
        for letter in self.__prompt:
            self.__final_tokens.append(self.__voc.get(letter))
            tokens_list.append(self.__voc.get(letter))
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

    def add_tokens(self, string: str, tokens_list: list[int]):
        for letter in string:
            tokens_list.append(self.__voc.get(letter))
            self.__final_tokens.append(self.__voc.get(letter))
            if self.__step == 1:
                self.__chosen_func.append(self.__voc.get(letter))

    def _init_request(self, tokens: list[int], prompt: str) -> None:
        self.__request_tokens = tokens
        self.init_prompt(self.__request_tokens)
        self.add_tokens(prompt, self.__request_tokens)

    def ask_llm(self, tokens: list[int], prompt: str,
                model: Small_LLM_Model) -> list[int]:
        self._init_request(tokens, prompt)
        logits: list[float] = model.get_logits_from_input_ids(
            self.__request_tokens)
        while self.__bracket_count > 0:
            self.handle_logits(logits, model)

    def search_params_type(self, model: Small_LLM_Model) -> dict | None:
        func_name: str = model.decode(self.__chosen_func).join()
        return [func.get('parameters') for func in self.__functions_dict if
        func.get('name') == func_name ][0]

    def handle_logits(self, logits: list[float],
                      model: Small_LLM_Model) -> int:


        logits_np: list[float] = np.array(logits)
        mask: list[bool] = np.ones(len(logits_np), dtype=bool)

        if self.__step == 1:
            mask[self.__name_authorized_id] = False
            logits_np[mask] = -np.inf

        if self.__step == 2:
            params: dict = self.search_params_type(model)
            if not params:
                return -1
            else:
                for key, value in params.items():
                    
