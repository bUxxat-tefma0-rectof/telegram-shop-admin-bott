#!/usr/bin/env python3
"""
Script para substituir edit_message_text por safe_edit_message no store bot
"""

import re

def fix_store_edits():
    """Substitui edit_message_text por safe_edit_message no store bot"""
    file_path = "/workspace/src/store_bot/handlers.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Padrão para encontrar await query.edit_message_text(
        pattern = r'await\s+query\.edit_message_text\s*\(\s*([^,]+)(?:,\s*(reply_markup=[^)]+))?\s*\)'
        
        def replacement(match):
            text = match.group(1)
            reply_markup = match.group(2) if match.group(2) else None
            
            if reply_markup:
                return f'await self.safe_edit_message(query, {text}, {reply_markup})'
            else:
                return f'await self.safe_edit_message(query, {text})'
        
        content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Store bot corrigido: {file_path}")
            return True
        else:
            print("❌ Nenhuma alteração necessária")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 CORRIGINDO EDIT_MESSAGE_TEXT NO STORE BOT...")
    print("=" * 50)
    
    if fix_store_edits():
        print("\n🎉 Store bot corrigido com sucesso!")
    else:
        print("\n⚠️ Nenhuma correção aplicada")

if __name__ == "__main__":
    main()