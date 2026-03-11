# ****************************************************************************#
#                                                                             #
#                                                         :::      ::::::::   #
#    errors.py                                          :+:      :+:    :+:   #
#                                                     +:+ +:+         +:+     #
#    By: bfitte <bfitte@student.42lyon.fr>          +#+  +:+       +#+        #
#                                                 +#+#+#+#+#+   +#+           #
#    Created: 2026/03/10 15:49:02 by bfitte            #+#    #+#             #
#    Updated: 2026/03/10 15:49:03 by bfitte           ###   ########lyon.fr   #
#                                                                             #
# ****************************************************************************#

class FileError(Exception):
    def __init__(self, path: str = None, details: str = None):
        message: str = f'A problem occured with {path}.\n'
        if details:
            message += details
        super().__init__(message)


class JSONError(FileError):
    def __init__(self, details: str, path: str):
        super().__init__(path, details)


class FormatError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class UnknownCharacterError(Exception):
    def __init__(self, letter: str):
        message: str = f'The \'{letter}\' is not used in this model.'
        super().__init__(message)


class MissingParameters(Exception):
    def __init__(self, *args):
        super().__init__(*args)
