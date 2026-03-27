# LINKEDIN GROWTH ENGINEER PRO

Sistema avançado em Python para otimização de presença profissional no LinkedIn através de análise comportamental, automação humanizada e aprendizado contínuo.

## 🎯 Objetivos

1. Aumentar visibilidade do perfil
2. Melhorar relevância algorítmica
3. Construir autoridade em PHP, Laravel, Backend e Software Architecture
4. Aprender quais ações geram maior retorno

## 🧩 Arquitetura

O sistema segue os princípios de **Clean Architecture** e é dividido em 5 camadas:

1. **Automation Layer**: Playwright para interações humanizadas.
2. **Intelligence Layer (AI)**: Motor de aprendizado para otimização de ações.
3. **Analytics Layer**: SQLite para armazenamento e métricas de crescimento.
4. **Behavior Simulation Layer**: Simulação de hábitos humanos (delays gaussianos, scroll irregular).
5. **Deployment Layer**: Docker e Docker Compose para fácil implantação em VPS.

## 🚀 Instalação e Execução

### Pré-requisitos

- Docker e Docker Compose instalados.
- Python 3.11+ (para execução local sem Docker).

### ⚙️ Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/your-repo/linkedin-growth-engineer-pro.git
   cd linkedin-growth-engineer-pro
   ```

2. Crie um arquivo `.env` na raiz do projeto, copiando o `.env.example` e preenchendo suas credenciais do LinkedIn:
   ```bash
   cp .env.example .env
   ```
   Edite o arquivo `.env`:
   ```
   LINKEDIN_EMAIL=seu_email@example.com
   LINKEDIN_PASSWORD=sua_senha
   HEADLESS=true # Defina como false para ver o navegador em ação (apenas para depuração)
   ```

### 🏃 Execução Local (com Docker Compose)

Para iniciar o sistema e o dashboard localmente:

```bash
docker-compose up --build -d
```

- O agente de automação (`app` service) será iniciado e executará a rotina diária agendada para 09:00 AM.
- O dashboard (`dashboard` service) estará disponível em `http://localhost:5000`.

Para parar os serviços:

```bash
docker-compose down
```

### 🏃 Execução Local (sem Docker)

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Execute o script principal:
   ```bash
   python3 main.py
   ```
   E o dashboard (em outro terminal):
   ```bash
    python3 -m app.dashboard.dashboard_app
   ```

### ☁️ Deploy em VPS

O sistema é projetado para ser facilmente implantado em qualquer VPS que suporte Docker, como DigitalOcean, Oracle Free Tier, ou outros provedores de baixo custo.

1. Instale Docker e Docker Compose na sua VPS.
2. Copie os arquivos do projeto para a VPS.
3. Navegue até o diretório do projeto na VPS.
4. Execute `docker-compose up --build -d`.

O `app` service executará a rotina agendada e o `dashboard` estará acessível na porta 5000 da sua VPS (certifique-se de que a porta está aberta no firewall).

## 🛡️ Boas Práticas e Limites Seguros

O sistema é construído com foco em **automação humanizada** e **segurança**. Ele inclui:

- **Delays Gaussianos e Scroll Irregular**: Simulações de comportamento humano para evitar detecção.
- **Limites de Ação Diários**: Configurados em `app/core/config.py` para prevenir atividades excessivas.
  - `MAX_ACTIONS_PER_DAY = 20`
  - `MAX_LIKES = 6`
  - `MAX_PROFILE_VISITS = 5`
- **Cooldown Automático**: Pausas entre as ações para maior naturalidade.
- **Rotinas Adaptativas**: Planos de ação diários variados para evitar padrões repetitivos.

**IMPORTANTE**: Este sistema não se destina a automação agressiva, spam ou bypass de segurança do LinkedIn. Use-o com responsabilidade e monitore seu comportamento.

## 🚨 Troubleshooting

- **Problemas de Login**: Verifique suas credenciais no arquivo `.env`. O LinkedIn pode ocasionalmente exigir verificação manual; se isso ocorrer, tente desativar o modo `HEADLESS` para depurar.
- **Erros de Playwright**: Certifique-se de que os browsers do Playwright estão instalados (`playwright install chromium`). Em ambientes Docker, isso é feito automaticamente.
- **Dashboard não aparece**: Verifique se o serviço `dashboard` está rodando (`docker-compose ps`) e se a porta 5000 está acessível (firewall).
- **Rotina não executa**: Verifique os logs do serviço `app` (`docker-compose logs app`) para identificar erros no agendamento ou execução da rotina.

## 🤝 Contribuição

Sinta-se à vontade para abrir issues ou pull requests para melhorias e novas funcionalidades.
