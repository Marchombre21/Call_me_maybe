# ****************************************************************************#
#                                                                             #
#                                                         :::      ::::::::   #
#    main.py                                            :+:      :+:    :+:   #
#                                                     +:+ +:+         +:+     #
#    By: bfitte <bfitte@student.42lyon.fr>          +#+  +:+       +#+        #
#                                                 +#+#+#+#+#+   +#+           #
#    Created: 2026/03/02 12:44:35 by bfitte            #+#    #+#             #
#    Updated: 2026/03/02 12:45:31 by bfitte           ###   ########lyon.fr   #
#                                                                             #
# ****************************************************************************#

import json
from src import FunctionCalling
from llm_sdk import Small_LLM_Model
# from src import TestModel, ValidationError


def main() -> None:
    print("Initiate model...")
    model: Small_LLM_Model = Small_LLM_Model()
    print("Model initiated.")
    path_dic: str = model.get_path_to_vocab_file()
    caller: FunctionCalling = FunctionCalling()
    prompts: list[str] = []

    with open(path_dic, "r") as f:
        caller.set_voc(json.load(f))
    with open("data/input/functions_definition.json", "r") as f:
        caller.set_functions(json.load(f))
    with open("data/input/function_calling_tests.json", "r") as f:
        for ask in json.load(f):
            for value in ask.values():
                prompts.append(value)
    for i, prompt in enumerate(prompts):
        print(f"appel {i + 1}")
        caller.ask_llm(prompt, model)
    print(model.decode(caller.get_answer()))


main()
