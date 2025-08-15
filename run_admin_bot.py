#!/usr/bin/env python3
"""
Script principal para executar o Bot Administrativo
"""

import os
import sys

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from admin_bot.bot import main

if __name__ == "__main__":
    main()