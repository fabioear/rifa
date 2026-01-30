export interface User {
    id: string;
    email: string;
    role: 'admin' | 'player';
    is_active: boolean;
    phone?: string;
    whatsapp_opt_in?: boolean;
    created_at?: string;
    avatar_url?: string;
}

export enum RifaStatus {
    RASCUNHO = "rascunho",
    ATIVA = "ativa",
    ENCERRADA = "encerrada",
    APURADA = "apurada"
}

export enum RifaTipo {
    MILHAR = "milhar",
    CENTENA = "centena",
    DEZENA = "dezena",
    GRUPO = "grupo"
}

export enum RifaLocal {
    PT_RJ = "PT-RJ",
    PTM_RJ = "PTM-RJ",
    CORUJINHA = "Corujinha",
    NACIONAL = "Nacional",
    FEDERAL = "Federal",
    EXTRA = "Extra",
    NOTURNA = "Noturna",
    PERSONALIZADO = "Personalizado"
}

export interface Rifa {
    id: string;
    titulo: string;
    descricao?: string;
    preco_numero: number;
    valor_premio?: number;
    tipo_rifa: RifaTipo;
    local_sorteio: string;
    data_sorteio: string;
    hora_encerramento?: string;
    status: RifaStatus;
    owner_id: string;
    created_at: string;
}

export enum NumeroStatus {
    LIVRE = "livre",
    RESERVADO = "reservado",
    PAGO = "pago",
    EXPIRADO = "expirado",
    CANCELADO = "cancelado"
}

export interface RifaNumero {
    id: string;
    rifa_id: string;
    tipo: RifaTipo;
    numero: string;
    status: NumeroStatus;
    user_id?: string;
    is_owner?: boolean;
    payment_id?: string;
    reserved_until?: string;
}

export type PremioStatus = "PENDING" | "WINNER" | "LOSER";

export interface NumeroComprado {
    numero: string;
    status: NumeroStatus;
    premio_status: PremioStatus;
    data_compra?: string | null;
}

export interface MinhaRifa {
    id: string;
    titulo: string;
    status: RifaStatus;
    data_sorteio: string;
    resultado?: string | null;
    numeros_comprados: NumeroComprado[];
}

export interface AdminSettings {
    id: string;
    user_id: string;
    pix_key?: string;
    pix_tipo?: string;
    nome_recebedor?: string;
    documento_recebedor?: string;
    picpay_account_id?: string;
    picpay_token?: string;
    aceita_pix: boolean;
    aceita_debito: boolean;
    aceita_credito: boolean;
    reserva_timeout_min: number;
}

export interface Sorteio {
    id: string;
    nome: string;
    horario: string;
    ativo: boolean;
}
