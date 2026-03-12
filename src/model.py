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

from pydantic import BaseModel, Field, field_validator
from .errors import FormatError


class FunctionModel(BaseModel):
    name: str = Field(pattern=r'^[a-z_"]+$')
    description: str = Field(min_length=15)
    parameters: dict[str, dict[str, str]] | None = Field(None)
    returns: dict[str, str] | None = Field(None)

    @field_validator('parameters', mode='after')
    @classmethod
    def check_parameters(
            cls, value: dict[str, str] | None) -> dict[str, str] | None:
        if value is None:
            return value
        for key, value_d in value.items():
            if not isinstance(key, str):
                raise FormatError('Keys of parameters dict must be'
                                  ' strings')
            if not isinstance(value_d, dict):
                raise FormatError('Values of keys parameters must be a'
                                  ' dict')
            for key_p, value_p in value_d.items():
                if key_p != 'type':
                    raise FormatError('The key of the dict of parameter value'
                                      ' must be "type".')
                if value_p not in ['number', 'string']:
                    raise FormatError('The value of the type parameter in'
                                      ' function dict must be either "number"'
                                      ' or "string".')
        return value
