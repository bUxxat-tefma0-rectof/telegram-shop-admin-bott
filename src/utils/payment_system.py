import mercadopago
import uuid
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from PIL import Image

class PaymentSystem:
    def __init__(self, access_token: str):
        self.mp = mercadopago.SDK(access_token)
        self.access_token = access_token
    
    def create_pix_payment(self, amount: float, user_id: int, description: str = "Recarga de saldo") -> Dict:
        """Cria um pagamento PIX"""
        try:
            # Gera ID único para o pagamento
            payment_id = str(uuid.uuid4())[:8].upper()
            
            # Dados do pagamento
            payment_data = {
                "transaction_amount": float(amount),
                "description": description,
                "payment_method_id": "pix",
                "external_reference": f"user_{user_id}_payment_{payment_id}",
                "payer": {
                    "email": f"user{user_id}@exemplo.com"
                },
                "notification_url": "https://seu-webhook-url.com/webhook"  # Configure seu webhook
            }
            
            # Cria o pagamento
            payment_response = self.mp.payment().create(payment_data)
            
            if payment_response["status"] == 201:
                payment_info = payment_response["response"]
                
                # Extrai informações do PIX
                pix_data = payment_info.get("point_of_interaction", {}).get("transaction_data", {})
                qr_code = pix_data.get("qr_code", "")
                qr_code_base64 = pix_data.get("qr_code_base64", "")
                
                # Calcula data de expiração (30 minutos)
                expiration_date = datetime.now() + timedelta(minutes=30)
                
                return {
                    "success": True,
                    "payment_id": payment_id,
                    "mp_payment_id": payment_info["id"],
                    "pix_code": qr_code,
                    "qr_code_base64": qr_code_base64,
                    "amount": amount,
                    "status": payment_info["status"],
                    "expiration_date": expiration_date,
                    "expires_in": "30 minutos"
                }
            else:
                return {
                    "success": False,
                    "error": "Erro ao criar pagamento",
                    "details": payment_response
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}"
            }
    
    def check_payment_status(self, mp_payment_id: str) -> Dict:
        """Verifica o status de um pagamento"""
        try:
            payment_response = self.mp.payment().get(mp_payment_id)
            
            if payment_response["status"] == 200:
                payment_info = payment_response["response"]
                
                return {
                    "success": True,
                    "status": payment_info["status"],
                    "status_detail": payment_info.get("status_detail", ""),
                    "amount": payment_info["transaction_amount"],
                    "date_approved": payment_info.get("date_approved"),
                    "payment_id": payment_info["id"]
                }
            else:
                return {
                    "success": False,
                    "error": "Pagamento não encontrado"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao verificar pagamento: {str(e)}"
            }
    
    def generate_qr_code_image(self, pix_code: str) -> bytes:
        """Gera imagem do QR Code PIX"""
        try:
            # Cria QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(pix_code)
            qr.make(fit=True)
            
            # Cria imagem
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Converte para bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
            
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