#!/usr/bin/env python3
"""
Script para corrigir todos os parse_mode problemáticos
"""

import os
import re

def fix_parse_modes(directory):
    """Remove parse_mode=ParseMode.MARKDOWN problemático"""
    count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Padrões para corrigir
                    patterns = [
                        # Remove parse_mode=ParseMode.MARKDOWN de edit_message_text
                        (r',\s*parse_mode=ParseMode\.MARKDOWN\s*\)', ')'),
                        # Remove parse_mode=ParseMode.MARKDOWN de reply_text/reply_photo
                        (r',\s*parse_mode=ParseMode\.MARKDOWN(?=\s*\))', ''),
                        # Remove parse_mode standalone
                        (r'\s*,\s*parse_mode=ParseMode\.MARKDOWN', ''),
                    ]
                    
                    original_content = content
                    
                    for pattern, replacement in patterns:
                        content = re.sub(pattern, replacement, content)
                    
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        count += 1
                        print(f"✅ Corrigido: {file_path}")
                        
                except Exception as e:
                    print(f"❌ Erro em {file_path}: {e}")
    
    return count

def main():
    """Função principal"""
    print("🔧 CORRIGINDO PARSE_MODE PROBLEMÁTICOS...")
    print("=" * 50)
    
    src_dir = "/workspace/src"
    fixed_count = fix_parse_modes(src_dir)
    
    print(f"\n📊 RESULTADO:")
    print(f"✅ {fixed_count} arquivos corrigidos")
    print("\n🎉 Todos os parse_mode problemáticos foram removidos!")

if __name__ == "__main__":
    main()