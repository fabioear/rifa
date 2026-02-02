from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db, SessionLocal
from app.models.whatsapp_session import WhatsappSession
from app.models.user import User
from app.models.rifa import Rifa, RifaStatus, RifaTipo
from app.models.rifa_numero import RifaNumero, NumeroStatus
from app.models.rifa_ganhador import RifaGanhador
from app.core.config import settings
from services.whatsapp_service import whatsapp_service
from app.core.security import get_password_hash
from app.core.tenant import get_tenant_by_host_or_default
import logging
import uuid
import secrets
import string
from datetime import datetime, timedelta

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Mensagens ---
MSG_BOAS_VINDAS = """🎰 *Bem-vindo ao Sistema Rifa JB*

Escolha uma opção:
1️⃣ Jogar agora
2️⃣ Ver rifas ativas
3️⃣ Meu histórico
4️⃣ Suporte

_Digite o número da opção desejada._"""

MSG_CADASTRO = """Olá! Não encontramos seu cadastro.
Para continuar, por favor digite seu *Nome Completo*."""

MSG_MODALIDADE = """Escolha a modalidade de jogo:

1️⃣ Grupo
2️⃣ Dezena
3️⃣ Centena
4️⃣ Milhar

0️⃣ Voltar"""

MSG_DIGITE_NUMERO = """Digite o número desejado.
Exemplo:
Grupo → 05
Dezena → 23
Centena → 123
Milhar → 4321

0️⃣ Voltar"""

MSG_CONFIRMACAO = """Confira os dados da sua rifa:

Modalidade: *{modalidade}*
Número: *{numero}*
Valor da rifa: R$ {preco}
Ganho fixo: R$ {premio}
Extração: 18h

Digite:
1️⃣ para CONFIRMAR
0️⃣ para CANCELAR"""

MSG_PIX = """💳 *Pagamento via Pix*

Valor: R$ {valor}

Escaneie o QR Code abaixo ou copie o código Pix.

0️⃣ Voltar ao Menu"""

MSG_SUPORTE = """🆘 *Suporte*

Digite sua dúvida ou aguarde que um atendente irá responder.
(Link para WhatsApp do suporte ou aguarde atendimento)

0️⃣ Voltar ao Menu"""

MSG_SEM_RIFAS = "🚫 Não há rifas ativas no momento para esta modalidade."
MSG_ERRO_GENERICO = "Desculpe, não entendi. Digite 0 para voltar ao Menu."

# --- Helpers ---

def get_or_create_session(db: Session, phone: str):
    session = db.query(WhatsappSession).filter(WhatsappSession.phone_number == phone).first()
    if not session:
        session = WhatsappSession(phone_number=phone, step="START")
        db.add(session)
        db.commit()
        db.refresh(session)
    return session

def update_session(db: Session, session: WhatsappSession, step: str, data: dict = None):
    session.step = step
    if data is not None:
        # Merge existing data with new data
        current_data = session.temp_data or {}
        current_data.update(data)
        session.temp_data = current_data
    db.commit()
    db.refresh(session)

def get_user_by_phone(db: Session, phone: str):
    # Try exact match first
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        # Try without +
        clean = phone.replace("+", "")
        user = db.query(User).filter(User.phone == clean).first()
    return user

def create_user_from_whatsapp(db: Session, phone: str, name: str):
    # Generate random password
    chars = string.ascii_letters + string.digits + "!@#$%"
    pwd = ''.join(secrets.choice(chars) for i in range(12))
    
    # Generate fake email
    clean_phone = "".join(filter(str.isdigit, phone))
    email = f"{clean_phone}@whatsapp.user"
    
    # Get default tenant
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).first()
    if not tenant:
        return None

    new_user = User(
        email=email,
        password_hash=get_password_hash(pwd),
        name=name,
        phone=phone,
        role="player",
        is_active=True,
        whatsapp_opt_in=True,
        tenant_id=tenant.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- Handlers ---

async def process_message_task(sender: str, incoming_msg: str):
    db = SessionLocal()
    try:
        # Get or Create Session
        session = get_or_create_session(db, sender)
        
        await process_message_logic(db, session, incoming_msg, sender)
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {e}")
    finally:
        db.close()

async def process_message_logic(db: Session, session: WhatsappSession, incoming_msg: str, sender: str):
    step = session.step
    incoming_msg = incoming_msg.strip()
    
    # Global Cancel
    if incoming_msg == "0" and step != "START" and step != "CADASTRO_NOME":
        update_session(db, session, "MENU", {})
        whatsapp_service.send_text_message(sender, MSG_BOAS_VINDAS)
        return

    # --- START / MENU ---
    if step == "START" or step == "MENU":
        # Check user existence first
        user = get_user_by_phone(db, sender)
        if not user:
            update_session(db, session, "CADASTRO_NOME")
            whatsapp_service.send_text_message(sender, MSG_CADASTRO)
            return

        if step == "START":
            # Just show menu
            update_session(db, session, "MENU")
            whatsapp_service.send_text_message(sender, MSG_BOAS_VINDAS)
            return

        # Menu Options
        if incoming_msg == "1": # Jogar
            update_session(db, session, "ESCOLHA_MODALIDADE")
            whatsapp_service.send_text_message(sender, MSG_MODALIDADE)
        
        elif incoming_msg == "2": # Ver Rifas
            rifas = db.query(Rifa).filter(Rifa.status == RifaStatus.ATIVA).all()
            if not rifas:
                whatsapp_service.send_text_message(sender, "Nenhuma rifa ativa no momento.")
                whatsapp_service.send_text_message(sender, MSG_BOAS_VINDAS)
            else:
                msg = "🎟️ *Rifas Ativas:*\n\n"
                for r in rifas:
                    msg += f"- {r.titulo} (R$ {r.preco_numero})\n"
                whatsapp_service.send_text_message(sender, msg)
                whatsapp_service.send_text_message(sender, "\nDigite 0 para voltar ao menu.")
        
        elif incoming_msg == "3": # Histórico
            # Fetch history
            user = get_user_by_phone(db, sender)
            numeros = db.query(RifaNumero).filter(
                RifaNumero.user_id == user.id,
                RifaNumero.status == NumeroStatus.PAGO
            ).order_by(RifaNumero.updated_at.desc()).limit(10).all()
            
            if not numeros:
                whatsapp_service.send_text_message(sender, "📜 Você ainda não tem rifas pagas.")
            else:
                msg = "📜 *Seu Histórico (Últimas 10):*\n\n"
                for n in numeros:
                    rifa = db.query(Rifa).get(n.rifa_id)
                    rifa_titulo = rifa.titulo if rifa else "Rifa Removida"
                    msg += f"📅 {n.updated_at.strftime('%d/%m')} - {rifa_titulo} - Nº *{n.numero}*\n"
                whatsapp_service.send_text_message(sender, msg)
            whatsapp_service.send_text_message(sender, "\nDigite 0 para voltar ao menu.")

        elif incoming_msg == "4": # Suporte
            whatsapp_service.send_text_message(sender, MSG_SUPORTE)
        
        else:
            whatsapp_service.send_text_message(sender, "Opção inválida.\n\n" + MSG_BOAS_VINDAS)

    # --- CADASTRO ---
    elif step == "CADASTRO_NOME":
        name = incoming_msg
        if len(name) < 3:
            whatsapp_service.send_text_message(sender, "Nome muito curto. Por favor, digite seu nome completo.")
            return
        
        create_user_from_whatsapp(db, sender, name)
        update_session(db, session, "MENU")
        whatsapp_service.send_text_message(sender, f"Cadastro realizado com sucesso, {name}!\n\n" + MSG_BOAS_VINDAS)

    # --- JOGAR ---
    elif step == "ESCOLHA_MODALIDADE":
        # Map 1-4 to RifaTipo
        modalidade_map = {
            "1": "grupo", 
            "2": "dezena",
            "3": "centena",
            "4": "milhar"
        }
        
        tipo_str = modalidade_map.get(incoming_msg)
        if not tipo_str:
            whatsapp_service.send_text_message(sender, "Opção inválida.\n" + MSG_MODALIDADE)
            return

        # Find ACTIVE rifa for this type
        rifas = db.query(Rifa).filter(Rifa.status == RifaStatus.ATIVA).all()
        selected_rifa = None
        for r in rifas:
            r_tipo = r.tipo_rifa.value if hasattr(r.tipo_rifa, 'value') else str(r.tipo_rifa)
            if r_tipo.lower() == tipo_str:
                selected_rifa = r
                break
        
        if not selected_rifa:
            whatsapp_service.send_text_message(sender, f"🚫 Não há rifas de {tipo_str} ativas no momento.\n\nDigite 0 para voltar.")
            return

        update_session(db, session, "JOGAR_NUMERO", {
            "rifa_id": str(selected_rifa.id),
            "modalidade": tipo_str,
            "preco": str(selected_rifa.preco_numero),
            "premio": str(selected_rifa.valor_premio or "A definir")
        })
        whatsapp_service.send_text_message(sender, MSG_DIGITE_NUMERO)

    elif step == "JOGAR_NUMERO":
        numero = incoming_msg
        rifa_id = session.temp_data.get("rifa_id")
        
        # Validate Number
        rifa_num = db.query(RifaNumero).filter(
            RifaNumero.rifa_id == rifa_id,
            RifaNumero.numero == numero
        ).first()
        
        if not rifa_num:
            whatsapp_service.send_text_message(sender, "Número inválido ou indisponível. Tente outro.")
            return
            
        if rifa_num.status != NumeroStatus.LIVRE and rifa_num.status != NumeroStatus.EXPIRADO:
             whatsapp_service.send_text_message(sender, "Este número já está reservado ou pago. Escolha outro.")
             return

        # Update session
        update_session(db, session, "JOGAR_CONFIRMACAO", {"numero": numero, "numero_id": str(rifa_num.id)})
        
        # Show Confirmation
        data = session.temp_data
        msg = MSG_CONFIRMACAO.format(
            modalidade=data.get("modalidade"),
            numero=numero,
            preco=data.get("preco"),
            premio=data.get("premio")
        )
        whatsapp_service.send_text_message(sender, msg)

    elif step == "JOGAR_CONFIRMACAO":
        if incoming_msg == "1":
            # Confirm Reservation
            numero_id = session.temp_data.get("numero_id")
            user = get_user_by_phone(db, sender)
            
            # Double check lock
            rifa_num = db.query(RifaNumero).get(numero_id)
            if rifa_num.status != NumeroStatus.LIVRE and rifa_num.status != NumeroStatus.EXPIRADO:
                 whatsapp_service.send_text_message(sender, "Poxa, alguém acabou de pegar esse número! Tente outro.\n\n" + MSG_DIGITE_NUMERO)
                 update_session(db, session, "JOGAR_NUMERO")
                 return
            
            # Reserve
            rifa_num.status = NumeroStatus.RESERVADO
            rifa_num.user_id = user.id
            rifa_num.reserved_until = datetime.now() + timedelta(minutes=15)
            rifa_num.payment_id = str(uuid.uuid4())
            
            db.commit()
            
            # Mock Pix
            pix_code = f"00020126580014BR.GOV.BCB.PIX...{rifa_num.numero}"
            
            update_session(db, session, "AGUARDANDO_PAGAMENTO")
            
            msg_pix = MSG_PIX.format(valor=session.temp_data.get("preco"))
            whatsapp_service.send_text_message(sender, msg_pix)
            whatsapp_service.send_text_message(sender, pix_code)
            whatsapp_service.send_text_message(sender, "⏳ Aguardando confirmação do pagamento... (O sistema identificará automaticamente)")
            
        elif incoming_msg == "0":
            update_session(db, session, "MENU")
            whatsapp_service.send_text_message(sender, "Cancelado. \n\n" + MSG_BOAS_VINDAS)
        else:
            whatsapp_service.send_text_message(sender, "Opção inválida. Digite 1 para Confirmar ou 0 para Cancelar.")


@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    form_data = await request.form()
    sender = form_data.get("From") 
    body = form_data.get("Body")
    
    if not sender or not body:
        return {"status": "ignored"}
    
    logger.info(f"WhatsApp Incoming from {sender}: {body}")
    
    # Process in background
    background_tasks.add_task(process_message_task, sender, body)
    
    from fastapi.responses import Response
    return Response(content="<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response></Response>", media_type="application/xml")