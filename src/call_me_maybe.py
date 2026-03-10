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
from argparse import ArgumentParser, Namespace
from src import FunctionCalling
from llm_sdk import Small_LLM_Model
# from src import TestModel, ValidationError


def main() -> None:
    print("Initiate model...")
    model: Small_LLM_Model = Small_LLM_Model()
    print("Model initiated.")

    # Initializing the parser
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument('--functions_definition', help='Path to the function'
                        'definitions file')
    parser.add_argument('--input', help='Path to the prompts file')
    parser.add_argument('--output', help='Path to the output file')
    args: Namespace = parser.parse_args()

    # Initializing the files's paths
    path_dic: str = model.get_path_to_vocab_file()
    path_func_def: str = args.functions_definition if\
        args.functions_definition else "data/input/functions_definition.json"
    path_prompts: str = args.input if args.input else\
        "data/input/function_calling_tests.json"
    path_output: str = args.output if args.output else\
        "data/output/function_calls.json"
    caller: FunctionCalling = FunctionCalling()
    prompts: list[str] = []

    with open(path_dic, "r") as f:
        caller.set_voc(json.load(f))
    with open(path_func_def, "r") as f:
        caller.set_functions(json.load(f))
    with open(path_prompts, "r") as f:
        for ask in json.load(f):
            for value in ask.values():
                prompts.append(value)
    for i, prompt in enumerate(prompts):
        caller.ask_llm(prompt, model)
    with open(path_output, 'w') as f:
        json.dump(caller.get_answer(), f, indent=1)


if __name__ == "__main__":
    main()
