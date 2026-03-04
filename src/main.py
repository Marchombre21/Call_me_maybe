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
from llm_sdk import Small_LLM_Model
# from src import TestModel, ValidationError


def main() -> None:
    print("Initiate model...")
    model: Small_LLM_Model = Small_LLM_Model()
    print("Model initiated.")
    with open("data/input/function_calling_tests.json", "r") as f:
        print(json.loads(f.read()))
    # result = model.encode("Comment allez-vous?")
    # print(result)
    # print(model.get_logits_from_input_ids(result[0].tolist()))

    # test: dict = {"name": "Bruno", "age": 19}
    # try:
    #     test1: TestModel = TestModel(**test)
    #     print(test1.name)
    # except (ValidationError) as e:
    #     print(e)


main()
