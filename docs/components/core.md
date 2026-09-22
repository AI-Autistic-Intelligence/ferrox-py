# Core Component (Inversion of Control)

Il modulo Core di `ferrox-py` è la spina dorsale del framework e gestisce l'intero ciclo di vita dell'applicazione tramite un container di Inversion of Control (IoC).

## 1. Container IoC e Dependency Injection
A differenza di framework web leggeri (come FastAPI o Flask) dove lo stato viene passato come parametri o variabili globali, `ferrox-py` impone l'uso del `Container`.

### Architettura
- **`ferrox_py.core.container.Container`**: Un dizionario thread-safe che risolve le dipendenze in base al tipo o al nome della stringa.
- **Supporto Transient e Singleton**: Attualmente, l'IoC risolve componenti Singleton.
- **Risoluzione Lazy**: I componenti vengono istanziati solo quando richiesti per evitare overhead al boot.

### Esempio di utilizzo:
```python
from ferrox_py.core.container import Container

class Database:
    def execute(self):
        return "Query Executed"

class UserService:
    def __init__(self, db: Database):
        self.db = db

# Inizializzazione
container = Container()
container.register("db", Database())
container.register("user_service", UserService(db=container.resolve("db")))

# Risoluzione
service = container.resolve("user_service")
print(service.db.execute())
```

## 2. L'Applicazione (FerroxApp)
La classe `FerroxApp` accetta il container configurato ed espone l'entrypoint globale. 
Gestisce:
1. Lifecycle Hooks (Start, Stop, Crash)
2. Inizializzazione della 7-Layer Request Pipeline
3. Aggancio dei trasporti (HTTP, Code, WebSockets)

## 3. Provider e Moduli
Ispirato a NestJS, `ferrox-py` incapsula feature specifiche all'interno di Moduli (es. `AuthModule`), i quali definiscono l'array dei `Provider` (le classi) da registrare automaticamente nel Container. Questo favorisce la manutenibilità e il disaccoppiamento tra dominio e infrastruttura.
