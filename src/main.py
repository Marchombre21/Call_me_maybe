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

from llm_sdk.llm_sdk import Small_LLM_Model


def main() -> None:
    truc: Small_LLM_Model = Small_LLM_Model()
    print(truc.encode("Je suis Bruno"))


main()
