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

from re import Pattern, compile, sub
from typing import cast
from .model import FunctionModel
from .initiate_request import (init_dict, init_name, init_parameters,
                               param_question_one, param_question_two)
from .add_functions import add_string, add_token_one, add_token_two
from .errors import FormatError
from .handle_logit import handle_logits
from pydantic import BaseModel, PrivateAttr
from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
from .utils import (value_by_token, check_last_token, add_name, add_parameters)


class FunctionCalling(BaseModel):

    __final_dicts: list[dict[str, str
                             | dict[str, str | int | float]]] = PrivateAttr(
                                 default_factory=list)
    __request_tokens: list[int] = PrivateAttr(default_factory=list)
    __name_valid_token: list[int] = PrivateAttr(default_factory=list)
    __param_valid_tokens: list[int] = PrivateAttr(default_factory=list)
    __chosen_func: list[int] = PrivateAttr(default_factory=list)
    __chosen_param: list[int] = PrivateAttr(default_factory=list)
    __futurs_params: list[str] = PrivateAttr(default_factory=list)
    __voc: dict[str, int] = PrivateAttr(default_factory=dict)
    __step: int = PrivateAttr(default=1)
    __functions_dict: list[dict[
        str, str
        | dict[str, str | dict[str, str]]]] = PrivateAttr(
            default_factory=list)

    def set_voc(self, voc_dict: dict[str, int]) -> None:
        """Store the dict returned by json.load containing the llm vocabulary
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
            if len(self.__name_valid_token) == 0:
                pattern: Pattern[str] = compile(r'^[a-z_"]+$')
                for token_str, token_value in self.__voc.items():
                    if pattern.match(token_str):
                        self.__name_valid_token.append(token_value)

    def set_functions(
        self,
        func_dict: list[dict[str, str
                             | dict[str, str | dict[str, str]]]]
    ) -> None:
        """Store the list of functions dict in the instance variable.

        Args:
            func_dict (list[dict]): The list of function in dict format

        Raises:
            FormatError: If the arg hasn't a list of dict format.
        """
        if isinstance(func_dict, list):
            if (len(func_dict) > 0):
                for dict_f in func_dict:
                    FunctionModel.model_validate(dict_f)
                self.__functions_dict = func_dict
            else:
                raise FormatError(
                    'There must be at least one function in the JSON file.')
        else:
            raise FormatError('Functions list is not in list type')

    def _init_request(self, tokens: list[int], prompt: str,
                      model: Small_LLM_Model) -> None:
        """Initialize the prompt (self.__request_tokens) to the LLM
        according to the step we are.

        Args:
            tokens (list[int]): The beginning of the prompt determined in the
            param_question function.
            prompt (str): The user request.
            model (Small_LLM_Model): The instance of Small_LLM_Model class
        """
        self.__request_tokens = tokens

        if self.__step == 1:
            init_dict(prompt, self.__final_dicts)
            init_name(self.__request_tokens, self.__voc)

        if self.__step == 2:
            init_parameters(self.__request_tokens, self.__voc)
            params: dict[str,
                         dict[str,
                              str]] | None = self.search_params_type(model)
            if not params:
                add_parameters(self.__final_dicts, self.__futurs_params[1],
                               None, None)
            else:
                for key, value in params.items():
                    self.__futurs_params.append(key)
                    self.__futurs_params.append(value.get('type', 'any'))
                if self.__futurs_params[1] == 'string':
                    add_string('"' + self.__futurs_params[0] + '": "',
                               self.__request_tokens, self.__voc)
                else:
                    add_string('"' + self.__futurs_params[0] + '": ',
                               self.__request_tokens, self.__voc)

    def init_autor_tokens(self) -> None:
        """Store the authorized tokens depending on the type of parameter
        searched for.
        """
        self.__param_valid_tokens = []
        if self.__futurs_params[1] == 'string':
            for value in self.__voc.values():
                self.__param_valid_tokens.append(value)
        if self.__futurs_params[1] == 'number':
            if len(self.__futurs_params) >= 4:
                pattern: Pattern[str] = compile(r'^([-0-9.,]+|}}|})$')
            else:
                pattern = compile(r'^([-0-9.]+|}}|})$')
            for token_str, token_value in self.__voc.items():
                if pattern.match(token_str):
                    self.__param_valid_tokens.append(token_value)

    def ask_llm(self, prompt: str, model: Small_LLM_Model) -> None:
        """Main function. It will handle all the process of the request by LLM

        Args:
            prompt (str): The user request
            model (Small_LLM_Model): The instance of Small_LLM_Model class
        """
        self.__step = 1
        self.__chosen_func = []

        # If there are floats with comma instead of dot the LLM is lost
        prompt = sub(r'(\d),(\d)', r'\1.\2', prompt)

        # We configure the prompt to switch to LLM.
        tokens: list[int] = param_question_one(prompt, model,
                                               self.__functions_dict)
        self._init_request(tokens, prompt, model)
        chosen_token: int = 0

        # Step 1 is the name function research.
        if self.__step == 1:
            while '"' not in value_by_token(chosen_token, self.__voc):
                logits: list[float] = model.get_logits_from_input_ids(
                    self.__request_tokens)
                chosen_token = handle_logits(logits, self.__name_valid_token)
                add_token_one(chosen_token, self.__request_tokens, self.__voc,
                              self.__chosen_func)
            func_name: str = "".join(model.decode(self.__chosen_func))
            add_name(self.__final_dicts, func_name)
            self.__step = 2

        # Step 2 is the parameters research
        if self.__step == 2:
            tokens = param_question_two(prompt, model, self.__functions_dict,
                                        self.__chosen_func)
            self._init_request(tokens, prompt, model)
            logits = model.get_logits_from_input_ids(self.__request_tokens)
            chosen_token = handle_logits(logits, self.__param_valid_tokens)

            # If there are more than 1 parameter, the waiting token (stop) will
            # not be the same
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
                    chosen_token = handle_logits(logits,
                                                 self.__param_valid_tokens)
                    add_token_two(chosen_token, self.__request_tokens,
                                  self.__futurs_params, self.__voc,
                                  self.__chosen_param)

                # When we found the parameter, it's added to the final result.
                param_str: str = "".join(model.decode(self.__chosen_param))
                add_parameters(self.__final_dicts, self.__futurs_params[1],
                               self.__futurs_params[0], param_str)

                # We can delete the parameter found and its type
                del self.__futurs_params[0:2]

                # We add tokens to the request depending on the next
                # parameter's type.
                if self.__futurs_params[1] == 'string':
                    add_string('"' + self.__futurs_params[0] + '": "',
                               self.__request_tokens, self.__voc)
                else:
                    add_string('"' + self.__futurs_params[0] + '": ',
                               self.__request_tokens, self.__voc)
                logits = model.get_logits_from_input_ids(self.__request_tokens)
                chosen_token = handle_logits(logits, self.__param_valid_tokens)

            if len(self.__futurs_params) == 2:

                self.__chosen_param = []
                if self.__futurs_params[1] == 'string':
                    stop = '"'
                else:
                    stop = '}'
                self.init_autor_tokens()

                while stop not in value_by_token(chosen_token, self.__voc):
                    logits = model.get_logits_from_input_ids(
                        self.__request_tokens)
                    chosen_token = handle_logits(logits,
                                                 self.__param_valid_tokens)
                    add_token_two(chosen_token, self.__request_tokens,
                                  self.__futurs_params, self.__voc,
                                  self.__chosen_param)

                param_str = "".join(model.decode(self.__chosen_param))
                add_parameters(self.__final_dicts, self.__futurs_params[1],
                               self.__futurs_params[0], param_str)

                self.__request_tokens[len(self.__request_tokens) - 1] =\
                    check_last_token(
                    self.__futurs_params[1], chosen_token, self.__voc)
                del self.__futurs_params[0:2]

    def search_params_type(
            self, model: Small_LLM_Model) -> dict[str, dict[str, str]] | None:
        """Return the dict containing the parameters of the chosen function or
        None if there are none.
        """
        func_name: str = "".join(model.decode(self.__chosen_func))
        parameters_dict: str | dict[str, str
                                    | dict[str, str]] | None = [
                                        func.get('parameters')
                                        for func in self.__functions_dict
                                        if func.get('name') == func_name
                                    ][0]
        if parameters_dict is None or isinstance(parameters_dict, dict):
            return cast(dict[str, dict[str, str]] | None, parameters_dict)
        else:
            raise FormatError("Parameters must be a dictionnary with 'type' as"
                              " key.")

    def get_answer(
            self) -> list[dict[str, str | dict[str, str | int | float]]]:
        return self.__final_dicts
