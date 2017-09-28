#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
This file contains an easy to use Author class so to be able to extend
author instances with easy to access methods
"""


class Author:

    def __init__(self, _id, name):

        self.id = _id
        self.name = name
