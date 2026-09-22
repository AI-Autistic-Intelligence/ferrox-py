# ⚡ Ferrox-Py (Core Framework)

<p align="center">
  <b>Un framework Python 3.11+ per il Server-Side Enterprise</b><br/>
  <i>Ispirato alla robustezza di Rust-Ferrox, porta l'Inversion of Control, la Modularità e l'Architettura a Cipolla nel mondo Python.</i>
</p>

---

## 1. Cosa fa questo pacchetto? (Overview)
`ferrox-py` è il cuore dell'ecosistema Ferrox per Python. Fornisce il container di Inversion of Control (IoC), il sistema di Dependency Injection (DI) e la struttura fondamentale per sviluppare backend robusti, scalabili e disaccoppiati in Python. Non è solo un framework web, ma un gestore dell'intero ciclo di vita dell'applicazione, supportando contemporaneamente API REST, GraphQL, background jobs e code di eventi.

## 2. Perché usare Ferrox-Py? (Filosofia)
Nel moderno sviluppo backend in Python (spesso dominato da script monolitici o framework troppo permissivi), le decisioni architetturali tendono a frammentarsi. Ferrox-Py nasce per risolvere il problema del debito tecnico nei progetti complessi, imponendo:
- **Disaccoppiamento netto** tra logica di dominio (Business Layer) e protocollo di trasporto (HTTP, gRPC, Code).
- **Gestione sicura dello stato** tramite container IoC centralizzati.
- **Validazione rigorosa** all'ingresso (tramite Pydantic).

## 3. A chi si rivolge?
È pensato per **Data Platform**, **SaaS Enterprise** e **Architetture a Microservizi** dove la sicurezza, la prevedibilità del codice e la manutenibilità a lungo termine sono critiche. Se hai bisogno di un sistema che scali assieme al tuo team senza diventare un groviglio di codice, Ferrox-Py è la scelta ideale.

## 4. Come funziona? (Architettura)
Ferrox-Py adotta fedelmente la **7-Layer Onion Request Pipeline** dell'ecosistema Ferrox originale:
1. **Security & Headers**: Intercettazione iniziale e sanificazione.
2. **Defesa Attiva & Rate Limiting**: Protezione preventiva contro gli abusi.
3. **Auth Guards**: Estrazione e validazione dei token (JWT/PASETO).
4. **RBAC & ZK Proofs**: Controllo rigoroso degli accessi basato sui ruoli.
5. **Validation Pipe**: Controllo formale del payload DTO (Data Transfer Object).
6. **Controller Layer**: Traduzione del trasporto in linguaggio di dominio.
7. **Business Service / CQRS**: Esecuzione della logica di dominio e persistenza.

## 5. Come si installa?
Assicurati di utilizzare Python 3.11+.

```bash
# Esempio di installazione in locale (sviluppo)
pip install -e .
```

Il progetto espone anche la CLI `ferrox` per utility e task di base.

## 6. Come si usa? (Quickstart)

```python
from ferrox_py.core.app import FerroxApp
from ferrox_py.core.container import Container

def main():
    # Inizializza il container IoC
    container = Container()
    
    # Registra i tuoi servizi e i controller
    # container.register("mio_servizio", MioServizio)
    
    # Costruisce e avvia l'applicazione
    app = FerroxApp(container)
    app.start()

if __name__ == "__main__":
    main()
```

## 7. L'Ecosistema Ferrox-Py
Il Core è progettato per essere esteso da pacchetti specializzati:
- 🛠️ [ferrox-py-utils](../ferrox-py-utils) - Strumenti ETL, pipeline dati e connettori (S3, CSV).
- 🔒 [ferrox-py-auth](../ferrox-py-auth) - Gestione IAM, SSO, RBAC e compliance GDPR.
- 💳 [ferrox-py-commerce](../ferrox-py-commerce) - Integrazioni Stripe/PayPal, Webhooks e idempoteza.
