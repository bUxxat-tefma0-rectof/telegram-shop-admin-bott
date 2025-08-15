# 🤖 Sistema de Bots Telegram - Loja Digital

Sistema completo de bots para Telegram com funcionalidades de loja digital, sistema de afiliados, pagamentos PIX e painel administrativo.

## 📋 Funcionalidades

### 🎯 Bot Administrativo
- **Dashboard completo** com métricas em tempo real
- **Gestão de produtos** e estoque
- **Configuração de pagamentos** PIX (manual e automático)
- **Sistema de afiliados** configurável
- **Gestão de usuários** e administradores
- **Transmissão de mensagens** em massa
- **Logs e relatórios** detalhados
- **Modo manutenção** ativável

### 🛒 Bot da Loja
- **Catálogo de produtos** com sistema de busca
- **Compras automáticas** com entrega instantânea
- **Sistema de recarga** via PIX
- **Perfil do usuário** com histórico
- **Rankings** de vendas e usuários
- **Sistema de afiliados** com links únicos
- **Alertas de estoque** personalizáveis
- **Suporte integrado**

### 💳 Sistema de Pagamentos
- **PIX automático** via Mercado Pago
- **PIX manual** para aprovação administrativa
- **Webhooks** para confirmação automática
- **Controle de limites** mínimo e máximo
- **Bônus de depósito** configurável

### 👥 Sistema de Afiliados
- **Links únicos** de afiliação
- **Pontos por indicação**
- **Conversão de pontos** em saldo
- **Relatórios de performance**

## 🚀 Instalação

### 1. Pré-requisitos
```bash
# Python 3.8 ou superior
python --version

# Git
git --version
```

### 2. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/sistema-bots-telegram.git
cd sistema-bots-telegram
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configuração

#### 4.1. Crie os Bots no Telegram
1. Acesse [@BotFather](https://t.me/BotFather) no Telegram
2. Crie dois bots:
   - Um para administração (`/newbot`)
   - Um para a loja (`/newbot`)
3. Anote os tokens de cada bot

#### 4.2. Configure o Mercado Pago (Opcional)
1. Acesse [Mercado Pago Developers](https://www.mercadopago.com.br/developers)
2. Crie uma aplicação
3. Obtenha o Access Token

#### 4.3. Configure as Variáveis de Ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env
nano .env
```

Preencha as variáveis no arquivo `.env`:
```env
# Bot Tokens
ADMIN_BOT_TOKEN=seu_token_do_bot_admin_aqui
STORE_BOT_TOKEN=seu_token_do_bot_loja_aqui

# Mercado Pago
MERCADO_PAGO_TOKEN=seu_token_mercado_pago_aqui

# Configurações do Bot
ADMIN_USER_ID=seu_id_telegram_aqui
OWNER_USER_ID=seu_id_telegram_aqui

# Database
DATABASE_PATH=./database/bot_database.db

# Configurações Gerais
SUPPORT_LINK=https://t.me/seu_suporte
SEPARATOR====
LOG_DESTINATION=seu_chat_id_para_logs

# Configurações de Pagamento
MIN_DEPOSIT=1.00
MAX_DEPOSIT=1000.00
PIX_EXPIRATION_TIME=30
DEPOSIT_BONUS=0
MIN_DEPOSIT_FOR_BONUS=50.00

# Configurações de Afiliados
MIN_POINTS_TO_CONVERT=400
POINTS_MULTIPLIER=0.01
POINTS_PER_RECHARGE=10
AFFILIATE_SYSTEM_ENABLED=true

# Configurações de Registro
REGISTRATION_BONUS=0.00

# Modo Manutenção
MAINTENANCE_MODE=false
```

### 5. Execução

#### 5.1. Executar Apenas o Bot Administrativo
```bash
python run_admin_bot.py
```

#### 5.2. Executar Apenas o Bot da Loja
```bash
python run_store_bot.py
```

#### 5.3. Executar Ambos os Bots
```bash
python run_both_bots.py
```

## 📖 Guia de Uso

### 🔧 Bot Administrativo

#### Primeiro Acesso
1. Inicie o bot admin: `/start`
2. Acesse o dashboard: `/admin`
3. Configure as opções básicas em **Configurações**

#### Adicionando Produtos
1. Va em **Configurações > Configurar Logins**
2. Clique em **Adicionar Login**
3. Envie no formato: `NOME===PREÇO===DESCRIÇÃO===EMAIL===SENHA===DURAÇÃO`

Exemplo:
```
NETFLIX===15.00===Netflix Premium===user@email.com===senha123===30
```

#### Configurando Pagamentos
1. **PIX Automático:**
   - Configure o token do Mercado Pago
   - Ative o PIX automático
   - Configure webhook (opcional)

2. **PIX Manual:**
   - Desative o PIX automático
   - Aprove pagamentos manualmente

#### Gestão de Usuários
- **Transmitir mensagens:** Envie para todos os usuários
- **Pesquisar usuário:** Busque por ID
- **Configurar bônus:** Defina bônus de registro

### 🛒 Bot da Loja

#### Para Usuários
1. **Registro:** `/start`
2. **Recarregar saldo:** Botão "Recarga" ou `/pix VALOR`
3. **Comprar produtos:** Navegue pelos produtos disponíveis
4. **Ver histórico:** `/historico`
5. **Sistema de afiliados:** `/afiliados`

#### Comandos Disponíveis
- `/start` - Menu principal
- `/pix VALOR` - Recarga rápida
- `/historico` - Gera arquivo com histórico
- `/afiliados` - Informações de afiliação
- `/id` - Mostra seu ID
- `/ranking` - Rankings do bot
- `/alertas` - Configura alertas de estoque

## 🏗️ Estrutura do Projeto

```
sistema-bots-telegram/
├── src/
│   ├── admin_bot/          # Bot administrativo
│   │   ├── bot.py         # Aplicação principal
│   │   ├── handlers.py    # Manipuladores de eventos
│   │   └── keyboards.py   # Teclados/botões
│   ├── store_bot/         # Bot da loja
│   │   ├── bot.py         # Aplicação principal
│   │   ├── handlers.py    # Manipuladores de eventos
│   │   └── keyboards.py   # Teclados/botões
│   ├── config/            # Configurações
│   │   └── settings.py    # Configurações centralizadas
│   ├── database/          # Banco de dados
│   │   └── models.py      # Modelos e operações
│   └── utils/             # Utilitários
│       └── payment_system.py # Sistema de pagamentos
├── database/              # Arquivos do banco
├── run_admin_bot.py      # Script do bot admin
├── run_store_bot.py      # Script do bot loja
├── run_both_bots.py      # Script para ambos
├── requirements.txt       # Dependências
├── .env.example          # Exemplo de configuração
└── README.md             # Este arquivo
```

## 🛠️ Configurações Avançadas

### Webhook do Mercado Pago
Para receber confirmações automáticas de pagamento, configure um webhook:

1. **Configure uma URL pública** (use ngrok para testes)
2. **Configure no Mercado Pago:**
   ```
   POST https://api.mercadopago.com/v1/webhooks
   {
     "url": "https://sua-url.com/webhook",
     "events": ["payment"]
   }
   ```

### Backup do Banco de Dados
```bash
# Fazer backup
cp database/bot_database.db database/backup_$(date +%Y%m%d_%H%M%S).db

# Restaurar backup
cp database/backup_YYYYMMDD_HHMMSS.db database/bot_database.db
```

### Logs
Os logs são salvos automaticamente e podem ser configurados no arquivo `settings.py`.

## 🚨 Troubleshooting

### Problemas Comuns

#### Bot não responde
1. Verifique se os tokens estão corretos
2. Confirme se o bot não está em modo manutenção
3. Verifique os logs para erros

#### Pagamentos não funcionam
1. Verifique o token do Mercado Pago
2. Confirme se o PIX está habilitado na conta
3. Teste com PIX manual primeiro

#### Banco de dados com erro
1. Verifique permissões da pasta `database/`
2. Delete o arquivo `.db` para recriar (perderá dados)
3. Restaure de um backup se disponível

### Logs de Debug
Para ativar logs detalhados, edite `settings.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Suporte

- **Documentação:** Este README
- **Issues:** Abra uma issue no GitHub
- **Telegram:** Configure seu link de suporte no `.env`

## 📝 Licença

Este projeto é licenciado sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -m 'Adiciona nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## ⚠️ Aviso Legal

Este sistema é para fins educacionais e comerciais legítimos. Certifique-se de cumprir todas as leis locais e termos de serviço do Telegram e Mercado Pago.

---

**Desenvolvido com ❤️ para a comunidade**