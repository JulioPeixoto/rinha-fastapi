import json
import logging
from typing import Optional

from aio_pika import DeliveryMode, Message, connect
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue

logger = logging.getLogger(__name__)


class RabbitMQService:    
    def __init__(self):
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None 
        self.payment_queue: Optional[AbstractQueue] = None
        self.connection_url = "amqp://user:password@rabbitmq:5672/"
        
    async def connect(self):
        logger.info("Conectando ao RabbitMQ...")
        self.connection = await connect(self.connection_url)
        self.channel = await self.connection.channel()
        
        # 2. Configurar para processar 1 mensagem por vez
        # evita sobrecarga
        await self.channel.set_qos(prefetch_count=1)
        
        # 3. Criar fila principal para pagamentos
        # durable=True significa que a fila sobrevive se o RabbitMQ reiniciar
        self.payment_queue = await self.channel.declare_queue(
            name="payment.processing",  # Nome da fila
            durable=True,              # Persiste mesmo se RabbitMQ reiniciar
        )
        
        logger.info("RabbitMQ conectado e fila criada com sucesso!")

    async def publish_payment(self, payment_data: dict):
        if not self.connection or self.connection.is_closed:
            await self.connect()
        
        message_body = json.dumps(payment_data).encode()
        
        # Criar mensagem persistente
        message = Message(
            body=message_body,
            delivery_mode=DeliveryMode.PERSISTENT,  # Salva no disco
            headers={
                "correlation_id": payment_data.get("correlationId"),
                "created_at": payment_data.get("requestedAt"),
            },
        )
        
        # Publicar na fila
        if not self.channel:
            raise Exception("Canal RabbitMQ não está disponível")
            
        await self.channel.default_exchange.publish(
            message=message,
            routing_key="payment.processing",  # Nome da fila de destino
        )
        
        logger.info(f"Pagamento {payment_data['correlationId']} adicionado à fila")

    async def consume_payments(self, callback_function):
        if not self.connection or self.connection.is_closed:
            await self.connect()
        
        if not self.payment_queue:
            raise Exception("Fila de pagamentos não foi criada")
        
        # Configurar consumidor
        # no_ack=False significa que precisamos confirmar manualmente 
        # quando processamos uma mensagem (evita perda)
        await self.payment_queue.consume(
            callback=callback_function,
            no_ack=False  # Exige confirmação manual (ack/reject)
        )
        
        logger.info("Worker iniciado - aguardando mensagens da fila...")

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Conexão RabbitMQ fechada")
