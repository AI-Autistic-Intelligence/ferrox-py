# CQRS, Events e Sagas Component

In architetture Enterprise e Microservizi complessi, i Controller non dovrebbero chiamare direttamente i Repository, ma dovrebbero lanciare Comandi o Query. `ferrox-py` fornisce pattern integrati per la segregazione.

## 1. CommandBus & QueryBus (CQRS)
Il pattern Command Query Responsibility Segregation disaccoppia chi esegue la mutazione di stato (Command) da chi legge i dati (Query).

```python
from ferrox_py.cqrs.bus import CommandBus

# 1. Definizione
class CreateOrderCommand:
    def __init__(self, item_id: str):
        self.item_id = item_id

# 2. Registrazione e Dispatch
bus = CommandBus()
# Registra un handler che sa come processare CreateOrderCommand
bus.register_handler(CreateOrderCommand, order_service.create_order)

# L'API invia il comando
result = bus.dispatch(CreateOrderCommand(item_id="12345"))
```

## 2. Event Dispatcher
Architettura Event-Driven. Quando si completa una transazione (es. Pagamento), viene scaturito un Evento. Chiunque sia sottoscritto (`Subscriber`) reagisce asincronamente. In `ferrox-py` il Bus è in memoria, ma estendibile su Redis Pub/Sub o RabbitMQ.

## 3. Sagas (Transazioni Distribuite)
Le Sagas sono una sequenza di transazioni locali. Se una fallisce (es. pagamento fallito, ma ordine creato), il motore esegue i passi compensativi per annullare le transazioni locali precedenti.

```python
# L'orchestratore sa come annullare (rollback) un comando.
# Ideale per scenari serverless o microservizi su database diversi.
```
