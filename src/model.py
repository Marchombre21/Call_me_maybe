# ****************************************************************************#
#                                                                             #
#                                                         :::      ::::::::   #
#    model.py                                           :+:      :+:    :+:   #
#                                                     +:+ +:+         +:+     #
#    By: bfitte <bfitte@student.42lyon.fr>          +#+  +:+       +#+        #
#                                                 +#+#+#+#+#+   +#+           #
#    Created: 2026/03/02 14:51:06 by bfitte            #+#    #+#             #
#    Updated: 2026/03/02 14:51:07 by bfitte           ###   ########lyon.fr   #
#                                                                             #
# ****************************************************************************#

from pydantic import BaseModel, Field, ValidationError


class TestModel(BaseModel):
    name: str = Field(min_length=3)
    age: int = Field(ge=18)
