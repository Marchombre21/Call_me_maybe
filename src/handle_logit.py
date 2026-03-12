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
from numpy.typing import NDArray


def handle_logits(logits: list[float], valid_tokens: list[int]) -> int:
    """Applies a mask to the logit table to add -infinity to the logits of
    unauthorized tokens.

    Returns:
        int: The position of the biggest logit.
    """
    logits_np: NDArray[np.float64] = np.array(logits)
    mask: NDArray[np.bool_] = np.ones(len(logits_np), dtype=bool)

    mask[valid_tokens] = False

    logits_np[mask] = -np.inf
    return int(np.argmax(logits_np))
