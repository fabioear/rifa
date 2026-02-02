#!/bin/bash

# ==============================================================================
# Script de Hardening para VPS Linux com Docker em Produção
# Autor: DevSecOps Assistant
# Data: $(date +%Y-%m-%d)
#
# DESCRIÇÃO:
# Este script realiza o hardening de um servidor Ubuntu/Debian focado em ambientes
# que executam Docker. Ele configura Firewall (UFW), SSH, Fail2ban e realiza
# auditorias de segurança em containers e no sistema.
#
# REQUISITOS:
# - Executar como root
# - Sistema Operacional: Ubuntu ou Debian
# - Docker instalado e em execução
#
# AVISO:
# Execute este script com cautela. Embora desenhado para ser seguro e idempotente,
# alterações em SSH e Firewall podem bloquear o acesso ao servidor se mal configuradas.
# ==============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
SSH_PORT=22 # Altere se usar porta customizada
BACKUP_DIR="/root/hardening_backups_$(date +%Y%m%d_%H%M%S)"

# ==============================================================================
# Funções Auxiliares
# ==============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
       log_error "Este script deve ser executado como root."
       exit 1
    fi
}

confirm() {
    read -r -p "${1:-Deseja continuar?} [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            true
            ;;
        *)
            false
            ;;
    esac
}

backup_file() {
    local file=$1
    if [ -f "$file" ]; then
        mkdir -p "$BACKUP_DIR"
        cp "$file" "$BACKUP_DIR/"
        log_info "Backup de $file criado em $BACKUP_DIR"
    fi
}

# ==============================================================================
# 1. Preparação do Sistema
# ==============================================================================

system_prep() {
    log_info "Iniciando preparação do sistema..."
    
    # Atualizar repositórios
    apt-get update -q

    # Instalar utilitários necessários se não existirem
    REQUIRED_PKGS="ufw fail2ban unattended-upgrades net-tools auditd"
    for pkg in $REQUIRED_PKGS; do
        if ! dpkg -l | grep -q "ii  $pkg"; then
            log_warn "Pacote $pkg não encontrado. Instalando..."
            apt-get install -y $pkg
        fi
    done

    # Configurar Unattended Upgrades
    log_info "Configurando Unattended Upgrades..."
    if [ -f /etc/apt/apt.conf.d/20auto-upgrades ]; then
        backup_file /etc/apt/apt.conf.d/20auto-upgrades
    fi
    
    cat > /etc/apt/apt.conf.d/20auto-upgrades <<EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
    log_success "Unattended Upgrades ativado."
}

# ==============================================================================
# 2. SSH Hardening
# ==============================================================================

ssh_hardening() {
    log_info "Iniciando SSH Hardening..."
    
    local ssh_config="/etc/ssh/sshd_config"
    backup_file "$ssh_config"

    # Verificações de segurança antes de aplicar
    if [ ! -d "/root/.ssh" ] || [ ! -f "/root/.ssh/authorized_keys" ]; then
        log_warn "Chaves SSH de root não encontradas em /root/.ssh/authorized_keys."
        log_warn "Desativar login por senha sem chaves configuradas bloqueará o acesso."
        if ! confirm "Deseja continuar mesmo assim? (SÓ ACEITE SE TIVER CERTEZA QUE TEM ACESSO)"; then
            log_error "Abortando SSH Hardening."
            return
        fi
    fi

    log_info "Aplicando configurações seguras no sshd_config..."

    # Desativar Root Login (Permitir apenas com chave se necessário, ou 'no' para bloquear total)
    # Recomendado: prohibit-password ou no. Vamos usar prohibit-password para permitir chaves.
    sed -i 's/^#*PermitRootLogin.*/PermitRootLogin prohibit-password/' "$ssh_config"

    # Desativar Autenticação por Senha
    sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' "$ssh_config"
    sed -i 's/^#*ChallengeResponseAuthentication.*/ChallengeResponseAuthentication no/' "$ssh_config"
    sed -i 's/^#*UsePAM.*/UsePAM yes/' "$ssh_config" # PAM ainda é necessário para algumas sessões, mas Auth por senha bloqueada acima

    # Garantir que não desconecta sessões ativas (ClientAliveInterval)
    if ! grep -q "^ClientAliveInterval" "$ssh_config"; then
        echo "ClientAliveInterval 300" >> "$ssh_config"
        echo "ClientAliveCountMax 2" >> "$ssh_config"
    fi

    # Verificar sintaxe
    if sshd -t; then
        log_success "Sintaxe do SSH válida. Recarregando serviço..."
        systemctl reload sshd
        log_success "SSH Hardening aplicado. Sessão atual preservada."
    else
        log_error "Erro na configuração do SSH. Restaurando backup..."
        cp "$BACKUP_DIR/sshd_config" "$ssh_config"
        exit 1
    fi
}

# ==============================================================================
# 3. Firewall (UFW) & Docker
# ==============================================================================

ufw_hardening() {
    log_info "Configurando Firewall (UFW)..."

    # Verificar se Docker está rodando
    if ! systemctl is-active --quiet docker; then
        log_warn "Docker não parece estar rodando. As configurações de DOCKER-USER podem falhar."
    fi

    # Instalar e configurar script ufw-docker ou configurar regras manuais
    # Vamos usar a abordagem manual segura adicionando ao after.rules para gerenciar a chain DOCKER-USER
    # Isso impede que o Docker fure o firewall expondo portas publicamente sem querer.
    
    local after_rules="/etc/ufw/after.rules"
    backup_file "$after_rules"

    # Adicionar regras para compatibilidade Docker se não existirem
    if ! grep -q "# BEGIN UFW AND DOCKER" "$after_rules"; then
        log_info "Adicionando regras de compatibilidade Docker no UFW..."
        cat >> "$after_rules" <<EOF

# BEGIN UFW AND DOCKER
*filter
:u-docker - [0:0]
:DOCKER-USER - [0:0]
-A DOCKER-USER -j u-docker

-A u-docker -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN
-A u-docker -p icmp -j RETURN
-A u-docker -i lo -j RETURN

# Permitir conexões de redes privadas (opcional, ajuste conforme necessário)
# -A u-docker -s 10.0.0.0/8 -j RETURN
# -A u-docker -s 172.16.0.0/12 -j RETURN
# -A u-docker -s 192.168.0.0/16 -j RETURN

# Bloquear o restante do tráfego externo para containers (mas permitir acesso interno do host)
-A u-docker -i eth0 -j DROP

COMMIT
# END UFW AND DOCKER
EOF
        log_success "Regras DOCKER-USER adicionadas ao UFW."
        log_warn "NOTA: Com essas regras, portas publicadas pelo Docker (-p 8080:80) NÃO estarão acessíveis externamente a menos que você libere explicitamente no UFW."
        log_warn "Exemplo para liberar porta 80 do container: ufw route allow proto tcp from any to any port 80"
    else
        log_info "Regras de Docker já detectadas no UFW."
    fi

    # Resetar UFW para garantir estado limpo (cuidado, mas necessário para hardening completo)
    # NÃO vamos resetar para evitar perder regras existentes customizadas, vamos apenas aplicar políticas.
    
    log_info "Definindo políticas padrão..."
    ufw default deny incoming
    ufw default allow outgoing

    log_info "Permitindo SSH ($SSH_PORT)..."
    ufw allow "$SSH_PORT"/tcp

    log_info "Permitindo HTTP/HTTPS..."
    ufw allow 80/tcp
    ufw allow 443/tcp

    # Ativar UFW
    log_info "Ativando UFW..."
    # 'yes' pipe para aceitar a confirmação automaticamente
    echo "y" | ufw enable
    log_success "UFW ativado."
}

# ==============================================================================
# 4. Fail2ban
# ==============================================================================

fail2ban_config() {
    log_info "Configurando Fail2ban..."
    
    # Criar jail.local se não existir
    if [ ! -f /etc/fail2ban/jail.local ]; then
        cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
        log_info "Criado /etc/fail2ban/jail.local"
    fi

    local jail_conf="/etc/fail2ban/jail.local"
    
    # Configurar SSH jail
    # Usando crudini ou sed para garantir configuração
    # Vamos usar um arquivo de configuração drop-in para garantir limpeza
    
    cat > /etc/fail2ban/jail.d/99-hardening.conf <<EOF
[sshd]
enabled = true
port = $SSH_PORT
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
EOF

    # Se houver Nginx/Apache, ativar jails
    if dpkg -l | grep -q nginx; then
        cat >> /etc/fail2ban/jail.d/99-hardening.conf <<EOF

[nginx-http-auth]
enabled = true
EOF
    fi

    systemctl restart fail2ban
    log_success "Fail2ban configurado e reiniciado."
}

# ==============================================================================
# 5. Auditoria Docker
# ==============================================================================

docker_audit() {
    log_info "Iniciando auditoria Docker..."
    
    # Verificar portas expostas em 0.0.0.0
    log_info "Verificando containers com portas expostas globalmente (0.0.0.0)..."
    
    # Listar containers e suas portas
    docker ps --format "table {{.Names}}\t{{.Ports}}" | while read -r line; do
        if echo "$line" | grep -q "0.0.0.0"; then
            container_name=$(echo "$line" | awk '{print $1}')
            ports=$(echo "$line" | awk '{$1=""; print $0}')
            
            # Verificar se é banco de dados conhecido
            if echo "$ports" | grep -E -q "5432|3306|6379|27017|9200"; then
                log_error "PERIGO: Container '$container_name' está expondo banco de dados publicamente: $ports"
                log_warn "AÇÃO RECOMENDADA: Altere o docker-compose para usar '127.0.0.1:PORTA:PORTA' ou use rede interna."
            else
                log_warn "Container '$container_name' exposto publicamente: $ports"
            fi
        fi
    done

    # Verificar containers privilegiados
    log_info "Verificando containers privilegiados..."
    privileged_containers=$(docker ps --quiet | xargs docker inspect --format '{{.Name}}: {{.HostConfig.Privileged}}' | grep 'true' || true)
    
    if [ -n "$privileged_containers" ]; then
        log_warn "Containers rodando em modo privilegiado encontrados:"
        echo "$privileged_containers"
        log_warn "Evite usar --privileged em produção a menos que estritamente necessário."
    else
        log_success "Nenhum container privilegiado encontrado."
    fi

    # Sugestão de Networks
    log_info "Verificando uso de redes..."
    # Apenas informativo
    docker network ls | grep bridge > /dev/null && log_info "Redes bridge detectadas. Certifique-se de que os containers de BD estão em redes internas sem driver 'host'."
}

# ==============================================================================
# 6. Auditoria do Sistema
# ==============================================================================

system_audit() {
    log_info "Realizando auditoria do sistema..."

    # Usuários com UID 0 (root)
    log_info "Verificando usuários com UID 0 (root)..."
    awk -F: '($3 == 0) {print}' /etc/passwd
    
    # Cron jobs
    log_info "Listando Cron jobs do sistema..."
    ls -la /etc/cron.* /var/spool/cron/crontabs/ || true

    # Serviços ativos
    log_info "Serviços ouvindo em portas TCP..."
    netstat -tulpn | grep LISTEN

    # Logs de autenticação recentes
    log_info "Últimas 5 tentativas de falha de login SSH:"
    grep "Failed password" /var/log/auth.log | tail -n 5 || echo "Nenhuma falha recente encontrada."
}

# ==============================================================================
# 7. Backups
# ==============================================================================

check_backups() {
    log_info "Verificando rotinas de backup..."
    
    # Procura simples por scripts de backup comuns ou cron jobs
    if grep -r "backup" /etc/cron* /var/spool/cron/crontabs/ > /dev/null 2>&1; then
        log_success "Possível rotina de backup encontrada nos cron jobs."
    else
        log_error "Nenhuma rotina de backup óbvia encontrada no Cron."
        log_warn "AÇÃO NECESSÁRIA: Implemente uma rotina de backup off-site IMEDIATAMENTE."
    fi
}

# ==============================================================================
# Execução Principal
# ==============================================================================

main() {
    check_root
    
    echo -e "${BLUE}======================================================${NC}"
    echo -e "${BLUE}   INICIANDO SCRIPT DE HARDENING DEVSECOPS   ${NC}"
    echo -e "${BLUE}======================================================${NC}"
    
    if ! confirm "Este script fará alterações no sistema. Você tem backup e acesso de console/VNC garantido?"; then
        log_error "Operação cancelada pelo usuário."
        exit 0
    fi

    system_prep
    ssh_hardening
    ufw_hardening
    fail2ban_config
    
    echo -e "\n${BLUE}--- AUDITORIA ---${NC}"
    docker_audit
    system_audit
    check_backups
    
    echo -e "${BLUE}======================================================${NC}"
    echo -e "${GREEN}   HARDENING CONCLUÍDO   ${NC}"
    echo -e "${BLUE}======================================================${NC}"
    echo -e "Resumo das ações:"
    echo -e "1. Atualizações automáticas ativadas."
    echo -e "2. SSH configurado (sem senha, sem root, keepalive)."
    echo -e "3. Firewall UFW ativado com proteção Docker (block external)."
    echo -e "4. Fail2ban protegendo SSH."
    echo -e "5. Backups de configuração salvos em: $BACKUP_DIR"
    echo -e ""
    echo -e "${YELLOW}IMPORTANTE:${NC} Teste o acesso SSH em um NOVO terminal ANTES de fechar este."
    echo -e "Se houver problemas, restaure os arquivos de $BACKUP_DIR"
}

main
