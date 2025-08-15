import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List

class PaymentSystem:
    def __init__(self, access_token: str):
        self.access_token = access_token
        # Por enquanto, PIX manual até configurar Mercado Pago
    
    def create_pix_payment(self, amount: float, user_id: int, description: str = "Recarga de saldo") -> Dict:
        """Cria um pagamento PIX (modo manual por enquanto)"""
        try:
            # Gera ID único para o pagamento
            payment_id = str(uuid.uuid4())[:8].upper()
            
            # Por enquanto retorna dados simulados para PIX manual
            return {
                "success": True,
                "payment_id": payment_id,
                "mp_payment_id": f"mock_{payment_id}",
                "pix_code": f"PIX_CODE_MANUAL_{payment_id}",
                "amount": amount,
                "status": "pending_manual",
                "expiration_date": datetime.now() + timedelta(minutes=30),
                "expires_in": "30 minutos"
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}"
            }
    
    def check_payment_status(self, mp_payment_id: str) -> Dict:
        """Verifica o status de um pagamento (modo manual)"""
        try:
            # Por enquanto retorna status pendente para aprovação manual
            return {
                "success": True,
                "status": "pending_manual",
                "status_detail": "Aguardando aprovação manual",
                "amount": 0,
                "date_approved": None,
                "payment_id": mp_payment_id
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao verificar pagamento: {str(e)}"
            }
    
    def generate_qr_code_image(self, pix_code: str) -> bytes:
        """Gera imagem do QR Code PIX (simplificado)"""
        try:
            # Por enquanto retorna None - implementar quando necessário
            return None
            
        except Exception as e:
            print(f"Erro ao gerar QR Code: {e}")
            return None
    
    def process_webhook(self, webhook_data: Dict) -> Dict:
        """Processa webhook do Mercado Pago"""
        try:
            # Extrai dados do webhook
            resource_id = webhook_data.get("data", {}).get("id")
            
            if not resource_id:
                return {"success": False, "error": "ID do recurso não encontrado"}
            
            # Busca informações do pagamento
            payment_status = self.check_payment_status(resource_id)
            
            if payment_status["success"] and payment_status["status"] == "approved":
                return {
                    "success": True,
                    "payment_approved": True,
                    "payment_id": resource_id,
                    "amount": payment_status["amount"]
                }
            
            return {
                "success": True,
                "payment_approved": False,
                "status": payment_status.get("status", "unknown")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao processar webhook: {str(e)}"
            }

class ManualPaymentSystem:
    """Sistema de pagamento manual para quando o PIX automático não estiver disponível"""
    
    def __init__(self):
        self.pending_payments = {}
    
    def create_manual_payment(self, amount: float, user_id: int) -> Dict:
        """Cria um pagamento manual"""
        payment_id = str(uuid.uuid4())[:8].upper()
        
        payment_data = {
            "payment_id": payment_id,
            "user_id": user_id,
            "amount": amount,
            "status": "pending",
            "created_date": datetime.now(),
            "expiration_date": datetime.now() + timedelta(minutes=30)
        }
        
        self.pending_payments[payment_id] = payment_data
        
        return {
            "success": True,
            "payment_id": payment_id,
            "amount": amount,
            "status": "pending_manual_approval",
            "message": "Pagamento criado. Aguardando aprovação manual do administrador."
        }
    
    def approve_manual_payment(self, payment_id: str) -> Dict:
        """Aprova um pagamento manual"""
        if payment_id in self.pending_payments:
            self.pending_payments[payment_id]["status"] = "approved"
            self.pending_payments[payment_id]["approved_date"] = datetime.now()
            
            return {
                "success": True,
                "payment_id": payment_id,
                "amount": self.pending_payments[payment_id]["amount"],
                "user_id": self.pending_payments[payment_id]["user_id"]
            }
        
        return {
            "success": False,
            "error": "Pagamento não encontrado"
        }
    
    def get_pending_payments(self) -> List[Dict]:
        """Retorna lista de pagamentos pendentes"""
        return [payment for payment in self.pending_payments.values() 
                if payment["status"] == "pending"]