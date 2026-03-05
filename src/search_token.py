# ****************************************************************************#
#                                                                             #
#                                                         :::      ::::::::   #
#    search_token.py                                    :+:      :+:    :+:   #
#                                                     +:+ +:+         +:+     #
#    By: bfitte <bfitte@student.42lyon.fr>          +#+  +:+       +#+        #
#                                                 +#+#+#+#+#+   +#+           #
#    Created: 2026/03/05 10:21:15 by bfitte            #+#    #+#             #
#    Updated: 2026/03/05 10:21:16 by bfitte           ###   ########lyon.fr   #
#                                                                             #
# ****************************************************************************#

def search_by_token(value: int, voc_dict: dict) -> str:
    return [key for key, val in voc_dict.items() if val == value][0]
