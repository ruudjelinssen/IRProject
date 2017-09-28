#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
This file contains the code to launch a Java VM instance and check for any exceptions that
may occur while doing so, such as an instance already being launched in the current scope.
"""

import lucene


class JavaVM:

    @staticmethod
    def init_vm():
        """Attempt to initialise the Java VM"""
        try:
            lucene.initVM(vmargs=['-Djava.awt.headless=true'])
            print('Launched apache lucene virtual Java instance running at', lucene.VERSION)
        except ValueError:
            print('Java VM already running - will not launch again')