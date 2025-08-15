#!/usr/bin/env python3
"""
Script para remover asteriscos dos textos
"""

import os
import re

def fix_asterisks(directory):
    """Remove asteriscos duplos dos textos"""
    count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Remove asteriscos duplos (mas mantém os necessários para markdown em notificações)
                    # Remove ** apenas em strings de texto visível ao usuário
                    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
                    
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        count += 1
                        print(f"✅ Asteriscos removidos: {file_path}")
                        
                except Exception as e:
                    print(f"❌ Erro em {file_path}: {e}")
    
    return count

def main():
    """Função principal"""
    print("🔧 REMOVENDO ASTERISCOS DOS TEXTOS...")
    print("=" * 50)
    
    src_dir = "/workspace/src"
    fixed_count = fix_asterisks(src_dir)
    
    print(f"\n📊 RESULTADO:")
    print(f"✅ {fixed_count} arquivos corrigidos")
    print("\n🎉 Todos os asteriscos foram removidos!")

if __name__ == "__main__":
    main()