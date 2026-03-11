# ****************************************************************************#
#                                                                             #
#                                                         :::      ::::::::   #
#    handle_logit.py                                    :+:      :+:    :+:   #
#                                                     +:+ +:+         +:+     #
#    By: bfitte <bfitte@student.42lyon.fr>          +#+  +:+       +#+        #
#                                                 +#+#+#+#+#+   +#+           #
#    Created: 2026/03/11 11:53:28 by bfitte            #+#    #+#             #
#    Updated: 2026/03/11 11:53:51 by bfitte           ###   ########lyon.fr   #
#                                                                             #
# ****************************************************************************#

import numpy as np


def handle_logits(logits: list[float], valid_tokens: list[int]) -> int:
    """_summary_

    Args:
        logits (list[float]): _description_

    Returns:
        int: _description_
    """
    logits_np: list[float] = np.array(logits)
    mask: list[bool] = np.ones(len(logits_np), dtype=bool)

    mask[valid_tokens] = False

    logits_np[mask] = -np.inf
    return int(np.argmax(logits_np))
