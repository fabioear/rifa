# WhatsApp (Twilio) – Configuração Rápida

- Credenciais (variáveis de ambiente):
  - TWILIO_ACCOUNT_SID
  - TWILIO_AUTH_TOKEN
  - TWILIO_FROM_NUMBER (ex.: whatsapp:+14155238886)
  - TWILIO_ENABLED=true|false
  - TWILIO_TEMPLATE_NEW_RIFA (Content SID do template nova_rifa_disponivel)
  - TWILIO_TEMPLATE_WINNER (Content SID do template usuario_ganhador)

- Desativar envio em teste:
  - Defina TWILIO_ENABLED=false para evitar qualquer disparo real.

- Rodar testes de falha da apuração:

```bash
pytest backend/tests/test_apuracao_failures.py
```

