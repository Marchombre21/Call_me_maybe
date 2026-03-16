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
from json import JSONDecodeError
from pydantic import ValidationError
from argparse import ArgumentParser, Namespace
from src import FunctionCalling
from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
from .errors import FileError, JSONError, FormatError


def main() -> None:
    print("Initiate model...")
    model: Small_LLM_Model = Small_LLM_Model()
    print("Model initiated.")

    # Initializing the parser
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument('--functions_definition',
                        help='Path to the function'
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
        "data/output/function_calling_results.json"

    # Class instantiation
    caller: FunctionCalling = FunctionCalling()
    prompts: list[str] = []

    # Attempt to recover vocabulary
    try:
        with open(path_dic, "r") as f:
            caller.set_voc(json.load(f))
    except (FileNotFoundError, PermissionError, IsADirectoryError, TypeError)\
            as e:
        raise FileError(path_dic, str(e))

    # Attempt to recover the function definitions
    try:
        with open(path_func_def, "r") as f:
            try:
                caller.set_functions(json.load(f))
            except JSONDecodeError as e:
                raise JSONError(str(e), path_func_def)
    except (FileNotFoundError, PermissionError, IsADirectoryError, TypeError)\
            as e:
        raise FileError(path_func_def, str(e))

    # Attempt to recover requests
    try:
        with open(path_prompts, "r") as f:
            try:
                for ask in json.load(f):
                    if not isinstance(ask, dict):
                        raise FormatError('Requests must be in dict format.')
                    for value in ask.values():
                        if isinstance(value, str) and value != '':
                            prompts.append(value)
                        else:
                            raise FormatError(
                                'The requests must be non-empty strings.')
            except JSONDecodeError as e:
                raise JSONError(str(e), path_prompts)
    except (FileNotFoundError, PermissionError, IsADirectoryError, TypeError)\
            as e:
        raise FileError(path_dic, str(e))

    # We ask the questions to the llm one after the other.
    for i, prompt in enumerate(prompts):
        print(f"Work in progress : {i}/{len(prompts)}. Please wait.")
        caller.ask_llm(prompt.replace('"', "'"), model)

    # Attempt to write the result in a file in JSON format
    try:
        with open(path_output, 'w') as f:
            try:
                json.dump(caller.get_answer(), f, indent=2)
            except JSONDecodeError as e:
                raise JSONError(str(e), path_output)
    except (FileNotFoundError, PermissionError, IsADirectoryError, TypeError)\
            as e:
        raise FileError(path_dic, str(e))
    print("All requests have been processed. Thank you for waiting!")


if __name__ == "__main__":
    try:
        main()
    except (ValidationError) as e:
        for error in e.errors():
            print(f"{error.get('loc')[0]}: {error.get('msg')}")
    except (Exception) as e:
        print(e)
