# Starcraft 2 - SMA

## Requisitos

* Python 3.7+
* StarCraft 2

## Instalação

Instale a biblioteca para operar no StarCraft 2.

```
pip3 install --upgrade burnysc2
```

## Sobre o projeto

### Mapa

O mapa utilizado é o [AcropolisLE](https://liquipedia.net/starcraft2/Acropolis_LE) devido a sua simetria. Esse mapa pode ser baixado [aqui](https://wiki.sc2ai.net/Ladder_Maps).

### Construção do agente

As percepções e ações dos agentes são fatores cruciais que devem ser considerados como: 

**Percepções**

* Identificar recurso 
* Identificar inimigos 
* Visualizar ambiente 

**Ações** 

* Coletar recurso 
* Fugir
* Atacar 
* Comunicar-se 
* Explorar mapa

Para que tais percepções e ações possam acontecer algumas variáveis devem ser consideradas para a tomada de decisão que são:

* Quantidade de Recursos 
* Construções 
* Tipos de construções 
* Quantidade de agentes por tipo 
* Estado dos agentes: em treinamento, parado, atacando 
* Alocação por unidade 
* Estado: sob ataque, atacando, parado, evoluindo… 

Outro ponto que deve ser considerado é o quão ciente os agentes estão a presença de inimigos, ambientes e quais informações são possíveis trocar, segue exemplo:
 
**Militar**

* Presença de Inimigo 
* Necessidade de Cura 
* Iniciar Ataque 
* Interromper Ataque 
* Fugir
  
**Construtor / Coletor / Scout** 

* Término de construções de unidades (build) 
* Localização de recurso 
* Limitação de recursos
