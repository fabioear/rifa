import { errorsPT } from '../i18n/errors.pt-BR';

export function mapApiError(error: any): string {
  // Se for uma string direta, tenta mapear ou retorna ela mesma
  if (typeof error === 'string') {
      return mapMessage(error);
  }

  // Axios error structure
  const responseData = error?.response?.data;
  
  // Tenta pegar o código ou detalhe do erro
  const code = responseData?.code;
  const detail = responseData?.detail || error?.message;

  if (code) {
    switch (code) {
      case "INVALID_CREDENTIALS":
        return errorsPT.invalidCredentials;
      case "USER_NOT_FOUND":
        return errorsPT.userNotFound;
      case "USER_BLOCKED":
      case "INACTIVE_USER":
        return errorsPT.inactiveUser;
      case "TOKEN_EXPIRED":
        return errorsPT.tokenExpired;
      case "USER_ALREADY_EXISTS":
        return errorsPT.userExists;
      default:
        // Se tiver um código desconhecido, tenta mapear a mensagem ou retorna genérico
        return mapMessage(detail) || errorsPT.unexpected;
    }
  }

  return mapMessage(detail) || errorsPT.unexpected;
}

function mapMessage(message: string): string {
    if (!message) return '';
    
    // Mapeamento de mensagens comuns do backend (FastAPI/Pydantic)
    if (message.includes("Incorrect email or password")) return errorsPT.invalidCredentials;
    if (message.includes("Inactive user")) return errorsPT.inactiveUser;
    if (message.includes("The user with this username already exists")) return errorsPT.userExists;
    if (message.includes("Network Error")) return errorsPT.networkError;
    if (message.includes("401")) return errorsPT.tokenExpired;
    if (message.includes("422")) return errorsPT.invalidData;
    if (message.includes("403")) return errorsPT.accessDenied;
    
    return message; // Retorna a mensagem original se não houver mapeamento específico (fallback)
}
